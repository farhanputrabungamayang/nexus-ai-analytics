# ✨ Nexus AI Data Intelligence 📊

An Enterprise-Grade Data Analytics & Visualization Dashboard powered by **Python, Streamlit, Pandas**, and **Google Gemini 1.5 Pro**.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini-orange.svg)

## 🚀 Key Features

* **🪄 Auto-Cleansing Magic:** Automatically remove duplicates and fill in missing values (`NaN`) with a single click.
* **🎛️ Smart Slicer:** Interactive sidebar filters that dynamically update metrics and visualizations in real-time.
* **📈 Advanced Visualization:** Generate Bar Charts, Line Charts, and Scatter Plots effortlessly using Plotly.
* **🤖 Executive AI Report:** Let Google Gemini analyze your dataset and generate professional business insights automatically.
* **📄 PDF Export:** Download the AI-generated executive report directly as a PDF for meetings.
* **💬 Chat with Data (RAG-lite):** Ask questions about your dataset in natural language and get instant analytical answers.

## 🛠️ Installation & Setup

1. Clone this repository:
   ```bash
   git clone [https://github.com/farhanputrabungamayang/nexus-ai-analytics.git](https://github.com/farhanputrabungamayang/nexus-ai-analytics.git)

2. Install the required dependencies:
   ```bash
   pip install streamlit pandas plotly openpyxl fpdf google-generativeai

3. Set up your Google Gemini API Key:
    Create a folder named .streamlit in the root directory.
    Inside it, create a file named secrets.toml.
    Add your API key:
        GOOGLE_API_KEY = "your-api-key-here"
4. Run the application:
   ```bash
   streamlit run app.py

📥 Testing the App
Don't have a dataset ready? No problem! Once you run the app, simply click the "Download Sample Data" button in the sidebar to get a ready-to-use CSV file equipped with intentional dummy errors to test the Auto-Cleansing feature!

Built with 😁 for Data Enthusiasts.