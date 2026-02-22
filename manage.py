#!/usr/bin/env python
"""
Point d'entrée CLI de Django.
Usage : python manage.py <commande>

Commandes courantes :
    runserver       → Lancer le serveur de développement
    migrate         → Appliquer les migrations de base de données
    makemigrations  → Créer les migrations après modification des modèles
    createsuperuser → Créer un administrateur
    shell           → Console Python avec contexte Django
"""

import os
import sys


def main():
    # Indique à Django quel fichier de configuration utiliser
    # Pointe vers dump_alert/settings.py
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dump_alert.settings")

    # Importe le gestionnaire de commandes Django
    from django.core.management import execute_from_command_line

    # Exécute la commande passée en argument (sys.argv = ['manage.py', 'commande', ...])
    execute_from_command_line(sys.argv)


# Ce bloc s'exécute uniquement si on lance directement ce fichier
# (pas si on l'importe comme module)
if __name__ == "__main__":
    main()
