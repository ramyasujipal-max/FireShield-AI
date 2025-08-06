import streamlit as st
import requests
import pandas as pd
from math import radians, cos, sin, sqrt, atan2
import pydeck as pdk
# --------------------------
# CSS Styling
# --------------------------
page_bg_css = """
<style>
body {
    background-color: #fcefee;
}

.stApp::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.4);
    z-index: -1;
}

.stApp {
    background-image: url("https://images.unsplash.com/photo-1508780709619-79562169bc64");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}

[data-testid="stSidebar"], .main, .block-container {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(8px);
    border-radius: 16px;
    padding: 2rem;
}

h1, h2, h3, h4, h5, h6, .markdown-text-container, label, p {
    font-weight: 700 !important;
    font-size: 1.2rem !important;
    color: #222222 !important;
}

.project-title {
    font-size: 2.5rem !important;
    font-weight: 800 !important;
    text-align: center;
    color: #222;
    margin-bottom: 1rem;
}

input[type="text"] {
    border: 2px solid #ccc !important;
    border-radius: 8px !important;
    padding: 10px !important;
    font-size: 1.1rem !important;
    background-color: #fff !important;
    color: #000 !important;
}
</style>
"""
st.markdown(page_bg_css, unsafe_allow_html=True)

def show_warning_box(message):
    st.markdown(f"""
    <div style="
        padding: 1rem;
        border-radius: 8px;
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
        font-weight: bold;
        margin-bottom: 1rem;
    ">
        🚫 {message}
    </div>
    """, unsafe_allow_html=True)


#if st.button("🔄 Clear Cache and Reload"):
#    st.cache_data.clear()
#   st.experimental_rerun()

#Get live emergency shelter data from the ArcGIS REST API for a given U.S. state.
def get_live_shelters(state_abbr="MD"):
    url = "https://services1.arcgis.com/99lidPhWCzftIe9K/arcgis/rest/services/Shelters/FeatureServer/0/query"
    params = {
        "where": f"STATE='{state_abbr}'",
        "outFields": "*",
        "f": "json",
        "returnGeometry": "true"
    }

    response = requests.get(url, params=params)

    #  Try parsing as JSON
    try:
        data = response.json()
    except Exception as e:
        st.error("❌ Failed to parse shelter API response.")
        return pd.DataFrame()

    #  Check for 'features' key
    if "features" not in data:
        show_warning_box(f"No shelters returned for state: {state_abbr}")
        return pd.DataFrame()

    #  Parse the data
    shelters = []
    for feature in data["features"]:
        attr = feature["attributes"]
        geom = feature.get("geometry")
        if geom:
            shelters.append({
                "Name": attr.get("NAME", ""),
                "Address": attr.get("ADDRESS", ""),
                "City": attr.get("CITY", ""),
                "ZIP": attr.get("ZIP", ""),
                "lat": geom["y"],
                "lon": geom["x"],
                "State": attr.get("STATE", "")
            })

    return pd.DataFrame(shelters)



# --------------------------
#  Fire Risk Logic
# --------------------------
def get_coordinates(zip_code):
    try:
        url = f"http://api.zippopotam.us/us/{zip_code}"
        response = requests.get(url)
        data = response.json()
        lat = float(data['places'][0]['latitude'])
        lon = float(data['places'][0]['longitude'])
        place_name = data['places'][0]['place name']
        state = data['places'][0]['state abbreviation']
        location_name = f"{place_name}, {state}"
        return lat, lon, location_name
    except:
        return None, None, None


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c
    
    
@st.cache_data(ttl=3600)
def check_fire_risk(lat, lon, radius_km=25):
    #  Fake fire for testing purposes
    fires = [{
        'distance_km': 50,
        'confidence': 'high',
        'brightness': 400.5
    }]
    return fires

  #real data uncomment        
 #   try:
 #       df = load_fire_data()
 #   except Exception as e:
 #       return None  # <– return None instead of []
    
 #   fires = []
 #   for _, row in df.iterrows():
 #       fire_lat = row['latitude']
 #       fire_lon = row['longitude']
 #       distance = haversine(lat, lon, fire_lat, fire_lon)

 #       if distance <= radius_km:
 #           fires.append({
 #               "distance_km": round(distance, 1),
 #              "confidence": row.get('confidence', 'unknown'),
 #               "brightness": row.get('bright_ti4', 'N/A')
 #           })

 #   return fires


