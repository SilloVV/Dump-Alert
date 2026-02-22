"""
Formulaire public de signalement de dépôt sauvage.

Ce formulaire est accessible sans connexion par n'importe quel citoyen.
Il ne contient PAS le champ 'status' (géré uniquement par l'admin)
ni le champ 'location' (capturé via un clic sur la carte Leaflet).
"""

from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["image", "description", "type"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Décrivez le dépôt : type de déchets, quantité estimée, accessibilité...",
                }
            ),
        }
        labels = {
            "image": "Photo du dépôt",
            "description": "Description",
            "type": "Catégorie de déchets",
        }
