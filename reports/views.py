"""
Vues de l'application Reports.

Une VUE = une fonction (ou classe) qui :
1. Reçoit une requête HTTP (GET, POST, etc.)
2. Traite les données (lecture/écriture BDD, logique métier)
3. Retourne une réponse HTTP (HTML, JSON, redirection)

C'est le "C" du pattern MVC (Model-View-Controller).
En Django, on parle de MTV : Model-Template-View.

Exemple :
    def liste_signalements(request):
        reports = Report.objects.all()
        return render(request, 'reports/liste.html', {'reports': reports})
"""

from django.shortcuts import render


# Les vues seront créées ici
# TODO: Créer les vues pour :
# - Afficher la liste des signalements
# - Créer un nouveau signalement
# - Afficher la heatmap
