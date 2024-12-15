import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

def get_sample_data():
    data = {
        "Agency": ["EPA", "CDC", "FEMA", "HUD", "DOE"],
        "Metric": ["Pollution Levels", "Disease Cases", "Disaster Relief", "Housing Units", "Energy Consumption"],
        "Year": [2022, 2023, 2023, 2022, 2023],
        "Value": [45, 1200, 300, 5000, 320],
    }
    return pd.DataFrame(data)

def fetch_data(api_url, params={}):
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()
        return pd.json_normalize(data)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

def consolidate_data(data_frames):
    if len(data_frames) > 1:
        return pd.concat(data_frames, ignore_index=True)
    elif len(data_frames) == 1:
        return data_frames[0]
    else:
        return pd.DataFrame()

def generate_summary(data):
    summary = data.describe(include='all').transpose()
    return summary

def create_plot(data, x_col, y_col, title):
    fig, ax = plt.subplots()
    ax.bar(data[x_col], data[y_col], color='skyblue')
    ax.set_title(title)
    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)
    plt.xticks(rotation=45)
    st.pyplot(fig)

st.title("Federal Data Consolidator for Kajabi Integration")
st.write("Consolidate public data from federal agencies and prepare it for Kajabi.")

st.subheader("Step 1: View Sample Data")
if st.checkbox("Show Sample Data"):
    sample_data = get_sample_data()
    st.write("Sample Data for Testing:")
    st.dataframe(sample_data)
    st.write("Summary of Sample Data:")
    st.write(generate_summary(sample_data))

st.subheader("Step 2: Input API URLs for Real Data")
api_urls = st.text_area("Enter API URLs (one per line):")

if st.button("Fetch Data"):
    if api_urls.strip():
        urls = api_urls.split("\n")
        data_frames = []
        for url in urls:
            st.write(f"Fetching data from: {url}")
            data = fetch_data(url.strip())
            if not data.empty:
                data_frames.append(data)
                st.success(f"Data fetched successfully from {url}.")
            else:
                st.warning(f"No data found at {url}.")
        consolidated_data = consolidate_data(data_frames)

        if not consolidated_data.empty:
            st.subheader("Consolidated Data")
            st.dataframe(consolidated_data)

            st.write("Summary of Consolidated Data:")
            st.write(generate_summary(consolidated_data))

            st.subheader("Data Visualization")
            if len(consolidated_data.columns) >= 2:
                x_col = st.selectbox("Select X-axis column", consolidated_data.columns)
                y_col = st.selectbox("Select Y-axis column", consolidated_data.columns)
                create_plot(consolidated_data, x_col, y_col, "Consolidated Data Visualization")

            csv = consolidated_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Consolidated Data as CSV",
                data=csv,
                file_name="consolidated_data.csv",
                mime="text/csv",
            )
        else:
            st.warning("No data to consolidate.")
    else:
        st.error("Please input at least one API URL.")
