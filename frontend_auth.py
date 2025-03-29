import streamlit as st
import secrets
import base64
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2
import esp_py
import random
import warnings
import google.generativeai as gen
from dotenv import load_dotenv
import os
load_dotenv()

gen.configure(api_key=os.getenv("GEM_KEY"))

warnings.filterwarnings("ignore", message="Please replace `st.experimental_get_query_params`")
warnings.filterwarnings("ignore", message="Please replace `st.experimental_set_query_params`")
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Initialize session state properly
if 'email' not in st.session_state:
    st.session_state.email = ''

cokie_name = os.getenv("COOKIE_NAME")
sign_key = os.getenv("SIGN_KEY")

c_id = os.getenv("CL_ID")
c_sec = os.getenv("CL_SECRET")
redirect_url = "http://localhost:8501"

client = GoogleOAuth2(client_id=c_id, client_secret=c_sec)

async def get_access_token(client: GoogleOAuth2, redirect_url: str, code: str):
    return await client.get_access_token(code, redirect_url)

async def get_email(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email

def get_logged_in_user_email():
    try:
        query_params = st.query_params.to_dict()
        code = query_params.get('code')
        if code:
            token = asyncio.run(get_access_token(client, redirect_url, code))
            st.query_params.clear()

            if token:
                user_id, user_email = asyncio.run(get_email(client, token['access_token']))
                st.session_state.email = user_email
                return user_email
        return None
    except:
        pass

def show_login_button():
    authorization_url = asyncio.run(client.get_authorization_url(
        redirect_url,
        scope=["email", "profile"],
        extras_params={"access_type": "offline"},
    ))
    st.markdown(f'<a href="{authorization_url}" target="_self">Login</a>', unsafe_allow_html=True)
    get_logged_in_user_email()

def fetch_data():
    dummy_data = {
        "PH": random.uniform(6.5, 8.5),
        "TDS": random.uniform(0, 500),
        "Turbidity": random.uniform(0, 10),
        "Temperature": random.uniform(10, 50)
    }
    return dummy_data

def determine_drinkability(data):
    if data['PH'] < 6.5 or data['PH']> 8.5:
        return "Not Drinkable (pH out of range)"
    if data['Turbidity'] > 5:
        return "Not Drinkable (High Turbidity)"
    if data['TDS'] > 500:
        return "Not Drinkable (High TDS)"
    if data['Temperature'] < 10 or data['Temperature'] > 50:
        return "Not Ideal but may be Drinkable"
    
    return "Drinkable"

def get_suggestion(data):
    model = gen.GenerativeModel('gemini-2.0-flash')
    try:
        prompt = f'''
        Given the following water quality parameters:
        PH: {data['PH']} 
        TDS: {data['TDS']}ppm
        Turbidity: {voltage_to_ntu(data['Turbidity'])}NTU
        Temperature: {data['Temperature']}°C   these are the values measured by the ph,tds,turbidiy,temperature sensors from arduino, so please go through the values in such a way!
        Please provide a suggestion on how to improve the water quality. keep your responses not more than 250 words and keep it simple. Only give the necessary sugession, don't tell anyother things please
        '''
        res = model.generate_content(prompt).text
    except Exception as e:
        res = f"Error: {e}"
    
    return res

def voltage_to_ntu(voltage):
    """
    Convert voltage readings from turbidity sensor to NTU values.
    Voltage range: 0-3.2V
    
    For most turbidity sensors:
    - Higher voltage (≈3.2V) = Clear water (0 NTU)
    - Lower voltage (≈0V) = Very turbid water (3000+ NTU)
    """
    # Simpler linear conversion based on common turbidity sensor behavior
    if voltage >= 3.0:
        ntu=  0.5  # Clear water
    elif voltage <= 0.5:
        ntu= 3000  # Maximum turbidity
    else:
        # Linear mapping from voltage to NTU
        # Map voltage range [0.5, 3.0] to NTU range [3000, 0]
        ntu = 3000 * (3.0 - voltage) / 2.5
        
    print("v:", voltage)
    print("ntu:", ntu)
    
    return ntu
    

def app():
    st.title('Welcome!')
    
    # Check if we need to log in
    if not st.session_state.email:
        get_logged_in_user_email()
        if not st.session_state.email:
            show_login_button()
            return  # Stop execution here if not logged in

    # User is logged in
    st.write(f"Logged in as: {st.session_state.email}")
    
    # Create a container for the data display
    data_container = st.container()
    
    # Fetch initial data
    # data = fetch_data()
    while(True):    
        data = esp_py.get_data()
        if not data:
            data = esp_py.get_data()
        else:
            break
    
    # Refresh button
    if st.button("Refresh Data"):
        # data = fetch_data()  # Just update the data
        while(True):    
            data = esp_py.get_data()
            if not data:
                data = esp_py.get_data()
            else:
                break
    
    # Display data in the container
    with data_container:
        # data["Turbidity"]
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**PH:** {data['PH']}")
            st.write(f"**TDS:** {float(data['TDS'])}")
        with col2:
            st.write(f"*Turbidity:* {voltage_to_ntu(data['Turbidity'])}")
            st.write(f"**Temperature:** {data['Temperature']}")
        
        drinkable_status = determine_drinkability(data)
        st.write(f"**Drinkability:** {drinkable_status}")
        st.markdown('---')
        st.subheader("Suggestions!")
        if st.button("Get Gemini Suggestion"):
            with st.spinner("Thinking..."):
                analysis = get_suggestion(data)
                st.markdown(analysis)

        st.markdown("<br><br>",unsafe_allow_html=True)

    
    # Logout button
    if st.button("Logout", type="primary", key="logout_non_required"):
        st.session_state.email = ''
        st.rerun()

app()