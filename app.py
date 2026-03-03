import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import io
from fpdf import FPDF
from datetime import datetime
import random

# --- 1. KONFIGURASI HALAMAN LUXURY ---
st.set_page_config(page_title="Nexus AI Analytics", page_icon="✨", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
        html, body, [class*="css"]  { font-family: 'Plus Jakarta Sans', sans-serif; }
        .stButton>button { border-radius: 12px; font-weight: 600; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.15); }
        div[data-testid="metric-container"] {
            background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
            backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px; padding: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.05);
        }
        .gradient-text {
            background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-weight: 800; font-size: 2.5rem; margin-bottom: 0px;
        }
        .subtitle { color: #888; font-size: 1.1rem; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. INISIALISASI AI & STATE ---
if "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model_hidup = next(m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods)
        ai_model = genai.GenerativeModel(model_hidup)
    except: ai_model = None
else: ai_model = None

if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "df" not in st.session_state: st.session_state.df = None
if "ai_report" not in st.session_state: st.session_state.ai_report = ""

# --- FUNGSI GENERATE DUMMY DATA ---
@st.cache_data
def generate_dummy_csv():
    cabang = ["Jakarta", "Bandung", "Surabaya", "Medan", "Bali"]
    produk = ["Laptop", "Smartphone", "Tablet", "Monitor", "Keyboard"]
    data = []
    for i in range(100):
        data.append([f"2023-10-{random.randint(1,30):02d}", random.choice(cabang), random.choice(produk), random.randint(5, 50), random.randint(1000000, 15000000)])
    df_dummy = pd.DataFrame(data, columns=["Tanggal", "Cabang", "Produk", "Qty_Terjual", "Pendapatan"])
    # Sengaja dikotorin buat demo Auto-Cleanse
    df_dummy.loc[5, 'Cabang'] = None 
    df_dummy.loc[12, 'Qty_Terjual'] = None
    df_dummy = pd.concat([df_dummy, df_dummy.iloc[[0, 1, 2]]]) # Tambah duplikat
    return df_dummy.to_csv(index=False).encode('utf-8')

def generate_pdf_report(report_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="NEXUS AI - EXECUTIVE DATA REPORT", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    clean_text = report_text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=clean_text)
    return pdf.output(dest='S').encode('latin1')

# --- 3. HEADER UI ---
st.markdown('<p class="gradient-text">✨ Nexus AI Data Intelligence</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Platform Analisis Data Enterprise Berbasis Generative AI</p>', unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 📥 Belum Punya Data?")
    st.download_button(label="📄 Download Sample Data", data=generate_dummy_csv(), file_name="Sample_Sales_Data.csv", mime="text/csv", type="secondary", use_container_width=True)
    st.caption("Gunakan file ini untuk mencoba fitur aplikasi.")
    st.markdown("---")

    st.markdown("### 📁 1. Data Ingestion")
    uploaded_file = st.file_uploader("Unggah dataset (CSV/Excel)", type=['csv', 'xlsx'])
    
    if uploaded_file and st.session_state.df is None:
        if uploaded_file.name.endswith('.csv'): st.session_state.df = pd.read_csv(uploaded_file)
        else: st.session_state.df = pd.read_excel(uploaded_file)
        st.success("Data berhasil dimuat!")
        st.rerun()
        
    if st.session_state.df is not None:
        df = st.session_state.df
        
        st.markdown("---")
        st.markdown("### 🧹 2. Data Cleansing")
        if st.button("✨ Auto-Cleanse Data", use_container_width=True):
            initial_rows = df.shape[0]
            df = df.drop_duplicates()
            df = df.fillna(method='ffill').fillna(method='bfill')
            st.session_state.df = df
            st.success(f"Dibersihkan! Dari {initial_rows} jadi {df.shape[0]} baris.")
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 🎛️ 3. Smart Slicer")
        cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if cat_cols:
            filter_col = st.selectbox("Filter Berdasarkan Kolom:", ["Tanpa Filter"] + cat_cols)
            if filter_col != "Tanpa Filter":
                unique_vals = df[filter_col].dropna().unique().tolist()
                selected_vals = st.multiselect("Pilih Nilai:", unique_vals, default=unique_vals[:5])
                if selected_vals: df = df[df[filter_col].isin(selected_vals)] 

        if st.button("🗑️ Reset Data", type="secondary"):
            st.session_state.df = None
            st.session_state.chat_history = []
            st.session_state.ai_report = ""
            st.rerun()

# --- 5. MAIN LOGIC & LAYOUT ---
if st.session_state.df is not None:
    display_df = df 
    
    st.markdown("### 📊 Dataset Overview (Real-time)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Baris Aktif", f"{display_df.shape[0]:,}")
    m2.metric("Total Kolom", f"{display_df.shape[1]}")
    m3.metric("Data Kosong (Missing)", f"{display_df.isnull().sum().sum()}")
    m4.metric("Duplikat", f"{display_df.duplicated().sum()}")
    st.markdown("<br>", unsafe_allow_html=True)

    tab_data, tab_viz, tab_ai = st.tabs(["🗂️ Data Explorer", "📈 Advanced Visualization", "🤖 Executive AI Report"])
    
    with tab_data:
        st.subheader("Cuplikan Data")
        st.dataframe(display_df.head(100), use_container_width=True)
        st.subheader("Statistik Deskriptif")
        st.write(display_df.describe())
            
    with tab_viz:
        st.subheader("Bikin Grafik Interaktif")
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)
            with col1: chart_type = st.selectbox("Jenis Visualisasi", ["Bar Chart", "Line Chart", "Scatter Plot"])
            with col2: x_axis = st.selectbox("Sumbu X (Label)", display_df.columns)
            with col3: y_axis = st.selectbox("Sumbu Y (Nilai)", display_df.columns)
                
            if st.button("✨ Generate Visualization", type="primary"):
                try:
                    if chart_type == "Bar Chart": fig = px.bar(display_df, x=x_axis, y=y_axis, color=x_axis, template="plotly_dark")
                    elif chart_type == "Line Chart": fig = px.line(display_df, x=x_axis, y=y_axis, template="plotly_dark")
                    else: fig = px.scatter(display_df, x=x_axis, y=y_axis, color=x_axis, template="plotly_dark")
                    
                    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig, use_container_width=True)
                except: st.error("⚠️ Tipe data tidak sesuai untuk grafik ini. Coba ganti Sumbu X/Y!")

    with tab_ai:
        col_ai1, col_ai2 = st.columns([3, 1])
        with col_ai1: st.subheader("🤖 AI Executive Summary")
        with col_ai2:
            if st.button("🚀 Generate Analisa Otomatis", use_container_width=True, type="primary"):
                if ai_model:
                    with st.spinner("AI sedang membedah data Anda..."):
                        context = f"Analisa data ini:\nKolom: {display_df.columns.tolist()}\nStatistik:\n{display_df.describe().to_markdown()}\nBerikan 3 insight utama dan 1 rekomendasi bisnis secara profesional."
                        try:
                            res = ai_model.generate_content(context)
                            st.session_state.ai_report = res.text
                        except: st.error("Gagal konek ke AI.")
        
        if st.session_state.ai_report:
            st.info(st.session_state.ai_report)
            pdf_data = generate_pdf_report(st.session_state.ai_report)
            st.download_button("⬇️ Download Report (PDF)", data=pdf_data, file_name="Nexus_AI_Report.pdf", mime="application/pdf", type="secondary")

        st.markdown("---")
        st.subheader("💬 Ngobrol dengan Data Anda (Chatbot)")
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        user_q = st.chat_input("Tanyakan sesuatu ke AI (Misal: 'Berapa rata-rata pendapatan?')")
        if user_q and ai_model:
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.chat_message("user"): st.markdown(user_q)
            with st.chat_message("assistant"):
                with st.spinner("Mencari jawaban dari data..."):
                    ctx = f"Data stats:\n{display_df.describe().to_markdown()}\n\nPertanyaan User: {user_q}\nJawablah dengan analitis."
                    reply = ai_model.generate_content(ctx).text
                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
else:
    st.info("👈 Silakan unggah dataset Anda melalui panel di sebelah kiri untuk memulai sesi analitik.")