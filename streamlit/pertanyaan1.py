import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from load_data import df_posting, df_skills, df_salaries, df_job_skills, df_job_industries, df_industries 

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Job Skills & Salary Dashboard", layout="wide")

# --- 1. FUNGSI LOAD DATA (DI-CACHE) ---
@st.cache_data
def load_data():
    # Load semua dataframe dari URL yang Anda sediakan
    
    df_p = df_posting
    df_s = df_skills
    df_sal = df_salaries
    df_js = df_job_skills
    df_ji = df_job_industries
    df_i = df_industries

    # Proses Merging (Sesuai logika EDA Anda)
    df = df_p.merge(df_js, on='job_posting_id', how='left')
    df = df.merge(df_s, on='skill_id', how='left')
    df = df.merge(df_ji, on='job_posting_id', how='left')
    df = df.merge(df_i, on='industry_id', how='left')
    df = df.merge(df_sal[['job_posting_id', 'min_salary', 'max_salary', 'med_salary']], 
                  on='job_posting_id', how='left')
    
    # Cleaning dasar
    df = df.dropna(subset=['skill_name'])
    return df

# --- 2. FUNGSI VISUALISASI ---

def plot_experience_heatmap(df, top_n_skills):
    top_skills = df['skill_name'].value_counts().nlargest(top_n_skills).index
    df_filtered = df[df['skill_name'].isin(top_skills)]
    pivot_exp = pd.crosstab(df_filtered['skill_name'], df_filtered['formatted_experience_level'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_exp, annot=True, fmt="d", cmap="YlGnBu", ax=ax)
    ax.set_title(f'Top {top_n_skills} Skills vs Level Pengalaman')
    return fig

def plot_industry_analysis(df, selected_industries):
    df_ind = df[df['industry_name'].isin(selected_industries)]
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Ambil top 10 skill untuk industri terpilih
    top_skills_ind = df_ind['skill_name'].value_counts().nlargest(10).reset_index()
    top_skills_ind.columns = ['skill_name', 'count']
    
    sns.barplot(data=top_skills_ind, x='count', y='skill_name', palette="viridis", ax=ax)
    ax.set_title(f'Top Skills di Industri Terpilih')
    return fig

def plot_salary_correlation(df):
    skill_salary = df.groupby('skill_name').agg(
        demand_count=('skill_name', 'count'),
        avg_med_salary=('med_salary', 'median')
    ).reset_index().dropna()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.regplot(data=skill_salary, x='demand_count', y='avg_med_salary', 
                scatter_kws={'alpha':0.5}, line_kws={'color':'red'}, ax=ax)
    
    # Anotasi top 5 salary
    top_5 = skill_salary.nlargest(5, 'avg_med_salary')
    for i, row in top_5.iterrows():
        ax.text(row['demand_count'], row['avg_med_salary'], row['skill_name'], color='darkred', weight='bold')
        
    ax.set_title('Korelasi: Permintaan Skill vs Estimasi Gaji')
    return fig

# --- 3. MAIN DASHBOARD ---

def visualisasi_pertanyaan():
    st.title("📊 Job Market & Skill Dashboard")
    st.markdown("Analisis hubungan antara Skill, Industri, Pengalaman, dan Gaji.")

    # Load Data
    with st.spinner('Memuat data...'):
        df = load_data()

    # --- SIDEBAR (INPUT VARIABLE) ---
    with st.sidebar:

        # Slider untuk jumlah skill yang ditampilkan
        top_n = st.slider("Tampilkan Top N Skill", 5, 30, 15)
        
        # Multiselect Industri
        all_industries = sorted(df['industry_name'].dropna().unique())
        selected_industries = st.multiselect(
            "Pilih Industri", 
            options=all_industries, 
            default=all_industries[:3]
        )

        # Filter Tipe Pekerjaan
        all_work_types = df['formatted_work_type'].unique()
        selected_work_types = st.multiselect(
            "Pilih Tipe Pekerjaan", 
            options=all_work_types, 
            default=all_work_types
        )

    # Apply Filter ke Dataframe Utama
    df_filtered = df[df['formatted_work_type'].isin(selected_work_types)]

    # --- LAYOUT UTAMA ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribusi Skill & Pengalaman")
        fig1 = plot_experience_heatmap(df_filtered, top_n)
        st.pyplot(fig1)

    with col2:
        st.subheader("Skill Terpopuler per Industri")
        if selected_industries:
            fig2 = plot_industry_analysis(df_filtered, selected_industries)
            st.pyplot(fig2)
        else:
            st.warning("Silakan pilih minimal satu industri di sidebar.")

    st.divider()

    col3, col4 = st.columns([2, 1])

    with col3:
        st.subheader("Analisis Korelasi Gaji")
        fig3 = plot_salary_correlation(df_filtered)
        st.pyplot(fig3)

    with col4:
        st.subheader("Statistik Ringkas")
        # Hitung korelasi
        skill_salary_analysis = df_filtered.groupby('skill_name').agg(
            demand_count=('skill_name', 'count'),
            avg_med_salary=('med_salary', 'median')
        ).reset_index().dropna()
        
        corr_value = skill_salary_analysis['demand_count'].corr(skill_salary_analysis['avg_med_salary'])
        
        st.metric("Total Lowongan", len(df_filtered['job_posting_id'].unique()))
        st.metric("Korelasi Demand vs Gaji", f"{corr_value:.4f}")
        
        st.write("**Top 5 Gaji Tertinggi per Skill:**")
        st.table(skill_salary_analysis.nlargest(5, 'avg_med_salary')[['skill_name', 'avg_med_salary']])