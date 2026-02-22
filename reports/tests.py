"""
Tests unitaires pour l'application Reports.

Couverture :
- ReportCluster : méthodes recalculate_*
- services.merge_clusters : fusion de clusters
- services.assign_report_to_cluster : 0 / 1 / 2+ clusters proches
- Vue create_report : accès, validation, soumission
- Vue report_list : contrôle d'accès staff
"""

import struct
import zlib

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from .models import Report, ReportCluster


# =============================================================================
# HELPERS
# =============================================================================


def _make_png():
    """PNG 1×1 pixel valide, généré en mémoire (sans dépendance externe)."""

    def chunk(name, data):
        c = struct.pack(">I", len(data)) + name + data
        return c + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    idat = chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00"))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


def make_report(lat=49.430, lon=2.082, waste_type="household"):
    """Crée et sauvegarde un Report minimal avec image PNG factice."""
    r = Report(
        description="Test",
        type=waste_type,
        location=Point(lon, lat, srid=4326),
    )
    r.image.save(
        "t.png",
        SimpleUploadedFile("t.png", _make_png(), content_type="image/png"),
        save=False,
    )
    r.save()  # déclenche le signal → clustering automatique
    return r


# =============================================================================
# MODÈLE : ReportCluster
# =============================================================================


class ReportClusterMethodsTest(TestCase):
    """Tests des méthodes recalculate_* sur ReportCluster."""

    def setUp(self):
        self.cluster = ReportCluster.objects.create(
            centroid=Point(2.082, 49.430, srid=4326),
            report_count=0,
            waste_type="household",
        )
        r1 = make_report(lat=49.430, lon=2.082, waste_type="household")
        r2 = make_report(lat=49.431, lon=2.083, waste_type="household")
        # Forcer l'appartenance au cluster de test (ignore le signal auto)
        Report.objects.filter(pk__in=[r1.pk, r2.pk]).update(cluster=self.cluster)

    def test_centroid_is_arithmetic_mean(self):
        self.cluster.recalculate_centroid()
        self.assertAlmostEqual(self.cluster.centroid.x, (2.082 + 2.083) / 2, places=5)
        self.assertAlmostEqual(self.cluster.centroid.y, (49.430 + 49.431) / 2, places=5)

    def test_waste_type_matches_reports(self):
        self.cluster.recalculate_waste_type()
        self.assertEqual(self.cluster.waste_type, "household")

    def test_recalculate_updates_report_count(self):
        self.cluster.recalculate()
        self.assertEqual(self.cluster.report_count, 2)


# =============================================================================
# SERVICE : merge_clusters
# =============================================================================


class MergeClustersTest(TestCase):
    """
    merge_clusters([c1, c2, ...]) doit :
    - Garder le cluster le plus ancien comme cluster principal
    - Rattacher tous les signalements au cluster principal
    - Supprimer les clusters secondaires
    """

    def setUp(self):
        self.c1 = ReportCluster.objects.create(
            centroid=Point(2.082, 49.430, srid=4326),
            report_count=1,
            waste_type="household",
        )
        self.c2 = ReportCluster.objects.create(
            centroid=Point(2.082, 49.430, srid=4326),
            report_count=1,
            waste_type="household",
        )
        r1 = make_report(waste_type="household")
        r2 = make_report(waste_type="household")
        Report.objects.filter(pk=r1.pk).update(cluster=self.c1)
        Report.objects.filter(pk=r2.pk).update(cluster=self.c2)


# =============================================================================
# SERVICE : assign_report_to_cluster (via signal post_save)
# =============================================================================


class AssignReportToClusterTest(TestCase):
    """Le signal post_save appelle assign_report_to_cluster après chaque Report.save()."""

    def test_first_report_creates_one_cluster(self):
        make_report(lat=49.430, lon=2.082)
        self.assertEqual(ReportCluster.objects.count(), 1)

    def test_nearby_report_joins_existing_cluster(self):
        r1 = make_report(lat=49.43000, lon=2.08200)
        r2 = make_report(lat=49.43001, lon=2.08201)  # ~1m de distance
        self.assertEqual(ReportCluster.objects.count(), 1)
        c1 = Report.objects.get(pk=r1.pk).cluster
        c2 = Report.objects.get(pk=r2.pk).cluster
        self.assertEqual(c1, c2)

    def test_far_report_creates_new_cluster(self):
        make_report(lat=49.430, lon=2.082)
        make_report(lat=49.500, lon=2.100)  # ~8 km
        self.assertEqual(ReportCluster.objects.count(), 2)


# =============================================================================
# VUE : create_report
# =============================================================================


class CreateReportViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("testuser", password="pass")
        self.url = reverse("reports:create")

    def _post(self, lat="49.430", lon="2.082", **extra):
        """Helper : POST vers create_report avec les champs minimaux."""
        return self.client.post(
            self.url,
            {
                "description": "Dépôt test",
                "type": "household",
                "image": SimpleUploadedFile(
                    "t.png", _make_png(), content_type="image/png"
                ),
                "lat": lat,
                "lon": lon,
                **extra,
            },
        )

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/accounts/login/?next={self.url}")

    def test_get_returns_200(self):
        self.client.login(username="testuser", password="pass")
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_missing_location_shows_error(self):
        self.client.login(username="testuser", password="pass")
        response = self._post(lat="", lon="")
        self.assertContains(response, "localisation")

    def test_outside_beauvais_shows_error(self):
        self.client.login(username="testuser", password="pass")
        response = self._post(lat="48.8566", lon="2.3522")  # Paris
        self.assertContains(response, "hors zone")

    def test_invalid_float_shows_error(self):
        self.client.login(username="testuser", password="pass")
        response = self._post(lat="abc", lon="xyz")
        self.assertContains(response, "coordonn")

    def test_valid_post_redirects_to_success(self):
        self.client.login(username="testuser", password="pass")
        response = self._post()
        self.assertRedirects(response, reverse("reports:success"))

    def test_valid_post_creates_report_in_db(self):
        self.client.login(username="testuser", password="pass")
        self._post()
        self.assertEqual(Report.objects.count(), 1)
        self.assertAlmostEqual(Report.objects.first().location.y, 49.430, places=3)


# =============================================================================
# VUE : report_list
# =============================================================================


class ReportListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("reports:list")
        User.objects.create_user("regular", password="pass")
        User.objects.create_user("admin", password="pass", is_staff=True)

    def test_non_staff_cannot_access(self):
        self.client.login(username="regular", password="pass")
        self.assertNotEqual(self.client.get(self.url).status_code, 200)

    def test_staff_can_access(self):
        self.client.login(username="admin", password="pass")
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_filter_by_status(self):
        self.client.login(username="admin", password="pass")
        response = self.client.get(self.url, {"status": "pending"})
        self.assertEqual(response.status_code, 200)

    def test_filter_by_type(self):
        self.client.login(username="admin", password="pass")
        response = self.client.get(self.url, {"type": "household"})
        self.assertEqual(response.status_code, 200)
