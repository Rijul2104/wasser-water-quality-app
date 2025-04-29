# water_quality_app_streamlit.py

import streamlit as st
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
from PIL import Image
import warnings

warnings.filterwarnings("ignore")

# Parameters
parameters = ["COD", "BOD", "DO", "TSS", "NO3", "Pathogens"]

# Title and Layout
st.set_page_config(page_title="Wasser - Water Quality Prediction", layout="centered")

# Session State to control navigation
if "page" not in st.session_state:
    st.session_state.page = "cover"

# Cover Page
if st.session_state.page == "cover":
    try:
        logo = Image.open("wasser_logo.png")  # Replace with actual path if needed
        st.image(logo, width=250)
    except FileNotFoundError:
        st.warning("Logo not found. Make sure 'wasser_logo.png' is in the same directory.")

    st.title("💧 Welcome to Wasser")
    st.subheader("AI-based Water Quality Prediction App")
    st.markdown("""
    This application allows you to input yearly water quality parameters and forecast future values 
    using ARIMA time series modeling. Click below to get started!
    """)

    if st.button("Start Application ▶️"):
        st.session_state.page = "main"

# Main Application Page
if st.session_state.page == "main":

    st.title("💧 Wasser - Water Quality Prediction")
    st.write("Enter the yearly water quality parameters below. Minimum 4 years required for prediction.")

    # Input table
    years = []
    data = {param: [] for param in parameters}

    rows = st.number_input("How many years of data do you want to enter?", min_value=4, max_value=20, value=5)

    with st.form("water_quality_form"):
        for i in range(rows):
            cols = st.columns(len(parameters) + 1)
            year = cols[0].text_input(f"Year {i+1}", key=f"year_{i}")
            years.append(year)
            for j, param in enumerate(parameters):
                val = cols[j+1].number_input(f"{param} (Year {i+1})", key=f"{param}_{i}")
                data[param].append(val)

        forecast_years = st.number_input("🔮 Years to Forecast", min_value=1, max_value=10, value=3)

        submitted = st.form_submit_button("Predict Water Quality 📈")

    if submitted:
        try:
            # Process Data
            years_clean = []
            for y in years:
                if y.isdigit():
                    years_clean.append(pd.to_datetime(str(int(y))))
                else:
                    st.warning(f"⚠️ Invalid year: {y}")

            if len(years_clean) < 4:
                st.error("❌ Please enter at least 4 valid years of data.")
            else:
                df = pd.DataFrame(data, index=years_clean)
                st.subheader("📄 Input Data:")
                st.dataframe(df)

                last_year = df.index[-1].year

                # Prediction Results
                for param in parameters:
                    st.subheader(f"🔮 {param} Predictions")
                    try:
                        series = df[param]
                        model = ARIMA(series, order=(1, 1, 1))
                        model_fit = model.fit()
                        forecast = model_fit.forecast(steps=forecast_years)

                        pred_years = [last_year + i + 1 for i in range(forecast_years)]
                        forecast.index = pred_years  # ✅ FIX: set index before DataFrame creation
                        pred_df = pd.DataFrame({param: forecast})
                        pred_df.index.name = 'Year'

                        st.table(pred_df)

                        # Plot
                        fig, ax = plt.subplots()
                        ax.plot(df.index.year, series, marker='o', label='Actual')
                        ax.plot(pred_years, forecast, marker='x', linestyle='--', color='red', label='Forecast')
                        ax.set_title(f"{param} Prediction")
                        ax.set_xlabel("Year")
                        ax.set_ylabel(param)
                        ax.legend()
                        st.pyplot(fig)

                    except Exception as e:
                        st.error(f"Error predicting {param}: {e}")
        except Exception as e:
            st.error(f"General Error: {e}")

