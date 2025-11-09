import streamlit as st
import requests
import pydeck as pdk

st.set_page_config(page_title="Map Demo", page_icon="🗺️", layout="centered")
st.title("🗺️ City Map Viewer")

# --- Geocoding Function ---
def get_coordinates(city_name):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={city_name}"
    headers = {"User-Agent": "MapDemoApp/1.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        results = response.json()
        if results:
            loc = results[0]
            return float(loc["lat"]), float(loc["lon"]), loc["display_name"]
    return None, None, None

# --- Map Display Function ---
def show_map(lat, lon, city_name):
    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v10",  # Default style
        initial_view_state=pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=10,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=[{"lat": lat, "lon": lon}],
                get_position="[lon, lat]",
                get_color="[255, 0, 0, 160]",
                get_radius=1000,
            ),
            pdk.Layer(
                "TextLayer",
                data=[{"lat": lat, "lon": lon, "text": city_name}],
                get_position="[lon, lat]",
                get_text="text",
                get_size=16,
                get_color=[255, 255, 255],
                get_angle=0,
                get_alignment_baseline='"bottom"',
            ),
        ],
    )
    st.pydeck_chart(deck)

# --- Input UI ---
city = st.text_input("Enter a city name")

# --- Main Logic ---
if city:
    lat, lon, full_name = get_coordinates(city)
    if lat and lon:
        st.success(f"Showing map for: {full_name}")
        show_map(lat, lon, full_name)
    else:
        st.error("Could not find location. Try a more specific name.")
