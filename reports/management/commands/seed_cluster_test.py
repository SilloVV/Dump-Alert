"""
Commande de test : insère 10 signalements groupés à moins de 10m
pour valider le système de clustering automatique.

Usage :
    python manage.py seed_cluster_test
    python manage.py seed_cluster_test --lat 49.431 --lon 2.082
    python manage.py seed_cluster_test --delete
"""

import struct
import zlib

from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from reports.models import Report


# ── Image PNG 1×1 pixel rouge (valide, ~70 octets) ─────────────────────────
def _make_tiny_png():
    """Génère un PNG 1×1 pixel valide en mémoire, sans dépendance externe."""

    def chunk(name, data):
        c = struct.pack(">I", len(data)) + name + data
        return c + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    raw = b"\x00\xff\x00\x00"  # filtre 0 + pixel RGB rouge
    idat = chunk(b"IDAT", zlib.compress(raw))
    iend = chunk(b"IEND", b"")
    return signature + ihdr + idat + iend


# ── Décalages en degrés autour d'un point central ──────────────────────────
# 1° lat ≈ 111 320 m | 1° lon ≈ 73 050 m à 49°N
# 9 m ≈ 0.000081° lat, 0.000123° lon  →  tous les points restent dans ≤10m
OFFSETS = [
    (0.000000, 0.000000),  # point central
    (0.000030, 0.000050),
    (-0.000025, 0.000040),
    (0.000050, -0.000030),
    (-0.000040, -0.000050),
    (0.000060, 0.000020),
    (-0.000010, 0.000070),
    (0.000045, -0.000060),
    (-0.000055, 0.000010),
    (0.000020, -0.000070),
]

WASTE_TYPE_CHOICES = ["green", "household", "bulky", "building", "chemical", "asbestos"]


class Command(BaseCommand):
    help = "Insère 10 signalements de test groupés à ≤10m pour tester le clustering."

    def add_arguments(self, parser):
        parser.add_argument(
            "--lat",
            type=float,
            default=49.43060,
            help="Latitude du point central (défaut: Beauvais)",
        )
        parser.add_argument(
            "--lon",
            type=float,
            default=2.08186,
            help="Longitude du point central (défaut: Beauvais)",
        )
        parser.add_argument(
            "--waste-type",
            type=str,
            default="household",
            choices=WASTE_TYPE_CHOICES,
            help="Catégorie de déchets pour tous les signalements (défaut: household)",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Supprime tous les signalements de test existants",
        )

    def handle(self, *args, **options):
        if options["delete"]:
            deleted, _ = Report.objects.filter(
                description__startswith="[TEST-CLUSTER]"
            ).delete()
            self.stdout.write(
                self.style.WARNING(f"{deleted} signalement(s) de test supprimé(s).")
            )
            return

        center_lat = options["lat"]
        center_lon = options["lon"]
        waste_type = options["waste_type"]
        png_bytes = _make_tiny_png()

        self.stdout.write(
            f"Insertion de 10 signalements [{waste_type}] autour de "
            f"({center_lat}, {center_lon})…"
        )

        created = []
        for i, (dlat, dlon) in enumerate(OFFSETS):
            lat = center_lat + dlat
            lon = center_lon + dlon

            report = Report(
                description=f"[TEST-CLUSTER] Point #{i + 1} — dépôt {waste_type} simulé",
                type=waste_type,
                location=Point(lon, lat, srid=4326),
            )
            # Attacher une image PNG factice
            report.image.save(
                f"test_cluster_{i + 1}.png",
                ContentFile(png_bytes),
                save=False,
            )
            report.save()  # déclenche le signal → clustering automatique
            created.append(report)
            self.stdout.write(f"  #{i + 1}  lat={lat:.6f}  lon={lon:.6f}")

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ {len(created)} signalements créés. "
                f"Vérifie maintenant le cluster dans /admin ou /reports/."
            )
        )
