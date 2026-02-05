"""
Routes URL de l'application Reports.

Ce fichier définit les URLs spécifiques à l'app reports.
Il sera inclus dans le fichier urls.py principal du projet.
"""

from django.urls import path
from . import views

app_name = 'reports'  # Namespace pour éviter les conflits de noms

urlpatterns = [
    # Liste des signalements (tableau)
    # Accessible à : /reports/
    path('', views.report_list, name='list'),
]
