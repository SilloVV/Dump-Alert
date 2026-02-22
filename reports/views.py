"""
Vues de l'application Reports.

Une VUE = une fonction (ou classe) qui :
1. Reçoit une requête HTTP (GET, POST, etc.)
2. Traite les données (lecture/écriture BDD, logique métier)
3. Retourne une réponse HTTP (HTML, JSON, redirection)

C'est le "C" du pattern MVC (Model-View-Controller).
En Django, on parle de MTV : Model-Template-View.
"""

from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point

from .models import Report
from .forms import ReportForm

# Limites géographiques de la zone de Beauvais
_LAT_MIN, _LAT_MAX = 49.35, 49.55
_LON_MIN, _LON_MAX = 1.80, 2.30


def _parse_coords(lat_str, lon_str):
    """
    Valide et convertit les coordonnées brutes du formulaire.
    Retourne (lat_f, lon_f) ou lève ValueError avec un message lisible.
    """
    if not lat_str or not lon_str:
        raise ValueError("Veuillez choisir une localisation sur la carte")
    try:
        lat_f, lon_f = float(lat_str), float(lon_str)
    except ValueError:
        raise ValueError("Erreur de coordonnées : réessayez")
    if not (_LAT_MIN <= lat_f <= _LAT_MAX and _LON_MIN <= lon_f <= _LON_MAX):
        raise ValueError("Position hors zone de Beauvais")
    return lat_f, lon_f


@staff_member_required  # Accessible uniquement aux utilisateurs staff (admin et certaines permissions)
def report_list(request):
    """
    Affiche la liste de tous les signalements dans un tableau.

    Accessible uniquement aux admins (is_staff=True).
    URL : /reports/
    """
    # Récupérer tous les signalements, triés par date (plus récents en premier)
    reports = Report.objects.select_related("cluster").order_by("-created_at")

    # Filtrage optionnel par statut (via paramètre GET)
    status_filter = request.GET.get("status")
    if status_filter:
        reports = reports.filter(status=status_filter)

    # Filtrage optionnel par catégorie de déchets
    waste_filter = request.GET.get("type")
    if waste_filter:
        reports = reports.filter(type=waste_filter)

    # Contexte envoyé au template
    context = {
        "reports": reports,
        "status_choices": Report.Status.choices,
        "waste_choices": Report.WasteType.choices,
        "current_status": status_filter,
        "current_waste": waste_filter,
    }

    return render(request, "reports/report_list.html", context)


@login_required  # Accessible uniquement aux utilisateurs connectés
def create_report(request):
    """
        Formulaire de signalement d'un dépôt sauvage.
    j
        Accessible aux utilisateurs connectés. Le statut est toujours 'pending' à la création.
        La localisation est capturée via deux champs cachés (lat, lon) remplis
        par le clic sur la carte Leaflet dans le template.

        URL : /signaler/
    """
    form = ReportForm()
    error = None

    if request.method == "POST":
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                lat_f, lon_f = _parse_coords(
                    request.POST.get("lat", "").strip(),
                    request.POST.get("lon", "").strip(),
                )
            except ValueError as e:
                error = str(e)
            else:
                report = form.save(commit=False)
                report.location = Point(lon_f, lat_f, srid=4326)
                report.save()  # déclenche le clustering via signals.py
                return redirect("reports:success")

    return render(request, "reports/report_form.html", {"form": form, "error": error})


def report_success(request):
    """Page de confirmation après soumission d'un signalement. URL : /merci/"""
    return render(request, "reports/report_success.html")
