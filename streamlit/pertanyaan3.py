import streamlit as st
import pandas as pd
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from itertools import combinations
import warnings
from load_data import df_posting, df_skills, df_salaries, df_job_skills



warnings.filterwarnings('ignore')

# Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Job Skills & Market Analysis", layout="wide")
sns.set_style("whitegrid")

# ================================================================================
# 1. DATA LOADING & PREPROCESSING (CACHED)
# ================================================================================
@st.cache_data
def load_and_prep_data():
    # Load datasets
    df_posting
    df_skills
    df_salaries
    df_job_skills
    
    # Cleaning
    time_cols_posting = ['original_listed_time', 'expiry', 'closed_time', 'listed_time']
    for col in time_cols_posting:
        df_posting[col] = pd.to_datetime(df_posting[col], unit='ms', errors='coerce')
        
    df_posting['company_id'] = df_posting['company_id'].astype('Int64')
    text_cols_posting = ['job_description', 'formatted_experience_level', 'skills_desc', 'posting_domain', 'application_url']
    for col in text_cols_posting:
        df_posting[col] = df_posting[col].fillna('Unknown')
        
    df_posting['remote_allowed'] = df_posting['remote_allowed'].fillna(0).astype('Int64')
    
    df_salaries['med_salary_est'] = df_salaries['med_salary'].fillna(
        (df_salaries['min_salary'] + df_salaries['max_salary']) / 2
    )
    
    # Merging
    df_job_skills_merged = df_job_skills.merge(df_skills, on='skill_id', how='left')
    df_analysis = df_job_skills_merged.merge(
        df_posting[['job_posting_id', 'title', 'views', 'applies', 'original_listed_time', 
                    'expiry', 'closed_time', 'formatted_experience_level', 'remote_allowed', 
                    'formatted_work_type']],
        on='job_posting_id',
        how='left'
    )
    df_analysis = df_analysis.merge(
        df_salaries[['job_posting_id', 'med_salary_est', 'min_salary', 'max_salary', 'pay_period']],
        on='job_posting_id',
        how='left'
    )
    
    # Feature Engineering Target Variables
    salary_threshold = df_analysis['med_salary_est'].quantile(0.75)
    df_analysis['high_salary'] = (df_analysis['med_salary_est'] >= salary_threshold).astype(int)
    
    df_analysis['listing_duration'] = (df_analysis['closed_time'] - df_analysis['original_listed_time']).dt.days
    df_with_closure = df_analysis[df_analysis['closed_time'].notna()].copy()
    closure_threshold = df_with_closure['listing_duration'].quantile(0.25)
    df_analysis['quick_closure'] = df_analysis['listing_duration'].apply(
        lambda x: 1 if pd.notna(x) and x <= closure_threshold else 0
    )
    
    return df_analysis, df_with_closure, salary_threshold, closure_threshold



