/**
 * Ajoute un champ de recherche d'adresse à la carte Leaflet.
 * Charge dynamiquement le plugin Geocoder pour éviter les problèmes d'ordre de chargement.
 */

// URL du plugin Leaflet Control Geocoder (CDN)
const GEOCODER_CSS = 'https://unpkg.com/leaflet-control-geocoder@2.4.0/dist/Control.Geocoder.css';
const GEOCODER_JS = 'https://unpkg.com/leaflet-control-geocoder@2.4.0/dist/Control.Geocoder.js';

/**
 * Charge dynamiquement un fichier CSS
 */
function loadCSS(url) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = url;
    document.head.appendChild(link);
}

/**
 * Charge dynamiquement un fichier JS et retourne une Promise
 */
function loadJS(url) {
    return new Promise(function(resolve, reject) {
        const script = document.createElement('script');
        script.src = url;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

/**
 * Initialise le geocoder sur la carte
 */
function initGeocoder(map) {
    const geocoder = L.Control.geocoder({
        defaultMarkGeocode: false,
        placeholder: 'Rechercher une adresse...',
        errorMessage: 'Adresse non trouvée',
        collapsed: false,  // Toujours visible
        geocoder: L.Control.Geocoder.nominatim({
            geocodingQueryParams: {
                countrycodes: 'fr',
                viewbox: '1.9,49.5,2.2,49.35',
                bounded: 1
            }
        })
    });

    // Quand une adresse est sélectionnée, centrer la carte
    geocoder.on('markgeocode', function(e) {
        const center = e.geocode.center;
        map.setView(center, 17);
    });

    // Ajouter à la carte
    geocoder.addTo(map);
    console.log('Geocoder ajouté à la carte');
}

// Écouter l'événement django-leaflet quand une carte est initialisée
window.addEventListener('map:init', function(event) {
    const map = event.detail.map;

    // Charger le CSS
    loadCSS(GEOCODER_CSS);

    // Vérifier si le plugin est déjà chargé
    if (typeof L.Control.Geocoder !== 'undefined') {
        initGeocoder(map);
        return;
    }

    // Sinon, charger le JS dynamiquement puis initialiser
    loadJS(GEOCODER_JS)
        .then(function() {
            console.log('Plugin Geocoder chargé dynamiquement');
            initGeocoder(map);
        })
        .catch(function(error) {
            console.error('Erreur lors du chargement du plugin Geocoder:', error);
        });
});
