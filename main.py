from fastapi import FastAPI, Query, HTTPException, Request, Body
from typing import List, Optional
from pydantic import BaseModel
import httpx

app = FastAPI(
    title="MeteoAPI",
    description="API météo inspirée de Meteostat, compatible RapidAPI.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Current", "description": "Météo actuelle"},
        {"name": "History", "description": "Historique météo"},
        {"name": "Forecast", "description": "Prévisions météo"},
        {"name": "Stations", "description": "Recherche de stations météo"},
        {"name": "Station Data", "description": "Données de la station"},
        {"name": "Point Data", "description": "Données du point"}
    ]
)

# Modèles de données
class WeatherCurrent(BaseModel):
    station: str
    temperature: float
    humidity: int
    wind_speed: float
    condition: str
    time: str

class WeatherHistory(BaseModel):
    station: str
    date: str
    temperature_avg: float
    temperature_min: float
    temperature_max: float
    precipitation: float

class WeatherForecast(BaseModel):
    station: str
    date: str
    temperature_min: float
    temperature_max: float
    precipitation: float
    condition: str

class Station(BaseModel):
    id: str
    name: str
    country: str
    region: Optional[str] = None
    lat: float
    lon: float

# Modèles pour les nouveaux endpoints
class HourlyData(BaseModel):
    time: str
    temperature: float
    humidity: int
    precipitation: float
    wind_speed: float

class DailyData(BaseModel):
    date: str
    temperature_min: float
    temperature_max: float
    precipitation: float

class MonthlyData(BaseModel):
    month: str
    temperature_avg: float
    precipitation: float

class ClimateData(BaseModel):
    period: str
    temperature_avg: float
    precipitation: float

class StationMeta(BaseModel):
    id: str
    name: str
    country: str
    lat: float
    lon: float
    elevation: float

# Données simulées
STATIONS = [
    Station(id="FRPAR", name="Paris", country="FR", region="Île-de-France", lat=48.8566, lon=2.3522),
    Station(id="FRLYS", name="Lyon", country="FR", region="Auvergne-Rhône-Alpes", lat=45.75, lon=4.85)
]

CURRENT_WEATHER = [
    WeatherCurrent(station="FRPAR", temperature=22.5, humidity=60, wind_speed=12.0, condition="Ensoleillé", time="2024-06-10T14:00:00Z"),
    WeatherCurrent(station="FRLYS", temperature=20.0, humidity=65, wind_speed=10.0, condition="Nuageux", time="2024-06-10T14:00:00Z")
]

HISTORY = [
    WeatherHistory(station="FRPAR", date="2024-06-09", temperature_avg=18.0, temperature_min=14.0, temperature_max=22.0, precipitation=0.0),
    WeatherHistory(station="FRLYS", date="2024-06-09", temperature_avg=17.0, temperature_min=13.0, temperature_max=21.0, precipitation=1.2)
]

FORECAST = [
    WeatherForecast(station="FRPAR", date="2024-06-11", temperature_min=15.0, temperature_max=24.0, precipitation=0.0, condition="Ensoleillé"),
    WeatherForecast(station="FRLYS", date="2024-06-11", temperature_min=14.0, temperature_max=22.0, precipitation=0.5, condition="Pluie")
]

# Vérification proxy RapidAPI
async def verify_rapidapi_proxy(request: Request):
    if not (request.headers.get("x-rapidapi-host") or request.headers.get("x-rapidapi-user")):
        raise HTTPException(status_code=401, detail="Accès uniquement via le proxy RapidAPI.")

# Helper pour trouver les coordonnées d'une station
station_coords = {s.id: (s.lat, s.lon) for s in STATIONS}

# Endpoints
@app.get("/current", response_model=List[WeatherCurrent], tags=["Current"])
async def get_current_weather(request: Request, station: Optional[str] = Query(None)):
    await verify_rapidapi_proxy(request)
    if station:
        return [w for w in CURRENT_WEATHER if w.station == station]
    return CURRENT_WEATHER

@app.get("/history", response_model=List[WeatherHistory], tags=["History"])
async def get_weather_history(request: Request, station: str = Query(...), date: Optional[str] = Query(None)):
    await verify_rapidapi_proxy(request)
    results = [h for h in HISTORY if h.station == station]
    if date:
        results = [h for h in results if h.date == date]
    return results