def visualisasi_pertanyaan():
    df_analysis, df_with_closure, salary_threshold, closure_threshold = load_and_prep_data()

    # ================================================================================
    # 2. SIDEBAR & INTERACTIVITY
    # ================================================================================

    # Filter Pengalaman
    exp_levels = df_analysis['formatted_experience_level'].unique()
    selected_exp = st.sidebar.multiselect("Experience Level", exp_levels, default=exp_levels)

    # Filter Remote
    is_remote = st.sidebar.checkbox("Show Remote Jobs Only", value=False)

    # Filter Top N
    top_n = st.sidebar.slider("Number of Top Skills/Pairs to show", min_value=5, max_value=30, value=15)

    # Apply filters
    filtered_df = df_analysis[df_analysis['formatted_experience_level'].isin(selected_exp)]
    if is_remote:
        filtered_df = filtered_df[filtered_df['remote_allowed'] == 1]

    # Re-calculate job_skills_dict based on filtered data
    job_skills_dict = filtered_df.groupby('job_posting_id')['skill_name'].apply(list).to_dict()

    # ================================================================================
    # 3. DASHBOARD MAIN CONTENT
    # ================================================================================
    st.title("📊 Job Market & Skills Analytics Dashboard")
    st.markdown("Dashboard interaktif berdasarkan postingan lowongan kerja, gaji, dan analisis *co-occurrence* keahlian (skills).")

    # Metric Summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Job Postings", f"{filtered_df['job_posting_id'].nunique():,}")
    col2.metric("Total Unique Skills", f"{filtered_df['skill_name'].nunique():,}")
    col3.metric("High Salary Threshold", f"${salary_threshold:,.0f}")
    col4.metric("Quick Closure Threshold", f"{closure_threshold:.0f} days")

    st.divider()

    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Skill Distribution", "🔗 Skill Networks", "💰 Salary Insights", "⚡ Closure Insights"])

    # ----------------- TAB 1: SKILL DISTRIBUTION -----------------
    with tab1:
        st.header("Distribui Skill & Kebutuhan Loker")
        
        c1, c2 = st.columns(2)
        with c1:
            # Skill counts
            skill_counts = filtered_df['skill_name'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 6))
            skill_counts.head(top_n).plot(kind='barh', ax=ax, color='steelblue')
            ax.set_xlabel('Frequency')
            ax.set_title(f'Top {top_n} Most Common Skills', fontweight='bold')
            ax.invert_yaxis()
            st.pyplot(fig)
            plt.close()
            
        with c2:
            # Skills per job
            skills_per_job = filtered_df.groupby('job_posting_id')['skill_name'].nunique()
            fig, ax = plt.subplots(figsize=(10, 6))
            skills_per_job.value_counts().sort_index().plot(kind='bar', ax=ax, color='skyblue')
            ax.set_xlabel('Number of Skills Required')
            ax.set_ylabel('Frequency')
            ax.set_title('Distribution of Skills Count per Job', fontweight='bold')
            st.pyplot(fig)
            plt.close()

    # ----------------- TAB 2: SKILL NETWORKS -----------------
    with tab2:
        st.header("Co-occurrence & Skill Networks")
        st.markdown("Menganalisis skill apa saja yang sering diminta secara bersamaan oleh perusahaan.")
        
        # Hitung Skill Pairs
        skill_pairs = Counter()
        for job_id, skills in job_skills_dict.items():
            if len(skills) >= 2:
                pairs = combinations(sorted(set(skills)), 2)
                for pair in pairs:
                    skill_pairs[pair] += 1
                    
        top_skill_pairs = skill_pairs.most_common(top_n)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            # Bar chart skill pairs
            pair_names = [f"{p[0]}+\n{p[1]}" for p, _ in top_skill_pairs]
            pair_counts = [count for _, count in top_skill_pairs]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.barh(range(len(pair_names)), pair_counts, color='teal')
            ax.set_yticks(range(len(pair_names)))
            ax.set_yticklabels(pair_names, fontsize=9)
            ax.set_title(f'Top {top_n} Skill Pair Co-occurrences', fontweight='bold')
            ax.invert_yaxis()
            st.pyplot(fig)
            plt.close()
            
        with c2:
            # Network Graph
            G = nx.Graph()
            for (skill1, skill2), count in top_skill_pairs:
                G.add_edge(skill1, skill2, weight=count)
                
            fig, ax = plt.subplots(figsize=(10, 8))
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=1500, ax=ax, alpha=0.9)
            
            edges = G.edges()
            weights = [G[u][v]['weight'] for u, v in edges]
            max_weight = max(weights) if weights else 1
            edge_widths = [3 * (w / max_weight) for w in weights]
            
            nx.draw_networkx_edges(G, pos, width=edge_widths, ax=ax, alpha=0.6, edge_color='gray')
            nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold', ax=ax)
            ax.set_title('Skill Co-occurrence Network', fontweight='bold')
            ax.axis('off')
            st.pyplot(fig)
            plt.close()

    # ----------------- TAB 3: SALARY INSIGHTS -----------------
    with tab3:
        st.header("Skill & Gaji Tinggi (High Salary)")
        df_for_salary = filtered_df[filtered_df['med_salary_est'].notna()].copy()
        
        c1, c2 = st.columns(2)
        with c1:
            # Avg Salary per Skill
            skill_salary_stats = df_for_salary.groupby('skill_name').agg({
                'med_salary_est': ['mean', 'count']
            })
            skill_salary_stats.columns = ['mean_salary', 'count']
            skill_salary_stats = skill_salary_stats[skill_salary_stats['count'] >= 5].sort_values('mean_salary', ascending=False)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            skill_salary_stats.head(top_n)['mean_salary'].plot(kind='barh', ax=ax, color='orange')
            ax.set_xlabel('Average Salary (USD)')
            ax.set_title(f'Top {top_n} Skills with Highest Average Salaries', fontweight='bold')
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
            ax.invert_yaxis()
            st.pyplot(fig)
            plt.close()

        with c2:
            # Skill Pairs vs High Salary
            salary_map = dict(zip(df_for_salary['job_posting_id'], df_for_salary['high_salary']))
            pair_salary_stats = {}
            
            for pair, count in top_skill_pairs:
                high_salary_count = sum(1 for job_id, skills in job_skills_dict.items() 
                                        if pair[0] in skills and pair[1] in skills and salary_map.get(job_id) == 1)
                total_count = sum(1 for job_id, skills in job_skills_dict.items() 
                                if pair[0] in skills and pair[1] in skills)
                
                if total_count > 0:
                    pair_salary_stats[pair] = high_salary_count / total_count
                    
            sorted_pairs_salary = sorted(pair_salary_stats.items(), key=lambda x: x[1], reverse=True)[:top_n]
            pair_labels = [f"{p[0]}+\n{p[1]}" for p, _ in sorted_pairs_salary]
            rates = [r * 100 for _, r in sorted_pairs_salary]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(range(len(pair_labels)), rates, color='darkgreen')
            ax.set_yticks(range(len(pair_labels)))
            ax.set_yticklabels(pair_labels, fontsize=9)
            ax.set_xlabel('High-Salary Rate (%)')
            ax.set_title('Top Skill Pairs Associated with High Salaries', fontweight='bold')
            ax.set_xlim([0, 100])
            ax.invert_yaxis()
            st.pyplot(fig)
            plt.close()

    # ----------------- TAB 4: CLOSURE INSIGHTS -----------------
    with tab4:
        st.header("Skill & Penutupan Loker Cepat (Quick Closure)")
        
        closure_map = dict(zip(filtered_df['job_posting_id'], filtered_df['quick_closure']))
        pair_closure_stats = {}
        
        for pair, count in top_skill_pairs:
            quick_closure_count = sum(1 for job_id, skills in job_skills_dict.items() 
                                    if pair[0] in skills and pair[1] in skills and closure_map.get(job_id) == 1)
            total_count = sum(1 for job_id, skills in job_skills_dict.items() 
                            if pair[0] in skills and pair[1] in skills)
            
            if total_count > 0:
                pair_closure_stats[pair] = quick_closure_count / total_count
                
        sorted_pairs_closure = sorted(pair_closure_stats.items(), key=lambda x: x[1], reverse=True)[:top_n]
        pair_labels_c = [f"{p[0]}+\n{p[1]}" for p, _ in sorted_pairs_closure]
        rates_c = [r * 100 for _, r in sorted_pairs_closure]
        
        c1, c2 = st.columns(2)
        with c1:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(range(len(pair_labels_c)), rates_c, color='darkred')
            ax.set_yticks(range(len(pair_labels_c)))
            ax.set_yticklabels(pair_labels_c, fontsize=9)
            ax.set_xlabel('Quick-Closure Rate (%)')
            ax.set_title('Top Skill Pairs Associated with Quick Job Closure', fontweight='bold')
            ax.set_xlim([0, 100])
            ax.invert_yaxis()
            st.pyplot(fig)
            plt.close()
            
        with c2:
            st.markdown("""
            ### 📌 Key Insights (Berdasarkan Data yang Difilter):
            Kombinasi skill (*skill pairs*) di sebelah kiri mengindikasikan bahwa lowongan tersebut cenderung **ditutup lebih cepat** (berada pada presentil ke-25 waktu listing terpendek).
            
            Ini bisa berarti:
            1. **Kandidat mudah ditemukan:** Pasokan talent dengan kombinasi ini sangat berlimpah.
            2. **Permintaan tinggi/Mendesak:** Perusahaan agresif dalam proses rekrutmen dan segera menutup lowongan setelah kandidat didapat.
            """)