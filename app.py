import folium
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium
import sqlalchemy
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("SQL_USER")
DB_PASSWORD = os.getenv("SQL_PASSWORD")
DB_HOST = os.getenv("SQL_HOST", "localhost")
DB_PORT = os.getenv("SQL_PORT", "5432")
DB_NAME = os.getenv("SQL_DB", "ukraine_nature_db")

DB_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

st.set_page_config(
    page_title="В похід природою України", page_icon="🗺️", layout="wide"
)

@st.cache_resource
def get_engine():
    return sqlalchemy.create_engine(DB_URI)

engine = get_engine()


def load_routes():
  try:
    return gpd.read_postgis("SELECT * FROM routes", engine, geom_col="geom")
  except Exception as e:
    st.error(f"Помилка завантаження маршрутів: {e}")
    return gpd.GeoDataFrame()


def load_monuments():
  try:
    return gpd.read_postgis("SELECT * FROM monuments", engine, geom_col="geom")
  except Exception as e:
    st.error(f"Помилка завантаження пам'яток: {e}")
    return gpd.GeoDataFrame()


routes_df = load_routes()
monuments_df = load_monuments()


st.title("🗺️ Інтерактивна карта: Маршрути та пам'ятки України")
st.write(
    "Фільтруйте маршрути за типом, складністю та категорією прямо на карті!"
)


st.sidebar.header("⚙️ Фільтри на карті")


st.sidebar.subheader("🥾 Маршрути")
show_routes = st.sidebar.checkbox("Відображати маршрути", value=True)

selected_route_types = []
selected_difficulties = []
selected_categories = []

if show_routes and not routes_df.empty:

  if "route_type" in routes_df.columns:
    r_types = routes_df["route_type"].dropna().unique().tolist()
    selected_route_types = st.sidebar.multiselect(
        "Тип маршруту (route_type):", options=r_types, default=r_types
    )


  if "difficulty" in routes_df.columns:
    diffs = routes_df["difficulty"].dropna().unique().tolist()
    selected_difficulties = st.sidebar.multiselect(
        "Складність (difficulty):", options=diffs, default=diffs
    )


  if "category" in routes_df.columns:
    cats = routes_df["category"].dropna().unique().tolist()
    selected_categories = st.sidebar.multiselect(
        "Категорія (category):", options=cats, default=cats
    )


st.sidebar.subheader("🏛️ Пам'ятки")
show_monuments = st.sidebar.checkbox("Відображати пам'ятки", value=True)

selected_mon_types = []
if show_monuments and not monuments_df.empty:
  if "type" in monuments_df.columns:
    m_types = monuments_df["type"].dropna().unique().tolist()
    selected_mon_types = st.sidebar.multiselect(
        "Тип пам'ятки:", options=m_types, default=m_types
    )


m = folium.Map(location=[48.3794, 31.1656], zoom_start=7, control_scale=True)

if show_routes and not routes_df.empty:
  filtered_routes = routes_df.copy()

  if selected_route_types and "route_type" in filtered_routes.columns:
    filtered_routes = filtered_routes[
        filtered_routes["route_type"].isin(selected_route_types)
    ]
  if selected_difficulties and "difficulty" in filtered_routes.columns:
    filtered_routes = filtered_routes[
        filtered_routes["difficulty"].isin(selected_difficulties)
    ]
  if selected_categories and "category" in filtered_routes.columns:
    filtered_routes = filtered_routes[
        filtered_routes["category"].isin(selected_categories)
    ]

  for _, row in filtered_routes.iterrows():
    r_name = row.get("name", "Без назви")
    r_type = row.get("route_type", "-")
    r_diff = row.get("difficulty", "-")
    r_cat = row.get("category", "-")
    r_dist = row.get("distance_km", 0)

    popup_html = f"""
        <div style="font-family: Arial; width: 220px;">
            <h4 style="margin: 0 0 5px 0; color: #1f77b4;">{r_name}</h4>
            <p style="margin: 2px 0;"><b>Тип:</b> {r_type}</p>
            <p style="margin: 2px 0;"><b>Складність:</b> {r_diff}</p>
            <p style="margin: 2px 0;"><b>Категорія:</b> {r_cat}</p>
            <p style="margin: 2px 0;"><b>Довжина:</b> {r_dist} км</p>
        </div>
        """
    folium.GeoJson(
        row["geom"],
        style_function=lambda x: {
            "color": "#3388ff",
            "weight": 4,
            "opacity": 0.7,
        },
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=r_name,
    ).add_to(m)

if show_monuments and not monuments_df.empty:
  filtered_monuments = monuments_df.copy()
  if selected_mon_types and "type" in filtered_monuments.columns:
    filtered_monuments = filtered_monuments[
        filtered_monuments["type"].isin(selected_mon_types)
    ]

  for _, row in filtered_monuments.iterrows():
    geom = row["geom"]
    if geom and geom.geom_type == "Point":
      m_name = row.get("name", "Пам'ятка")
      m_type = row.get("type", "-")
      m_region = row.get("region", "-")
      m_status = row.get("condition_status", "-")
      m_desc = row.get("description", "Опис відсутній.")

      popup_html = f"""
            <div style="font-family: Arial; width: 240px;">
                <h4 style="margin: 0 0 5px 0; color: #d9534f;">{m_name}</h4>
                <p style="margin: 2px 0;"><b>Категорія:</b> {m_type}</p>
                <p style="margin: 2px 0;"><b>Регіон:</b> {m_region}</p>
                <p style="margin: 2px 0;"><b>Стан:</b> {m_status}</p>
                <hr style="margin: 6px 0;">
                <p style="margin: 2px 0; font-size: 13px; color: #333;">{m_desc}</p>
            </div>
            """

      folium.Marker(
          location=[geom.y, geom.x],
          popup=folium.Popup(popup_html, max_width=300),
          tooltip=m_name,
          icon=folium.Icon(color="red", icon="info-sign"),
      ).add_to(m)

st_folium(m, width=1200, height=700)