def load_fallback_shelters(state_abbr="CA"):
    try:
        df = pd.read_csv("Shelters_Full_Mock.csv")

        # Ensure column names are clean and uppercase matches
        df.columns = df.columns.str.upper()

        if 'STATE' not in df.columns:
            st.error("❌ 'STATE' column missing in fallback CSV.")
            return pd.DataFrame()

        filtered_df = df[df['STATE'].str.upper() == state_abbr.upper()]

        if filtered_df.empty:
            st.warning(f"⚠️ No fallback shelters found for state: {state_abbr}")

        return filtered_df

    except FileNotFoundError:
        st.error("❌ Shelters_Full_Mock.csv not found.")
        return pd.DataFrame()

    except Exception as e:
        st.error(f"⚠️ Could not load fallback shelter list. Error: {e}")
        return pd.DataFrame()



def get_wildfire_risk(zip_code):
    lat, lon, location_name = get_coordinates(zip_code)
    if lat is None:
        return "❌ Invalid ZIP Code or unable to fetch coordinates.", None, None, None

    fires_nearby = check_fire_risk(lat, lon)
    if not fires_nearby:
        return (
            f"✅ ZIP Code {zip_code} is currently at **Low Risk** — no fires within 25 km.",
            lat,
            lon,
            location_name
        )

    closest_fire = min(fires_nearby, key=lambda x: x['distance_km'])
    distance = closest_fire['distance_km']
    confidence = closest_fire['confidence']
    brightness = closest_fire['brightness']

    #  Custom message based on dummy values
    if distance < 5 and brightness > 350 and confidence == 'high':
        risk_level = "🚨 **High Risk 🔴** - Immediate danger in your area!"
    elif distance < 15 and brightness > 300 and confidence in ['high', 'nominal']:
        risk_level = "⚠️ **Moderate Risk 🔶** - Stay alert, fire nearby."
    elif distance < 25 and brightness > 250:
        risk_level = "⚠️ **Low-Moderate Risk 🟡** - Fire detected in your region."
    else:
        risk_level = "✅ **Low Risk 🟢** - No immediate fire threats."

    message = (
        f"{risk_level}\n"
        f"🔥 Closest fire: {distance} km away\n"
        f"Confidence: {confidence} | Brightness: {brightness}"
    )

    return message, lat, lon, location_name




# --------------------------
#  Streamlit UI
# --------------------------
st.markdown('<h1 class="project-title">🔥 FireShield.AI</h1>', unsafe_allow_html=True)
st.subheader("Wildfire Risk Predictor & Emergency Prep Assistant")

st.markdown("""
Protect your home and family from wildfires.  
Enter your location and we'll provide a fire risk estimate and personalized evacuation checklist.
""")

# Step 1: User input
zip_code = st.text_input("📍 Enter your U.S. ZIP Code").strip()
st.caption("Only 5-digit U.S. ZIP Codes supported.")
st.divider()

# Step 2: Checklist inputs
st.subheader("🧾 Personalize Your Checklist")
has_pets = st.checkbox("I have pets")
has_kids = st.checkbox("I have young children")
has_elderly = st.checkbox("I care for elderly or sick people")

