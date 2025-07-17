# MeteoAPI

API météo basée sur [Open-Meteo](https://open-meteo.com/), compatible RapidAPI.

## Endpoints principaux

- `GET /current` : Météo actuelle (par station, via Open-Meteo)
- `GET /history` : Historique météo (par station et date, via Open-Meteo)
- `GET /forecast` : Prévisions météo (par station, via Open-Meteo)
- `GET /stations` : Recherche de stations météo (liste locale)
- `GET /station/hourly` : Données horaires d'une station (en réalité, données Open-Meteo pour la position de la station)
- `GET /station/daily` : Données journalières d'une station
- `GET /station/monthly` : Données mensuelles d'une station
- `GET /station/climate` : Données climatiques d'une station
- `GET /station/meta` : Métadonnées d'une station
- `GET /station/nearby` : Stations proches d'un point
- `GET /point/hourly` : Données horaires pour un point géographique (Open-Meteo)
- `GET /point/daily` : Données journalières pour un point (Open-Meteo)
- `GET /point/monthly` : Données mensuelles pour un point (Open-Meteo)
- `GET /point/climate` : Données climatiques pour un point (Open-Meteo)
- `GET /ping` : Vérification de disponibilité

## Fonctionnement

- **Toutes les données météo sont récupérées en temps réel via l'API Open-Meteo** (pas de simulation).
- Les endpoints `/station/*` utilisent les coordonnées de la station pour interroger Open-Meteo (il n'existe pas de données par ID de station chez Open-Meteo, c'est donc une "simulation live" basée sur la position).
- Les endpoints `/point/*` permettent d'obtenir la météo pour n'importe quel point géographique (latitude/longitude).

## Exemples d'utilisation

### Météo horaire pour une station (Paris)
```
GET /station/hourly?station=FRPAR
```

### Météo journalière pour un point (Toulouse)
```
GET /point/daily?lat=43.6&lon=1.44
```

### Climatologie pour une station (Lyon)
```
GET /station/climate?station=FRLYO
```

### Climatologie pour un point (Lyon)
```
GET /point/climate?lat=45.75&lon=4.85
```

## Remarques
- L'API ne nécessite pas de clé, car Open-Meteo est gratuite et sans authentification.
- Les stations sont définies localement (nom, pays, coordonnées) pour simuler un accès "par station".
- Les données sont issues en temps réel d'Open-Meteo, donc la qualité dépend de ce service.

## Lancer l'API

```bash
uvicorn main:app --reload
```

## Tester l'API

```bash
pytest test_api.py
```

---

**API développée pour démonstration, basée sur Open-Meteo.** 