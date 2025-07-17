import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
HEADERS = {"x-rapidapi-host": "testhost"}

STATION = "FRPAR"
LAT = 48.8566
LON = 2.3522

# /ping
def test_ping():
    r = client.get("/ping", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

# /current
def test_current():
    r = client.get("/current", headers=HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    r2 = client.get(f"/current?station={STATION}", headers=HEADERS)
    assert r2.status_code == 200

# /history
def test_history():
    r = client.get(f"/history?station={STATION}", headers=HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    r2 = client.get(f"/history?station={STATION}&date=2024-06-09", headers=HEADERS)
    assert r2.status_code == 200

# /forecast
def test_forecast():
    r = client.get(f"/forecast?station={STATION}", headers=HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

# /stations
def test_stations():
    r = client.get("/stations", headers=HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    r2 = client.get("/stations?country=FR", headers=HEADERS)
    assert r2.status_code == 200

# Station Data endpoints
def test_station_hourly():
    r = client.get(f"/station/hourly?station={STATION}", headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert "hourly" in data

def test_station_daily():
    r = client.get(f"/station/daily?station={STATION}", headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert "daily" in data

def test_station_monthly():
    r = client.get(f"/station/monthly?station={STATION}", headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert "daily" in data  # Open-Meteo ne fournit pas de monthly, on utilise daily

def test_station_climate():
    r = client.get(f"/station/climate?station={STATION}", headers=HEADERS)
    assert r.status_code == 200 or r.status_code == 400  # 400 si pas de données pour ce point
    # On ne teste pas la structure car Open-Meteo peut retourner une erreur pour certains points

def test_station_meta():
    r = client.get(f"/station/meta?station={STATION}", headers=HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json(), dict)

def test_station_nearby():
    r = client.get(f"/station/nearby?lat={LAT}&lon={LON}", headers=HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json(), list)

# Point Data endpoints
def test_point_hourly():
    r = client.get(f"/point/hourly?lat={LAT}&lon={LON}", headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert "hourly" in data

def test_point_daily():
    r = client.get(f"/point/daily?lat={LAT}&lon={LON}", headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert "daily" in data

def test_point_monthly():
    r = client.get(f"/point/monthly?lat={LAT}&lon={LON}", headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert "daily" in data  # Open-Meteo ne fournit pas de monthly, on utilise daily

def test_point_climate():
    r = client.get(f"/point/climate?lat={LAT}&lon={LON}", headers=HEADERS)
    assert r.status_code == 200 or r.status_code == 400
    # On ne teste pas la structure car Open-Meteo peut retourner une erreur pour certains points 