import streamlit as st
import requests
import urllib.parse
import pydeck as pdk
import time
import json
from streamlit_lottie import st_lottie
import base64


# --- Page Setup ---
st.set_page_config(page_title="Weather App", page_icon="🌤️", layout="centered")

# --- Splash Animation ---
def load_lottiefile(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

if "show_intro" not in st.session_state:
    st.session_state.show_intro = True

if st.session_state.show_intro:
    lottie_intro = load_lottiefile("weather.json")
    splash = st.empty()
    with splash.container():
        st.markdown("<h1 style='text-align:center;'>Welcome to Weather app!</h1>", unsafe_allow_html=True)
        st_lottie(lottie_intro, height=280, speed=0.5, loop=True)
        time.sleep(2)
    splash.empty()
    st.session_state.show_intro = False

# --- Background Image ---
def set_local_background(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    css = f"""
    <style>
    html, body, .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stVerticalBlock"],
    .main, .block-container,
    .css-1d391kg, .css-18ni7ap {{
        background: transparent !important;
    }}
    section[data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(12px);
        box-shadow: inset 0 0 10px #00ffff60, 0 0 20px #00ffff88;
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }}
    section[data-testid="stSidebar"] * {{
        background-color: transparent !important;
    }}
    button:hover {{
        border: 1px solid #00ffff !important;
        box-shadow: 0 0 12px #00ffff60;
        color: #00ffff !important;
        transition: all 0.3s ease-in-out;
    }}
    #inspo-quote {{
        position: fixed;
        bottom: 12px;
        right: 18px;
        font-size: 14px;
        font-style: italic;
        color: #ffffffcc;
        background: rgba(0,0,0,0.25);
        padding: 6px 12px;
        border-radius: 8px;
        z-index: 999;
        pointer-events: none;
    }}
    </style>
    <div id="inspo-quote">“Weather is the mood of the sky.”🌤️ </div>
    """
    st.markdown(css, unsafe_allow_html=True)

set_local_background("weather app.jpg")

# app title
st.title("🌤️ Weather App")
# --- Sidebar Info ---
with st.sidebar:
    st.header("ℹ️ About This App")
    st.markdown("""
This app provides **real-time weather conditions** for any city, including:

- 🌡️ Temperature  
- 💨 Wind Speed  
- 🌈 Weather Condition  
- 🤗 Feels Like Temperature  
- 🌇 Sunset Time  
- 🛰️ Satellite Map

Built for clarity, speed, and modular design.
""")

    st.divider()

    st.header("⚙️ How It Works")
    st.markdown("""
- 🌍 **Geolocation** via OpenStreetMap  
- 🌦️ **Weather data** from Open-Meteo  
- 🗺️ **Map rendering** using Mapbox Satellite via PyDeck  
- ⚡ Optimized with caching for fast performance
""")

    st.divider()

    st.header("🔗 Source APIs")
    st.markdown("""
- [Open-Meteo](https://open-meteo.com/) — Weather data  
- [OpenStreetMap](https://nominatim.openstreetmap.org/) — Geolocation  
- [Mapbox](https://www.mapbox.com/) — Satellite maps  
""")

    st.divider()

    st.header("🙌 Credits")
    st.markdown("""
Developed by **Ansh kunwar** — 🧠 Python developer · 🎨 UI/UX Designer · ⚙️ Modular thinker

**🛠️ Technologies Used:**  
- 🐍 Python  
- 🚀 Streamlit  
- 🌐 REST APIs  
- 🗺️ PyDeck + Mapbox  

**📚 Data Sources:**  
- 🌦️ Open-Meteo  
- 🧭 OpenStreetMap  
- 🛰️ Mapbox  


**📄 License:Apache licence 2.0**  
Open-source · Educational & public use only
""")

    st.divider()

    st.header("📬 Contact Developer")
    st.markdown("""
For feedback, collaboration, or questions:

- 📧 Email: anshkunwar3009@gmail.com
- 🐙 Source code: [github.com](https://github.com/anshk1234/weather-app)  
- 🚀 See other projects: [streamlit.io/ansh kunwar](https://share.streamlit.io/user/anshk1234)
                
- Feel free to reach out!
""")
    st.markdown("<br><center>© 2025 Weather app</center>", unsafe_allow_html=True)


# --- Input UI ---
city = st.text_input("Enter city name", "")

# --- Geocoding ---
@st.cache_data
def get_coordinates(city_name):
    headers = {"User-Agent": "StreamlitWeatherApp/1.0"}
    query = urllib.parse.quote(city_name.strip().title())
    geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={query}"
    response = requests.get(geo_url, headers=headers)
    if response.status_code == 200:
        results = response.json()
        if results:
            location = results[0]
            full_name = location["display_name"]
            lat = float(location["lat"])
            lon = float(location["lon"])
            return lat, lon, full_name
    return None, None, None

# --- Weather Data Fetching ---
@st.cache_data
def get_weather(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current_weather=true"
        f"&hourly=temperature_2m,apparent_temperature"
        f"&daily=sunset"
        f"&past_days=2"  # fetch historical data for last 2 days
        f"&forecast_days=3"  # fetch forecast for next 3 days
        f"&timezone=auto"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# --- Weather Code Mapping ---
weather_codes = {
    0: "Clear ☀️",
    1: "Mainly Clear 🌤️",
    2: "Partly Cloudy ⛅",
    3: "Overcast ☁️",
    45: "Fog 🌫️",
    51: "Light Drizzle 🌦️",
    61: "Light Rain 🌧️",
    71: "Light Snow 🌨️",
    80: "Rain Showers 🌧️",
    95: "Thunderstorm ⛈️"
}




# --- Main Logic ---
if city:
    lat, lon, location_name = get_coordinates(city)
    if lat and lon:
        data = get_weather(lat, lon)
        if data:
            current = data["current_weather"]
            feels_like = data["hourly"]["apparent_temperature"][0]
            sunset = data["daily"]["sunset"][0].split("T")[1]
            condition = weather_codes.get(current["weathercode"], "Unknown")

            st.subheader(f"Weather in {location_name}")
            st.metric("🌡️ Temperature", f"{current['temperature']} °C")
            st.write(f"💨 Wind Speed: {current['windspeed']} km/h")
            st.write(f"🌈 weather Conditions: {condition}")
            st.write(f"🤗 Feels Like: {feels_like} °C")
            st.write(f"🌇 Sunset at: {sunset}")
            # --- Map Style Selector ---
            map_style_choice = st.selectbox("🗺️ Choose Map Style", ["Satellite", "Streets", "Light", "Dark"])
            style_dict = {
                "Satellite": "mapbox://styles/mapbox/satellite-v9",
                "Streets": "mapbox://styles/mapbox/streets-v11",
                "Light": "mapbox://styles/mapbox/light-v10",
                "Dark": "mapbox://styles/mapbox/dark-v10"
           }
        selected_style = style_dict[map_style_choice]
        # --- Map Display Function ---
        def show_map(lat, lon, city_name):
            st.subheader("🗺️ Location Map")
            st.pydeck_chart(pdk.Deck(
                map_style=selected_style,
                initial_view_state=pdk.ViewState(
                    latitude=lat,
                    longitude=lon,
                    zoom=10,
                    pitch=0,
            ),
            layers=[
            # 🔴 Red Marker
                pdk.Layer(
                'ScatterplotLayer',
                data=[{"lat": lat, "lon": lon}],
                get_position='[lon, lat]',
                get_color='[255, 0, 0, 160]',
                get_radius=1000,
            ),
            # 🏷️ City Name Label
            pdk.Layer(
                'TextLayer',
                data=[{"lat": lat, "lon": lon, "text": city_name}],
                get_position='[lon, lat]',
                get_text='text',
                get_size=16,
                get_color=[255, 255, 255],
                get_angle=0,
                get_alignment_baseline='"bottom"',
            )
        ],
    ))

if city:
    lat, lon, location_name = get_coordinates(city)
    if lat and lon:
        data = get_weather(lat, lon)
        if data:
            # Show weather info
            show_map(lat, lon, city)
        else:
            st.error("Weather data not available.")
    else:
        st.warning("Could not find location. Try a more specific name.")



# --- Historical & Forecast Overlay ---
if "data" in locals() and data is not None:
    st.subheader("📈 Historical & Forecast Data")
    try:
        hourly = data.get("hourly", {})
        timestamps = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        feels = hourly.get("apparent_temperature", [])

        if timestamps and temps and feels:
            st.markdown("**Last 5 Hours:**")
            for i in range(5):
                st.write(f"🕒 {timestamps[i]} — 🌡️ {temps[i]}°C | 🤗 Feels like: {feels[i]}°C")

            st.markdown("**Next 5 Hours:**")
            for i in range(len(timestamps) - 5, len(timestamps)):
                st.write(f"🕒 {timestamps[i]} — 🌡️ {temps[i]}°C | 🤗 Feels like: {feels[i]}°C")

            st.markdown("**Temperature Trend (Hourly):**")
            st.line_chart({
                "Temperature (°C)": temps,
                "Feels Like (°C)": feels
            })
        else:
            st.warning("Hourly temperature data is missing.")
    except Exception:
        pass  # Silently skip if something goes wrong
        
# ---- Footer ----
st.markdown("<p style='text-align:center; color:white;'>© 2025 Weather app| Powered by Open-Meteo</p>", unsafe_allow_html=True)