@app.get("/forecast", response_model=List[WeatherForecast], tags=["Forecast"])
async def get_weather_forecast(request: Request, station: str = Query(...)):
    await verify_rapidapi_proxy(request)
    return [f for f in FORECAST if f.station == station]

@app.get("/stations", response_model=List[Station], tags=["Stations"])
async def get_stations(request: Request, country: Optional[str] = Query(None)):
    await verify_rapidapi_proxy(request)
    if country:
        return [s for s in STATIONS if s.country == country]
    return STATIONS

@app.get("/ping", tags=["Current"])
async def ping():
    return {"status": "ok"}

# Station Data
@app.get("/station/hourly", tags=["Station Data"])
async def get_hourly_station_data(request: Request, station: str = Query(...)):
    await verify_rapidapi_proxy(request)
    lat, lon = station_coords.get(station, (None, None))
    if lat is None or lon is None:
        raise HTTPException(status_code=404, detail="Station inconnue")
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPEN_METEO_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()
    return data

@app.get("/station/daily", tags=["Station Data"])
async def get_daily_station_data(request: Request, station: str = Query(...)):
    await verify_rapidapi_proxy(request)
    lat, lon = station_coords.get(station, (None, None))
    if lat is None or lon is None:
        raise HTTPException(status_code=404, detail="Station inconnue")
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPEN_METEO_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()
    return data

@app.get("/station/monthly", tags=["Station Data"])
async def get_monthly_station_data(request: Request, station: str = Query(...)):
    await verify_rapidapi_proxy(request)
    lat, lon = station_coords.get(station, (None, None))
    if lat is None or lon is None:
        raise HTTPException(status_code=404, detail="Station inconnue")
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPEN_METEO_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()
    return data

@app.get("/station/climate", tags=["Station Data"])
async def get_station_climate_data(request: Request, station: str = Query(...)):
    await verify_rapidapi_proxy(request)
    lat, lon = station_coords.get(station, (None, None))
    if lat is None or lon is None:
        raise HTTPException(status_code=404, detail="Station inconnue")
    climate_url = "https://climate-api.open-meteo.com/v1/climate"
    params = {
        "latitude": lat,
        "longitude": lon,
        "models": "ERA5",
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_mean",
        "start_date": "1991-01-01",
        "end_date": "2020-12-31"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(climate_url, params=params)
        if resp.status_code == 400:
            return {"error": True, "reason": "No climate data for this location"}
        resp.raise_for_status()
        data = resp.json()
    return data

@app.get("/station/meta", tags=["Station Data"])
async def get_station_meta_data(request: Request, station: str = Query(...)):
    await verify_rapidapi_proxy(request)
    s = next((s for s in STATIONS if s.id == station), None)
    if not s:
        raise HTTPException(status_code=404, detail="Station inconnue")
    return s

@app.get("/station/nearby", tags=["Station Data"])
async def get_nearby_stations(request: Request, lat: float = Query(...), lon: float = Query(...)):
    await verify_rapidapi_proxy(request)
    # Retourne les stations connues les plus proches (ici, toutes)
    return STATIONS

# Point Data
OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"

@app.get("/point/hourly", tags=["Point Data"])
async def get_hourly_point_data(request: Request, lat: float = Query(...), lon: float = Query(...)):
    await verify_rapidapi_proxy(request)
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPEN_METEO_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()
    return data

@app.get("/point/daily", tags=["Point Data"])
async def get_daily_point_data(request: Request, lat: float = Query(...), lon: float = Query(...)):
    await verify_rapidapi_proxy(request)
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPEN_METEO_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()
    return data

@app.get("/point/monthly", tags=["Point Data"])
async def get_monthly_point_data(request: Request, lat: float = Query(...), lon: float = Query(...)):
    await verify_rapidapi_proxy(request)
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(OPEN_METEO_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()
    return data

@app.get("/point/climate", tags=["Point Data"])
async def get_point_climate_data(request: Request, lat: float = Query(...), lon: float = Query(...)):
    await verify_rapidapi_proxy(request)
    climate_url = "https://climate-api.open-meteo.com/v1/climate"
    params = {
        "latitude": lat,
        "longitude": lon,
        "models": "ERA5",
        "daily": "temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum,wind_speed_10m_mean",
        "start_date": "1991-01-01",
        "end_date": "2020-12-31"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(climate_url, params=params)
        if resp.status_code == 400:
            return {"error": True, "reason": "No climate data for this location"}
        resp.raise_for_status()
        data = resp.json()
    return data 