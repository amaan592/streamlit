import streamlit as st
import pandas as pd
import os
from io import BytesIO
from fpdf import FPDF

# Configure the Streamlit app's appearance and layout
st.set_page_config(page_title="Data Sweeper", layout="wide")

# Custom CSS for styling the app with dynamic colors
st.markdown(
    """
    <style>
        .main {
            background-color: #121212;
        }
        .block-container {
            padding: 3rem 2rem;
            border-radius: 12px;
            background-color:rgb(28, 167, 167);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.18);
        }
        h1, h2, h3, h4, h5, h6 {
            color: #66c2ff;
        }
        .stButton>button {
            border: none;
            border-radius: 8px;
            background-color: #0078D7;
            color: white;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
        }
        .stButton>button:hover {
            background-color: #005a9e;
            cursor: pointer;
        }
        .stDataFrame, .stTable {
            border-radius: 10px;
            overflow: hidden;
        }
        .css-1aumxhk, .css-18e3th9 {
            text-align: left;
            color: #ffffff;
        }
        .stRadio>label {
            font-weight: bold;
            color: #ff66c2;
        }
        .stCheckbox>label {
            color:rgb(255, 102, 138);
        }
        .stDownloadButton>button {
            background-color: #ff5733;
            color: white;
        }
        .stDownloadButton>button:hover {
            background-color: #c70039;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the main app title and introductory text
st.title("Advanced Data Sweeper")
st.write("Transform your files between CSV, Excel, and PDF formats with built-in data cleaning and visualization.")

# File uploader widget that accepts CSV, Excel, and PDF files
uploaded_files = st.file_uploader("Upload your files (CSV, Excel, or PDF):", type=["csv", "pdf", "xlsx"], accept_multiple_files=True)

# Processing logic for uploaded files (if any files are uploaded)
if uploaded_files:
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[-1].lower()
        
        if file_extension == ".csv":
            df = pd.read_csv(file)
        elif file_extension == ".xlsx":
            df = pd.read_excel(file)
        else:
            st.error(f"Unsupported file type: {file_extension}")
            continue
        
        st.write(f"**📄 File Name:** {file.name}")
        st.write(f"**📏 File Size:** {file.size / 1024:.2f} KB")

        st.write("🔍 Preview of the Uploaded File:")
        st.dataframe(df.head())
        
        st.subheader("🛠️ Data Cleaning Options")
        if st.checkbox(f"Clean Data for {file.name}"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Remove Duplicates from {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")
            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values in Numeric Columns Filled with Column Means!")

        st.subheader("🎯 Select Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]
        
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include='number').iloc[:, :2])
        
        st.subheader("🔄 Conversion Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel", "PDF"], key=file.name)
        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_extension, ".csv")
                mime_type = "text/csv"
            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine='openpyxl')
                file_name = file.name.replace(file_extension, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif conversion_type == "PDF":
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for i in range(len(df)):
                    row = df.iloc[i]
                    pdf.cell(200, 10, txt=str(row.values), ln=True)
                buffer = BytesIO(pdf.output(dest='S').encode('latin1'))
                file_name = file.name.replace(file_extension, ".pdf")
                mime_type = "application/pdf"
            buffer.seek(0)
            
            st.download_button(
                label=f"⬇️ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

st.success("🎉 Your files copmplete successfully!")