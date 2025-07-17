MeteoAPI - Weather API (Open-Meteo based)
==========================================

Description
-----------
This API provides weather data for major cities/stations worldwide, using the Open-Meteo service as a backend. It is compatible with RapidAPI and offers endpoints to retrieve weather information and station metadata. The list of stations includes 500+ major cities, geographically distributed and with unique identifiers.

Features
--------
- FastAPI-based, easy to deploy and extend
- Uses Open-Meteo for real-time weather data
- Predefined list of 500+ major world cities/stations
- Unique, human-readable station IDs (e.g., FRPARIS, USNYC)
- Endpoints for current weather, forecast, all stations, and station metadata
- Error handling for unknown stations and invalid parameters

Endpoints
---------

1. `/weather/{station_id}`
   - Returns current weather for the given station ID
   - **Request Example:**
     ```http
     GET /weather/FRPARIS
     ```
   - **Response Example:**
     ```json
     {
       "station_id": "FRPARIS",
       "name": "Paris",
       "country": "France",
       "latitude": 48.8566,
       "longitude": 2.3522,
       "temperature": 19.2,
       "weather": "Partly cloudy",
       "timestamp": "2024-06-20T14:00:00Z"
     }
     ```

2. `/forecast/{station_id}`
   - Returns weather forecast for the given station ID
   - **Request Example:**
     ```http
     GET /forecast/USNYC
     ```
   - **Response Example:**
     ```json
     {
       "station_id": "USNYC",
       "name": "New York",
       "country": "United States",
       "latitude": 40.7128,
       "longitude": -74.0060,
       "forecast": [
         {"date": "2024-06-20", "temperature": 25.1, "weather": "Sunny"},
         {"date": "2024-06-21", "temperature": 23.8, "weather": "Rain showers"},
         {"date": "2024-06-22", "temperature": 24.5, "weather": "Cloudy"}
       ]
     }
     ```

3. `/stations`
   - Returns the list of all available stations (IDs, names, coordinates, country)
   - **Request Example:**
     ```http
     GET /stations
     ```
   - **Response Example:**
     ```json
     [
       {
         "id": "FRPARIS",
         "name": "Paris",
         "country": "France",
         "latitude": 48.8566,
         "longitude": 2.3522
       },
       {
         "id": "USNYC",
         "name": "New York",
         "country": "United States",
         "latitude": 40.7128,
         "longitude": -74.0060
       },
       ...
     ]
     ```

4. `/station/{station_id}`
   - Returns metadata for a specific station (name, country, coordinates)
   - **Request Example:**
     ```http
     GET /station/INDELHI
     ```
   - **Response Example:**
     ```json
     {
       "id": "INDELHI",
       "name": "Delhi",
       "country": "India",
       "latitude": 28.6139,
       "longitude": 77.2090
     }
     ```

5. `/stationmeta/{station_id}`
   - Returns extended metadata for a specific station (may include timezone, elevation, etc.)
   - **Request Example:**
     ```http
     GET /stationmeta/BRRIO
     ```
   - **Response Example:**
     ```json
     {
       "id": "BRRIO",
       "name": "Rio de Janeiro",
       "country": "Brazil",
       "latitude": -22.9068,
       "longitude": -43.1729,
       "timezone": "America/Sao_Paulo",
       "elevation": 2
     }
     ```

6. `/station/search?name={city}`
   - Search for station(s) by city or station name (case-insensitive, partial match allowed)
   - **Request Example:**
     ```http
     GET /station/search?name=paris
     ```
   - **Response Example:**
     ```json
     [
       {
         "id": "FRPARIS",
         "name": "Paris",
         "country": "France",
         "lat": 48.8566,
         "lon": 2.3522
       }
     ]
     ```
   - **Request Example (partial match):**
     ```http
     GET /station/search?name=yo
     ```
   - **Response Example:**
     ```json
     [
       {
         "id": "USNYC",
         "name": "New York",
         "country": "United States",
         "lat": 40.7128,
         "lon": -74.0060
       },
       {
         "id": "JPYOKOHAMA",
         "name": "Yokohama",
         "country": "Japan",
         "lat": 35.4437,
         "lon": 139.6380
       }
     ]
     ```

Parameters
----------
- `station_id`: Unique string identifier for each station (see `/stations` endpoint for the full list)

Data Structure
--------------
Each station is defined as:
```
{
  "id": "FRPARIS",
  "name": "Paris",
  "country": "France",
  "latitude": 48.8566,
  "longitude": 2.3522
}
```

Error Handling
--------------
- If a station ID is unknown, the API returns a 404 error with the message "Unknown station".
- If parameters are missing or invalid, a 400 error is returned.

How to Run
----------
1. Install dependencies:
   `pip install -r requirements.txt`
2. Start the API:
   `uvicorn main:app --reload`
   (from the `MeteoAPI` directory)
3. Access the documentation at `http://localhost:8000/docs`

Dependencies
------------
- fastapi
- uvicorn
- httpx (for Open-Meteo requests)

Sources
-------
- [Open-Meteo API](https://open-meteo.com/)
- List of cities: extracted from world cities datasets, curated for diversity and coverage

Notes
-----
- Station IDs are case-sensitive and must match exactly (e.g., `FRPARIS`, not `FRPAR`).
- The `/stations` endpoint is recommended for discovering available IDs.
- The API is designed for demonstration and educational purposes, not for production-scale use. 