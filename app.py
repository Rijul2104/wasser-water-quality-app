
import streamlit as st
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64
import warnings

warnings.filterwarnings("ignore")

parameters = ["COD", "BOD", "DO", "TSS", "NO3", "Pathogens"]
st.set_page_config(page_title="Wasser - Water Quality Forecast", layout="wide")

# Session Setup
if "page" not in st.session_state:
    st.session_state.page = "cover"
if "data_ready" not in st.session_state:
    st.session_state.data_ready = False
if "data" not in st.session_state:
    st.session_state.data = {}
if "years" not in st.session_state:
    st.session_state.years = []

# Cover Page
if st.session_state.page == "cover":
    try:
        logo = Image.open("wasser_logo.png")
        st.image(logo, width=250)
    except:
        st.warning("Logo not found.")
    st.title("💧 Welcome to Wasser")
    st.subheader("AI-based Water Quality Prediction")
    st.markdown("Click below to start entering water quality data.")
    if st.button("▶️ Start Application"):
        st.session_state.page = "input"

# Input Page
elif st.session_state.page == "input":
    st.title("📥 Water Quality Data Entry")
    st.markdown("Enter at least 4 years of data to predict future values using ARIMA.")

    rows = st.number_input("How many years of data?", min_value=4, max_value=20, value=5, key="row_count")
    forecast_years = st.number_input("🔮 Years to Forecast", min_value=1, max_value=10, value=3, key="forecast_count")

    data = {param: [] for param in parameters}
    years = []

    with st.form("water_form"):
        for i in range(rows):
            cols = st.columns(len(parameters) + 1)
            year = cols[0].text_input(f"Year {i+1}", key=f"year_{i}")
            years.append(year)
            for j, param in enumerate(parameters):
                val = cols[j+1].number_input(f"{param} (Year {i+1})", key=f"{param}_{i}")
                data[param].append(val)
        submitted = st.form_submit_button("📈 Generate Forecast")

    if submitted:
        valid_years = []
        for y in years:
            if y.isdigit():
                valid_years.append(pd.to_datetime(str(int(y))))
            else:
                st.warning(f"⚠️ Invalid year: {y}")

        if len(valid_years) < 4:
            st.error("❌ Please enter at least 4 valid years.")
        else:
            st.session_state.page = "results"
            st.session_state.years = valid_years
            st.session_state.data = data
            st.session_state.forecast_years = forecast_years
            st.session_state.data_ready = True

# Results Page
elif st.session_state.page == "results":
    st.title("📊 Forecast Results")
    if not st.session_state.data_ready:
        st.warning("⚠️ No data available. Go back and enter values first.")
    else:
        df = pd.DataFrame(st.session_state.data, index=st.session_state.years)
        df.index.name = "Year"
        st.subheader("📄 Input Data")
        st.dataframe(df)

        last_year = df.index[-1].year
        all_forecasts = []

        for param in parameters:
            st.markdown(f"### 🔮 {param} Forecast")
            try:
                series = df[param]
                model = ARIMA(series, order=(1, 1, 1))
                model_fit = model.fit()
                forecast = model_fit.forecast(steps=st.session_state.forecast_years)

                pred_years = [last_year + i + 1 for i in range(st.session_state.forecast_years)]
                forecast.index = pred_years
                pred_df = pd.DataFrame({param: forecast})
                pred_df.index.name = "Year"
                all_forecasts.append(pred_df)

                # Plot
                fig, ax = plt.subplots()
                ax.plot(df.index.year, series, marker='o', label="Actual")
                ax.plot(pred_years, forecast, marker='x', linestyle='--', color='red', label="Forecast")
                ax.set_title(f"{param} Prediction")
                ax.set_xlabel("Year")
                ax.set_ylabel(param)
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)

                # Table
                st.dataframe(pred_df.style.format("{:.2f}"))

                st.markdown("---")
            except Exception as e:
                st.error(f"Error predicting {param}: {e}")

        # Download all results
        final_forecast = pd.concat(all_forecasts, axis=1)
        csv = final_forecast.to_csv().encode("utf-8")
        st.download_button("📥 Download All Forecasts (CSV)", data=csv, file_name="wasser_forecast.csv", mime="text/csv")

    if st.button("🔄 Back to Input"):
        st.session_state.page = "input"
