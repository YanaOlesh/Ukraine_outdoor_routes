# Ukraine Outdoor Routes 🥾🚴

Interactive Web GIS platform for processing GPX tracks, spatial database management, and dynamic visualization of hiking and cycling routes and cultural monuments in Ukraine using PostGIS, Python, and Streamlit.

## Project Overview

The goal is to build an automated Spatial ETL pipeline and interactive mapping interface that processes raw GPX hiking and cycling tracks, enriches spatial geometries with terrain/elevation metrics and monuments, and dynamically presents updated route layers directly from a PostgreSQL/PostGIS spatial database.

## Methodology & Workflow

1. **Automated GPX Ingestion & ETL Pipeline**: Extracted vector geometry from raw `.gpx` tracks using `GeoPandas` and `Shapely`. Programmatically parsed track points and line geometries to calculate key spatial metrics: total distance (km) and estimated duration for both hiking and cycling activities.
2. **Elevation Profile Enrichment**: Integrated the Open-Meteo DEM API to retrieve high-resolution elevation data along route coordinates, calculating total elevation gain (m) and profile variations.
3. **PostGIS Data Integration & Dynamic Sync**: Stored route geometries and monuments layers in a centralized PostgreSQL/PostGIS spatial database. Enriched records with metadata tags (difficulty level, route type/activity, author notes). Any database updates or newly ingested routes automatically trigger live map rendering without requiring code redeployment.
4. **Interactive Web Application & Export**: Built an interactive Streamlit web map with layer controls and attribute filters. Enabled direct GPX file download capabilities so users can export processed tracks for offline GPS navigation.

## Tech Stack

- **Spatial Database**: PostgreSQL, PostGIS
- **Data Processing & Analysis**: Python, GeoPandas, Shapely, SQLAlchemy, psycopg2, Requests (Open-Meteo API)
- **Web GIS & Visualization**: Streamlit, Folium, streamlit-folium

## Project Structure

- `app.py` - Interactive Web GIS application built with Streamlit and Folium.
- `project_Ukraine_routes.ipynb` - Jupyter Notebook with the automated GPX ETL pipeline, spatial queries, and PostGIS data loading logic.
- `.env` - Local configuration file for database credentials (git-ignored).
- `requirements.txt` - Python dependencies for environment reproduction.

## How to Run

1. Clone the repository and set up your local PostGIS database (`ukraine_nature_db`).
2. Create a `.env` file and fill in your database credentials (`SQL_USER`, `SQL_PASSWORD`, `SQL_HOST`, `SQL_PORT`, `SQL_DB`).
3. Run `pip install -r requirements.txt` to install required packages.
4. Execute `streamlit run app.py` to start the interactive web application.