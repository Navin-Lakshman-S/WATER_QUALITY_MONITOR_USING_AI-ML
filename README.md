# Water Quality Monitoring System

## Overview
This project is a comprehensive water quality monitoring system that combines Arduino-based sensors with a Streamlit web interface. The system measures key water quality parameters (pH, TDS, turbidity, and temperature) and provides real-time analysis of water drinkability along with AI-powered improvement suggestions using Google's Gemini model.

## Features
- **Real-time water quality monitoring** of critical parameters
- **Secure user authentication** via Google OAuth
- **AI-powered water quality analysis** using Google's Gemini model
- **Drinkability assessment** based on water quality parameters
- **Personalized improvement suggestions** for enhancing water quality

## Hardware Components
- ESP32 microcontroller
- pH sensor
- TDS (Total Dissolved Solids) sensor
- Turbidity sensor
- DS18B20 temperature sensor

## Software Architecture
The project consists of three main components:
1. **Arduino Code**: Collects sensor data and sends it to the Streamlit application
2. **ESP_PY Module**: Establishes serial communication between the hardware and web interface
3. **Streamlit Frontend**: Provides user authentication, data visualization, and AI analysis

## Installation

### Prerequisites
- Python 3.12.8 or 3.12.9
- Arduino IDE
- An ESP32 development board with appropriate sensors
- Google API credentials for OAuth and Gemini API

### Step 1: Clone the repository
```bash
git clone https://github.com/Navin-Lakshman-S/WATER_QUALITY_MONITOR_USING_AI-ML.git
cd WATER_QUALITY_MONITOR_USING_AI-ML
```

### Step 2: Install Python dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set up environment variables
Create a `.env` file in the project root with the following variables:
```
GEM_KEY=your_gemini_api_key
COOKIE_NAME=your_cookie_name
SIGN_KEY=your_signing_key
CL_ID=your_google_oauth_client_id
CL_SECRET=your_google_oauth_client_secret
```

### Step 4: Upload Arduino code
Open `Water_Quality_monitor_Upd/Water_Quality_monitor_Upd.ino` in the Arduino IDE and upload it to your ESP32 board.

## Usage

### Step 1: Connect the hardware
Connect the ESP32 with all sensors to your computer via USB.

### Step 2: Run the ESP communication module
```bash
python esp_py.py
```
Follow the prompts to enter the correct COM port and baud rate for your device.

### Step 3: Launch the Streamlit application
```bash
streamlit run frontend_auth.py
```

### Step 4: Access the web interface
Open your browser and navigate to http://localhost:8501. Log in with your Google account to access the dashboard.

## System Operation
1. Sign in using Google authentication
2. View real-time water quality measurements
3. Get drinkability assessment based on measured parameters
4. Request AI-powered suggestions for improving water quality
5. Refresh data to get the latest readings

## Dependencies
- streamlit
- httpx_oauth
- google-generativeai
- pyserial
- ArduinoJson (for ESP32)
- OneWire (for ESP32)
- DallasTemperature (for ESP32)

## Future Improvements
- Mobile application integration
- Historical data tracking and trend analysis
- Additional water quality parameters
- Automated alert system for concerning readings
- Cloud data storage for long-term monitoring
