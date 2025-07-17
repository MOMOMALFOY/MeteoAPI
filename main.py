from fastapi import FastAPI, Query, HTTPException, Request, Body
from typing import List, Optional
from pydantic import BaseModel
import httpx
from stations import STATIONS
import math

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

# Vérification proxy RapidAPI
async def verify_rapidapi_proxy(request: Request):
    if not (request.headers.get("x-rapidapi-host") or request.headers.get("x-rapidapi-user")):
        raise HTTPException(status_code=401, detail="Accès uniquement via le proxy RapidAPI.")

# Helper pour trouver les coordonnées d'une station
station_coords = {s["id"]: (s["lat"], s["lon"]) for s in STATIONS}

# Endpoints
@app.get("/current", tags=["Current"])
async def get_current_weather(request: Request, station: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None):
    await verify_rapidapi_proxy(request)
    if station:
        coords = station_coords.get(station)
        if not coords:
            raise HTTPException(status_code=404, detail="Station inconnue")
        lat, lon = coords
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Paramètres manquants (station ou lat/lon)")
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto"
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(OPEN_METEO_BASE, params=params)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Erreur Open-Meteo")
        data = r.json()
        if "hourly" in data and "time" in data["hourly"]:
            idx = -1
            result = {k: v[idx] for k, v in data["hourly"].items()}
            return result
        return data

@app.get("/history", tags=["History"])
async def get_history_weather(request: Request, station: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None, date: Optional[str] = None):
    await verify_rapidapi_proxy(request)
    if station:
        coords = station_coords.get(station)
        if not coords:
            raise HTTPException(status_code=404, detail="Station inconnue")
        lat, lon = coords
    if lat is None or lon is None or date is None:
        raise HTTPException(status_code=400, detail="Paramètres manquants (station/lat/lon/date)")
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date,
        "end_date": date,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone": "auto"
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(OPEN_METEO_BASE, params=params)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Erreur Open-Meteo")
        return r.json()

@app.get("/forecast", tags=["Forecast"])
async def get_forecast_weather(request: Request, station: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None, days: int = 7):
    await verify_rapidapi_proxy(request)
    if station:
        coords = station_coords.get(station)
        if not coords:
            raise HTTPException(status_code=404, detail="Station inconnue")
        lat, lon = coords
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="Paramètres manquants (station ou lat/lon)")
    if days is None:
        days = 7
    from datetime import date, timedelta
    start = date.today().isoformat()
    end = (date.today() + timedelta(days=days)).isoformat()
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone": "auto"
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(OPEN_METEO_BASE, params=params)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Erreur Open-Meteo")
        return r.json()

@app.get("/stations", response_model=List[Station], tags=["Stations"])
async def get_stations(request: Request, country: Optional[str] = Query(None)):
    await verify_rapidapi_proxy(request)
    if country:
        return [s for s in STATIONS if s["country"] == country]
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
    s = next((s for s in STATIONS if s["id"] == station), None)
    if not s:
        raise HTTPException(status_code=404, detail="Station inconnue")
    return s

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Rayon de la Terre en km
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

@app.get("/station/nearby", tags=["Stations"])
async def get_station_nearby(request: Request, lat: Optional[float] = None, lon: Optional[float] = None):
    await verify_rapidapi_proxy(request)
    if lat is None or lon is None:
        raise HTTPException(status_code=400, detail="lat and lon are required")
    stations_with_dist = [
        (s, haversine(lat, lon, s["lat"], s["lon"])) for s in STATIONS
    ]
    stations_with_dist.sort(key=lambda x: x[1])
    return [s for s, d in stations_with_dist[:5]]

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

@app.get("/station/search", tags=["Stations"])
async def search_station_by_name(request: Request, name: str = Query(..., description="City or station name to search")):
    await verify_rapidapi_proxy(request)
    name_lower = name.lower()
    results = [
        {"id": s["id"], "name": s["name"], "country": s["country"], "lat": s["lat"], "lon": s["lon"]}
        for s in STATIONS if name_lower in s["name"].lower()
    ]
    if not results:
        raise HTTPException(status_code=404, detail="No station found for this name")
    return results 