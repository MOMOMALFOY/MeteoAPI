# MeteoAPI

API météo d'exemple inspirée de Meteostat, compatible RapidAPI.

## Endpoints principaux

- `GET /current` : Météo actuelle (par station)
- `GET /history` : Historique météo (par station et date)
- `GET /forecast` : Prévisions météo (par station)
- `GET /stations` : Recherche de stations météo (par pays)
- `GET /ping` : Vérification de disponibilité

## Exemple d'utilisation

### Météo actuelle
```
GET /current?station=FRPAR
```

### Historique météo
```
GET /history?station=FRPAR&date=2024-06-09
```

### Prévisions météo
```
GET /forecast?station=FRPAR
```

### Recherche de stations
```
GET /stations?country=FR
```

## Remarques
- Cette API est un exemple : les données sont simulées.
- L'accès est restreint au proxy RapidAPI (vérification des headers).
- Pour une vraie intégration, il suffit de remplacer les listes simulées par des appels à l'API Meteostat officielle. 