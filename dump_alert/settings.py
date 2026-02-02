"""
Configuration Django pour le projet Dump Alert.

Ce fichier centralise TOUS les paramètres de l'application :
- Base de données
- Applications installées
- Sécurité
- Internationalisation
- Fichiers statiques et médias
"""

import os
from pathlib import Path

# =============================================================================
# CHEMINS
# =============================================================================
# Chemin racine du projet (dossier contenant manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# GDAL/GEOS/PROJ - Bibliothèques géospatiales (via QGIS)
# =============================================================================
# QGIS inclut ces bibliothèques, on les réutilise pour GeoDjango
QGIS_PATH = r"C:\Program Files\QGIS 3.40.15"
os.environ['PATH'] = os.path.join(QGIS_PATH, 'bin') + ';' + os.environ.get('PATH', '')
os.environ['PROJ_LIB'] = os.path.join(QGIS_PATH, 'share', 'proj')

GDAL_LIBRARY_PATH = os.path.join(QGIS_PATH, 'bin', 'gdal312.dll')
GEOS_LIBRARY_PATH = os.path.join(QGIS_PATH, 'bin', 'geos_c.dll')


# =============================================================================
# SÉCURITÉ
# =============================================================================
# Clé secrète pour le chiffrement (sessions, CSRF, etc.)
# /!\ En production : utiliser une variable d'environnement !
SECRET_KEY = 'django-insecure-%-1jkiqf%d^o7z#zk3xq#)cma5$1^f6#hvfi*sdy2g4o^=p86h'

# Mode debug : affiche les erreurs détaillées
# /!\ Mettre à False en production !
DEBUG = True

# Domaines autorisés à accéder à l'application
# Ex: ['monsite.com', 'www.monsite.com']
ALLOWED_HOSTS = []


# =============================================================================
# APPLICATIONS INSTALLÉES
# =============================================================================
INSTALLED_APPS = [
    # --- Apps Django par défaut ---
    'django.contrib.admin',         # Interface d'administration
    'django.contrib.auth',          # Authentification utilisateurs
    'django.contrib.contenttypes',  # Types de contenu (pour les relations)
    'django.contrib.sessions',      # Sessions utilisateur
    'django.contrib.messages',      # Messages flash (notifications)
    'django.contrib.staticfiles',   # Fichiers statiques (CSS, JS)

    # --- GeoDjango ---
    'django.contrib.gis',           # Extension géospatiale de Django

    # --- Apps tierces ---
    'leaflet',                      # Cartes interactives OpenStreetMap

    # --- Nos applications ---
    'reports',                      # Gestion des signalements
]


# =============================================================================
# MIDDLEWARE
# =============================================================================
# Couches de traitement qui s'exécutent à chaque requête/réponse
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',        # Sécurité HTTP
    'django.contrib.sessions.middleware.SessionMiddleware', # Gestion sessions
    'django.middleware.common.CommonMiddleware',            # Traitements communs
    'django.middleware.csrf.CsrfViewMiddleware',            # Protection CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Auth user
    'django.contrib.messages.middleware.MessageMiddleware', # Messages flash
    'django.middleware.clickjacking.XFrameOptionsMiddleware',   # Anti-clickjack
]


# =============================================================================
# URLS ET TEMPLATES
# =============================================================================
# Fichier principal des routes URL
ROOT_URLCONF = 'dump_alert.urls'

# Configuration des templates HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],           # Dossiers de templates personnalisés
        'APP_DIRS': True,     # Chercher les templates dans chaque app
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Point d'entrée WSGI (serveur web)
WSGI_APPLICATION = 'dump_alert.wsgi.application'


# =============================================================================
# BASE DE DONNÉES
# =============================================================================
# PostgreSQL + PostGIS local via Docker
# Commande : docker run -d --name dump-alert-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=dump_alert -p 5432:5432 postgis/postgis:16-3.4
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'dump_alert',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# =============================================================================
# VALIDATION DES MOTS DE PASSE
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================================
# INTERNATIONALISATION
# =============================================================================
LANGUAGE_CODE = 'fr-fr'         # Langue de l'interface
TIME_ZONE = 'Europe/Paris'      # Fuseau horaire
USE_I18N = True                 # Activer les traductions
USE_TZ = True                   # Utiliser les fuseaux horaires


# =============================================================================
# FICHIERS STATIQUES ET MÉDIAS
# =============================================================================
# Fichiers statiques (CSS, JS, images de l'interface)
STATIC_URL = 'static/'

# Fichiers médias (uploads utilisateurs : images des signalements)
MEDIA_URL = '/media/'               # URL publique
MEDIA_ROOT = BASE_DIR / 'media'     # Dossier physique sur le disque

# Type de clé primaire par défaut pour les modèles
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# CONFIGURATION LEAFLET (CARTES)
# =============================================================================
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (49.43060, 2.08186),     # Centre de Beauvais (depuis QGIS)
    'DEFAULT_ZOOM': 13,                         # Zoom ville (rues visibles)
    'MIN_ZOOM': 10,                             # Zoom min (agglo Beauvais)
    'MAX_ZOOM': 18,                             # Zoom max (détail parcelles)
    'TILES': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',  # Tuiles OSM
    'ATTRIBUTION_PREFIX': 'Dump Alert - Beauvais',
    'RESET_VIEW': False,                        # Désactive le bouton "Réinitialiser"
    'PLUGINS': {
        'geocoder': {
            'css': ['https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.css'],
            'js': ['https://unpkg.com/leaflet-control-geocoder/dist/Control.Geocoder.js'],
            'auto-include': True,
        },
    },
}