# Step 3: Run on button click
if st.button("🚨 Generate My Checklist & Risk"):
    if not zip_code.isdigit() or len(zip_code) != 5:
        st.error("❌ Please enter a valid 5-digit U.S. ZIP Code.")
    else:
        # Get wildfire risk and location
        risk_message, lat, lon, location_name = get_wildfire_risk(zip_code)

        if lat and lon:
            # 🔻 Shelter block
            state_abbr = location_name.split(",")[-1].strip()

            with st.spinner("🔍 Finding nearby emergency shelters..."):
                shelters_df = get_live_shelters(state_abbr)

                if shelters_df.empty:
                    st.warning(f"⚠️ No live shelters found. Showing fallback list for {state_abbr}.")
                    shelters_df = load_fallback_shelters(state_abbr)

                if not shelters_df.empty:
                    try:
                        shelters_df['distance_km'] = shelters_df.apply(
                            lambda row: haversine(lat, lon, row['LATITUDE'], row['LONGITUDE']), axis=1
                        )
                        nearby_shelters = shelters_df[shelters_df['distance_km'] <= 25]
                    except:
                        nearby_shelters = pd.DataFrame()

                    if not nearby_shelters.empty:
                        st.subheader("🏠 Emergency Shelters Nearby (within 25 km):")

                        # Prepare data for pydeck
                        shelters_map_df = nearby_shelters[['LATITUDE', 'LONGITUDE']].rename(
                            columns={'LATITUDE': 'lat', 'LONGITUDE': 'lon'}
                        )
                        shelters_map_df['type'] = 'shelter'

                        zip_df = pd.DataFrame([{'lat': lat, 'lon': lon, 'type': 'zip'}])
                        map_df = pd.concat([shelters_map_df, zip_df], ignore_index=True)

                        # Define layers
                        shelter_layer = pdk.Layer(
                            "ScatterplotLayer",
                            data=map_df[map_df['type'] == 'shelter'],
                            get_position='[lon, lat]',
                            get_color='[0, 200, 0, 180]',  # Green
                            get_radius=1000,
                            pickable=True
                        )

                        zip_layer = pdk.Layer(
                            "ScatterplotLayer",
                            data=map_df[map_df['type'] == 'zip'],
                            get_position='[lon, lat]',
                            get_color='[0, 0, 255, 180]',  # Blue
                            get_radius=700,
                            pickable=True
                        )

                        view_state = pdk.ViewState(
                            latitude=lat,
                            longitude=lon,
                            zoom=10,
                            pitch=0
                        )

                        st.pydeck_chart(pdk.Deck(
                            layers=[zip_layer, shelter_layer],
                            initial_view_state=view_state,
                            tooltip={"html": "<b>Type:</b> {type}", "style": {"backgroundColor": "gray", "color": "white"}}
                        ))

                        st.dataframe(nearby_shelters[['NAME', 'ADDRESS', 'CITY', 'ZIP', 'distance_km']].sort_values(by='distance_km'))
                    else:
                        st.subheader("📜 Emergency Shelter Directory")
                        st.dataframe(shelters_df[['NAME', 'ADDRESS', 'CITY', 'ZIP']].sort_values(by='CITY'))
                        st.info("✅ No shelters within 25 km, but your area may still be safe.")
                else:
                    st.info("ℹ️ No shelter data available at this time.")

            # 🔺 End shelter block

            #  Fire risk info
            st.subheader("🔥 Estimated Fire Risk:")
            st.markdown(risk_message)

            if location_name:
                st.write(f"📍 Location: **{location_name}**")

            st.subheader("📍 ZIP Code Location")
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))

            #  Checklist logic
            checklist = [
                "Water (1 gallon per person per day)",
                "Non-perishable food (3-day supply)",
                "Phone charger and power bank",
                "Important documents (ID, insurance, etc.)",
                "First aid kit"
            ]
            if has_pets:
                checklist.append("Pet food, leash, carrier")
            if has_kids:
                checklist.append("Baby formula, diapers, comfort toy")
            if has_elderly:
                checklist.append("Medications, glasses, medical devices")

            st.subheader("🧳 Emergency Evacuation Checklist:")
            for item in checklist:
                st.markdown(f"- {item}")
        else:
            st.warning("⚠️ Couldn't determine your location from the ZIP code.")





