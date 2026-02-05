"""
Vues de l'application Reports.

Une VUE = une fonction (ou classe) qui :
1. Reçoit une requête HTTP (GET, POST, etc.)
2. Traite les données (lecture/écriture BDD, logique métier)
3. Retourne une réponse HTTP (HTML, JSON, redirection)

C'est le "C" du pattern MVC (Model-View-Controller).
En Django, on parle de MTV : Model-Template-View.
"""

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

from .models import Report


@staff_member_required  # Accessible uniquement aux utilisateurs staff (is_staff=True)
def report_list(request):
    """
    Affiche la liste de tous les signalements dans un tableau.

    Accessible uniquement aux admins (is_staff=True).
    URL : /reports/
    """
    # Récupérer tous les signalements, triés par date (plus récents en premier)
    reports = Report.objects.all().order_by('-created_at')

    # Filtrage optionnel par statut (via paramètre GET)
    status_filter = request.GET.get('status')
    if status_filter:
        reports = reports.filter(status=status_filter)

    # Filtrage optionnel par niveau de danger
    danger_filter = request.GET.get('danger')
    if danger_filter:
        reports = reports.filter(danger_level=danger_filter)

    # Contexte envoyé au template
    context = {
        'reports': reports,
        'status_choices': Report.Status.choices,
        'danger_choices': Report.DangerLevel.choices,
        'current_status': status_filter,
        'current_danger': danger_filter,
    }

    return render(request, 'reports/report_list.html', context)
