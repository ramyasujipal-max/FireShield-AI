# FireShield-AI
Wildfire risk detector with nearby emergency shelters, live alerts, and map-based visualization. Built for safety, speed, and social good.

# FireShield.AI

**Wildfire Risk Predictor & Emergency Prep Assistant**

FireShield.AI is a web application that helps U.S. residents assess wildfire risk based on ZIP code and receive a personalized evacuation checklist. It also displays nearby emergency shelters using real-time geospatial data.

---

## Features

- Wildfire Risk Estimator  
  Predicts wildfire risk using fire proximity, intensity, and satellite data (supports dummy or real data), calculated in miles.

- Shelter Finder  
  Displays emergency shelters within 25 miles of the user's ZIP code using live or fallback shelter datasets.

- Map Visualizations  
  Uses PyDeck to visually show shelters and ZIP code location with interactive tooltips.

- Personalized Emergency Checklist  
  Generates a dynamic evacuation checklist based on whether the user has pets, children, or elderly care responsibilities.

- Location Summary  
  Displays the user's location name, fire distance in miles, and satellite-based confidence and brightness readings.

---

## Demo & Screenshots

Please see the `FireShieldAI_Presentation.pptx` file for a complete walkthrough of the app, including screenshots, user journey, and feature highlights.

---

## How It Works

### 1. User Input
- Enter a valid 5-digit U.S. ZIP code.
- Optionally select household conditions (pets, children, elderly).

### 2. Fire Risk Calculation
- Retrieves geolocation data based on ZIP code.
- Currently uses dummy fire data.
- To enable real fire data, uncomment the relevant code in `check_fire_risk()`.

### 3. Shelter Discovery
- Queries ArcGIS API for live shelter data.
- If no live data is found, uses fallback shelter data from a CSV file.

### 4. Visualization
- Map displays both ZIP code and nearby shelters.
- Interactive tooltips indicate location type.

---

## Files in This Repository

| File                         | Description                                |
|-----------------------------|--------------------------------------------|
| `app.py`                    | Main Streamlit application code            |
| `Shelters_Full_Mock.csv`    | Fallback shelter dataset                   |
| `FireShieldAI_Presentation.pptx` | Demo with screenshots and feature tour |
| `README.md`                 | Project overview and documentation         |

---

## Tech Stack

- Python
- Streamlit
- PyDeck
- Pandas
- ArcGIS REST API
- Zippopotam.us API

 


