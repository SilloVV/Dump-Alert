# Dump Alert

Application Django/GeoDjango de signalement de dépôts sauvages avec géolocalisation et heatmap.

## Fonctionnalités

- Signalement avec upload d'image et niveau de dangerosité
- Validation/rejet des signalements par un administrateur
- Géolocalisation sur carte interactive
- Génération de marker sur une map QGsis 

## Prérequis

- Python >= 3.11
- [uv](https://github.com/astral-sh/uv)
- [QGIS](https://qgis.org/) ou [OSGeo4W](https://trac.osgeo.org/osgeo4w/) (Windows) pour les bibliothèques GDAL/GEOS


![Map QGIS](Dump-Alert/images_readme/beauvais.png)

## Installation (Windows)

**Important :** Utiliser le **shell OSGeo4W** pour que les dépendances GDAL soient accessibles.

```bash
# 1. Ouvrir "OSGeo4W Shell" depuis le menu Démarrer (installé avec QGIS)

# 2. Naviguer vers le projet
cd C:\Users\User\Desktop\dump-alert\Dump-Alert

# 3. Activer l'environnement et lancer
.venv\Scripts\activate
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Technologies

Django 5.2 • GeoDjango • SpatiaLite/PostGIS • django-leaflet • Pillow
