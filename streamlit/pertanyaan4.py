import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from load_data import df_posting, df_skills, df_salaries, df_job_skills, df_job_industries, df_industries, df_companies



def visualisasi_pertanyaan():
    # ─────────────────────────────────────────────
    # PAGE CONFIG
    # ─────────────────────────────────────────────
    st.set_page_config(
        page_title="Kompensasi Kerja Dashboard",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ─────────────────────────────────────────────
    # CUSTOM CSS
    # ─────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;700&display=swap');

    :root {
        --bg: #0b0f1a;
        --surface: #141927;
        --border: #1e2a40;
        --accent: #00e5ff;
        --accent2: #ff4f7b;
        --accent3: #ffe066;
        --text: #e8edf5;
        --muted: #7a8aaa;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--bg);
        color: var(--text);
    }

    .stApp { background-color: var(--bg); }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] * { color: var(--text) !important; }

    /* Metric cards */
    .metric-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 3px; height: 100%;
        background: var(--accent);
    }
    .metric-label {
        font-family: 'Space Mono', monospace;
        font-size: 11px;
        letter-spacing: 2px;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .metric-value {
        font-family: 'Space Mono', monospace;
        font-size: 28px;
        font-weight: 700;
        color: var(--accent);
        line-height: 1;
    }
    .metric-sub {
        font-size: 12px;
        color: var(--muted);
        margin-top: 4px;
    }

    /* Section headers */
    .section-header {
        font-family: 'Space Mono', monospace;
        font-size: 13px;
        letter-spacing: 3px;
        color: var(--accent);
        text-transform: uppercase;
        margin: 32px 0 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border);
    }

    /* Hero header */
    .hero {
        padding: 32px 0 24px;
        margin-bottom: 8px;
    }
    .hero h1 {
        font-family: 'Space Mono', monospace;
        font-size: 32px;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 6px;
        line-height: 1.2;
    }
    .hero h1 span { color: var(--accent); }
    .hero p { color: var(--muted); font-size: 14px; margin: 0; }

    /* Filter tags */
    .stSelectbox > div > div, .stMultiSelect > div > div {
        background: var(--surface) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
    }
    .stSlider > div { color: var(--text) !important; }

    /* Chart containers */
    .chart-box {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .chart-title {
        font-family: 'Space Mono', monospace;
        font-size: 12px;
        letter-spacing: 1.5px;
        color: var(--muted);
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .chart-subtitle {
        font-size: 18px;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 16px;
    }

    hr { border-color: var(--border); margin: 24px 0; }

    .badge {
        display: inline-block;
        background: rgba(0,229,255,0.1);
        color: var(--accent);
        border: 1px solid rgba(0,229,255,0.3);
        border-radius: 20px;
        font-family: 'Space Mono', monospace;
        font-size: 10px;
        letter-spacing: 1px;
        padding: 2px 10px;
        margin-right: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # DATA LOADING & PREPROCESSING
    # ─────────────────────────────────────────────
    @st.cache_data
    def load_and_process_data():
        try:
            df_posting
            df_skills
            df_salaries
            df_job_skills
            df_job_industries
            df_industries
            df_companies

            # Merge pipeline
            df_salary_clean = df_salaries.dropna(subset=['med_salary']).copy()
            df_eda = df_salary_clean.merge(
                df_posting[['job_posting_id', 'company_id', 'location']], on='job_posting_id', how='inner')
            df_eda = df_eda.merge(
                df_companies[['company_id', 'company_size', 'state']], on='company_id', how='left')
            df_eda = df_eda.merge(
                df_job_industries[['job_posting_id', 'industry_id']], on='job_posting_id', how='left')
            df_eda = df_eda.merge(
                df_industries[['industry_id', 'industry_name']], on='industry_id', how='left')
            df_eda = df_eda.merge(
                df_job_skills[['job_posting_id', 'skill_id']], on='job_posting_id', how='left')
            df_eda = df_eda.merge(
                df_skills[['skill_id', 'skill_name']], on='skill_id', how='left')

            # Normalize salary
            def normalize_salary(row):
                s = row['med_salary']
                p = str(row['pay_period']).upper()
                if p == 'HOURLY':  return s * 2080
                elif p == 'MONTHLY': return s * 12
                return s

            df_eda['yearly_salary_est'] = df_eda.apply(normalize_salary, axis=1)

            # Skill classification
            tech_kw = ['IT','Engineering','Software','Data','Programming','Cloud','Network',
                    'Developer','Analytics','Design','ART']
            def classify(name):
                if pd.isna(name): return 'Unknown'
                nu = str(name).upper()
                for kw in tech_kw:
                    if kw.upper() in nu: return 'Technical'
                return 'Non-Technical'

            df_eda['skill_category'] = df_eda['skill_name'].apply(classify)
            df_jobs = df_eda.drop_duplicates(subset=['job_posting_id'])
            return df_eda, df_jobs, True, ""

        except FileNotFoundError as e:
            # Demo / sample data if CSVs not found
            np.random.seed(42)
            n = 1200
            industries = ['Technology','Finance','Healthcare','Energy','Consulting',
                        'Manufacturing','Education','Retail','Media','Biotech']
            locations  = ['New York, NY','San Francisco, CA','Seattle, WA','Austin, TX',
                        'Boston, MA','Chicago, IL','Denver, CO','Atlanta, GA',
                        'Los Angeles, CA','Remote']
            sizes = list(range(8))

            df_jobs = pd.DataFrame({
                'job_posting_id': range(n),
                'company_size': np.random.choice(sizes, n),
                'industry_name': np.random.choice(industries, n),
                'location': np.random.choice(locations, n),
                'pay_period': np.random.choice(['YEARLY','HOURLY','MONTHLY'], n, p=[.6,.25,.15]),
                'med_salary': np.random.lognormal(11.2, 0.4, n),
                'skill_name': np.random.choice(
                    ['Software Engineering','Data Analytics','Sales','IT Support',
                    'Project Management','Cloud Computing','Marketing','Finance'],n),
            })
            df_jobs['yearly_salary_est'] = df_jobs['med_salary']
            tech_kw = ['Engineering','Analytics','IT','Cloud','Computing']
            df_jobs['skill_category'] = df_jobs['skill_name'].apply(
                lambda x: 'Technical' if any(kw in str(x) for kw in tech_kw) else 'Non-Technical')

            df_eda = df_jobs.copy()
            return df_eda, df_jobs, False, str(e)

    df_eda, df_jobs_unique, real_data, data_err = load_and_process_data()

    # ─────────────────────────────────────────────
    # PLOTLY THEME
    # ─────────────────────────────────────────────
    PLOTLY_LAYOUT = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', color='#e8edf5'),
        margin=dict(l=8, r=8, t=36, b=8),
        showlegend=True,
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor='#1e2a40'),
        xaxis=dict(gridcolor='#1e2a40', zerolinecolor='#1e2a40'),
        yaxis=dict(gridcolor='#1e2a40', zerolinecolor='#1e2a40'),
    )
    COLORS = ['#00e5ff','#ff4f7b','#ffe066','#a78bfa','#34d399','#f97316','#60a5fa','#f472b6']

    # ─────────────────────────────────────────────
    # SIDEBAR FILTERS
    # ─────────────────────────────────────────────
    with st.sidebar:


        # Salary range
        sal_min = int(df_jobs_unique['yearly_salary_est'].quantile(0.01))
        sal_max = int(df_jobs_unique['yearly_salary_est'].quantile(0.99))
        sal_range = st.slider(
            "Rentang Gaji Tahunan (USD)",
            min_value=sal_min, max_value=sal_max,
            value=(sal_min, min(300_000, sal_max)),
            step=5_000, format="$%d"
        )

        # Industry filter
        all_industries = sorted(df_jobs_unique['industry_name'].dropna().unique())
        sel_industries = st.multiselect(
            "Industri", options=all_industries,
            default=all_industries[:6] if len(all_industries) >= 6 else all_industries,
            placeholder="Pilih industri..."
        )

        # Company size filter
        all_sizes = sorted(df_jobs_unique['company_size'].dropna().unique())
        sel_sizes = st.multiselect(
            "Ukuran Perusahaan (0–7)", options=[int(s) for s in all_sizes],
            default=[int(s) for s in all_sizes],
            placeholder="Pilih ukuran..."
        )

        # Skill category
        sel_skill_cat = st.radio(
            "Kategori Skill",
            options=["Semua", "Technical", "Non-Technical"],
            index=0, horizontal=True
        )

        # Top N
        top_n = st.slider("Tampilkan Top N Industri / Lokasi", 5, 20, 10)

        st.markdown("---")
        st.markdown("""
        <div style='font-size:11px;color:#7a8aaa;line-height:1.6'>
        📊 <b>Dashboard ini</b> menganalisis faktor-faktor yang memengaruhi kompensasi tenaga kerja.<br><br>
        Data: LinkedIn Job Postings
        </div>
        """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # APPLY FILTERS
    # ─────────────────────────────────────────────
    def apply_filters(df, unique=True):
        d = df.copy()
        d = d[(d['yearly_salary_est'] >= sal_range[0]) & (d['yearly_salary_est'] <= sal_range[1])]
        if sel_industries:
            d = d[d['industry_name'].isin(sel_industries)]
        if sel_sizes:
            d = d[d['company_size'].isin(sel_sizes)]
        if sel_skill_cat != "Semua":
            d = d[d['skill_category'] == sel_skill_cat]
        return d

    df_f = apply_filters(df_jobs_unique)
    df_eda_f = apply_filters(df_eda)

    # ─────────────────────────────────────────────
    # HERO HEADER
    # ─────────────────────────────────────────────
    if not real_data:
        st.warning(f"⚠️ File CSV tidak ditemukan ({data_err}). Menampilkan **data demo acak** untuk preview tampilan dashboard.", icon="⚠️")

    st.markdown("""
    <div class='hero'>
    <h1>💼 Insight <span>Kompensasi</span> Pekerja</h1>
    <p>Analisis interaktif faktor-faktor penentu gaji — industri, lokasi, skill, dan skala perusahaan</p>
    </div>
    """, unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # KPI METRICS ROW
    # ─────────────────────────────────────────────
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    total_jobs  = len(df_f)
    med_sal     = df_f['yearly_salary_est'].median()
    avg_sal     = df_f['yearly_salary_est'].mean()
    n_industry  = df_f['industry_name'].nunique()

    with m_col1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-label'>Total Lowongan</div>
            <div class='metric-value'>{total_jobs:,}</div>
            <div class='metric-sub'>setelah filter diterapkan</div>
        </div>""", unsafe_allow_html=True)

    with m_col2:
        st.markdown(f"""<div class='metric-card' style='border-left-color:#ff4f7b'>
            <div class='metric-label'>Median Gaji</div>
            <div class='metric-value' style='color:#ff4f7b'>${med_sal:,.0f}</div>
            <div class='metric-sub'>per tahun (USD)</div>
        </div>""", unsafe_allow_html=True)

    with m_col3:
        st.markdown(f"""<div class='metric-card' style='border-left-color:#ffe066'>
            <div class='metric-label'>Rata-rata Gaji</div>
            <div class='metric-value' style='color:#ffe066'>${avg_sal:,.0f}</div>
            <div class='metric-sub'>per tahun (USD)</div>
        </div>""", unsafe_allow_html=True)

    with m_col4:
        st.markdown(f"""<div class='metric-card' style='border-left-color:#a78bfa'>
            <div class='metric-label'>Jumlah Industri</div>
            <div class='metric-value' style='color:#a78bfa'>{n_industry}</div>
            <div class='metric-sub'>dalam dataset terfilter</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # ROW 1: Company Size Boxplot + Skill Category
    # ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>// UKURAN PERUSAHAAN & SKILL</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown("""<div class='chart-box'>
        <div class='chart-title'>Company Size vs Salary</div>
        <div class='chart-subtitle'>Distribusi Gaji per Skala Perusahaan</div>
        """, unsafe_allow_html=True)

        df_size = df_f.dropna(subset=['company_size'])
        if not df_size.empty:
            fig_box = px.box(
                df_size, x='company_size', y='yearly_salary_est',
                color='company_size',
                color_discrete_sequence=COLORS,
                labels={'company_size':'Ukuran Perusahaan (0=Terkecil, 7=Terbesar)',
                        'yearly_salary_est':'Estimasi Gaji Tahunan (USD)'},
                points=False,
            )
            # FIX: Pisahkan layout global dan spesifik
            fig_box.update_layout(**PLOTLY_LAYOUT)
            fig_box.update_layout(
                height=350,
                showlegend=False,
                xaxis_title='Ukuran Perusahaan (0–7)',
                yaxis_tickformat='$,.0f'
            )
            fig_box.update_traces(marker_line_color='rgba(0,0,0,0)')
            st.plotly_chart(fig_box, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Tidak ada data setelah filter.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("""<div class='chart-box'>
        <div class='chart-title'>Skill Category</div>
        <div class='chart-subtitle'>Technical vs Non-Technical</div>
        """, unsafe_allow_html=True)

        df_skill_f = df_eda_f[df_eda_f['skill_category'] != 'Unknown']
        if not df_skill_f.empty:
            skill_med = df_skill_f.groupby('skill_category')['yearly_salary_est'].median().reset_index()
            fig_skill = px.bar(
                skill_med, x='skill_category', y='yearly_salary_est',
                color='skill_category',
                color_discrete_map={'Technical':'#00e5ff','Non-Technical':'#ff4f7b'},
                text=skill_med['yearly_salary_est'].apply(lambda v: f'${v:,.0f}'),
                labels={'skill_category':'','yearly_salary_est':'Median Gaji (USD)'},
            )
            fig_skill.update_traces(textposition='outside', textfont_size=13)
            # FIX: Pisahkan layout global dan spesifik
            fig_skill.update_layout(**PLOTLY_LAYOUT)
            fig_skill.update_layout(
                height=350,
                showlegend=False,
                yaxis_tickformat='$,.0f'
            )
            st.plotly_chart(fig_skill, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Tidak ada data skill setelah filter.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # ROW 2: Industry + Location
    # ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>// INDUSTRI & LOKASI</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        st.markdown("""<div class='chart-box'>
        <div class='chart-title'>Top Industries by Salary</div>
        <div class='chart-subtitle'>Median Gaji per Industri</div>
        """, unsafe_allow_html=True)

        agg_col = st.radio(
            "Agregasi", ["Median", "Rata-rata"], horizontal=True, key="agg_industry",
            label_visibility="collapsed"
        )
        agg_fn = np.median if agg_col == "Median" else np.mean
        top_ind = df_f.groupby('industry_name')['yearly_salary_est'].agg(agg_fn).nlargest(top_n).reset_index()
        top_ind.columns = ['industry_name','salary']

        if not top_ind.empty:
            fig_ind = px.bar(
                top_ind.sort_values('salary'), x='salary', y='industry_name',
                orientation='h',
                color='salary',
                color_continuous_scale=['#1e2a40','#00e5ff'],
                text=top_ind.sort_values('salary')['salary'].apply(lambda v: f'${v/1000:.0f}K'),
                labels={'salary':f'{agg_col} Gaji (USD)', 'industry_name':''},
            )
            fig_ind.update_traces(textposition='outside')
            # FIX: Pisahkan layout global dan spesifik
            fig_ind.update_layout(**PLOTLY_LAYOUT)
            fig_ind.update_layout(
                height=420,
                coloraxis_showscale=False,
                xaxis_tickformat='$,.0f'
            )
            st.plotly_chart(fig_ind, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Tidak ada data industri.")
        st.markdown("</div>", unsafe_allow_html=True)

    with c4:
        st.markdown("""<div class='chart-box'>
        <div class='chart-title'>Top Locations by Salary</div>
        <div class='chart-subtitle'>Median Gaji per Lokasi</div>
        """, unsafe_allow_html=True)

        min_postings = st.slider("Min. jumlah lowongan per lokasi", 1, 50, 10, key="loc_min")
        loc_counts = df_f['location'].value_counts()
        valid_locs = loc_counts[loc_counts >= min_postings].index
        df_vloc = df_f[df_f['location'].isin(valid_locs)]

        agg_col2 = st.radio(
            "Agregasi", ["Median", "Rata-rata"], horizontal=True, key="agg_loc",
            label_visibility="collapsed"
        )
        agg_fn2 = np.median if agg_col2 == "Median" else np.mean
        top_loc = df_vloc.groupby('location')['yearly_salary_est'].agg(agg_fn2).nlargest(top_n).reset_index()
        top_loc.columns = ['location','salary']

        if not top_loc.empty:
            fig_loc = px.bar(
                top_loc.sort_values('salary'), x='salary', y='location',
                orientation='h',
                color='salary',
                color_continuous_scale=['#1e2a40','#ff4f7b'],
                text=top_loc.sort_values('salary')['salary'].apply(lambda v: f'${v/1000:.0f}K'),
                labels={'salary':f'{agg_col2} Gaji (USD)', 'location':''},
            )
            fig_loc.update_traces(textposition='outside')
            # FIX: Pisahkan layout global dan spesifik
            fig_loc.update_layout(**PLOTLY_LAYOUT)
            fig_loc.update_layout(
                height=420,
                coloraxis_showscale=False,
                xaxis_tickformat='$,.0f'
            )
            st.plotly_chart(fig_loc, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Tidak ada data lokasi dengan jumlah lowongan yang cukup.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # ROW 3: Salary Distribution Histogram + Scatter
    # ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>// DISTRIBUSI & KORELASI</div>", unsafe_allow_html=True)
    c5, c6 = st.columns([2,3])

    with c5:
        st.markdown("""<div class='chart-box'>
        <div class='chart-title'>Salary Distribution</div>
        <div class='chart-subtitle'>Distribusi Frekuensi Gaji</div>
        """, unsafe_allow_html=True)

        n_bins = st.slider("Jumlah Bin", 10, 80, 30, key="hist_bins")
        fig_hist = px.histogram(
            df_f, x='yearly_salary_est', nbins=n_bins,
            color_discrete_sequence=['#00e5ff'],
            labels={'yearly_salary_est':'Estimasi Gaji Tahunan (USD)', 'count':'Jumlah Lowongan'},
        )
        # FIX: Pisahkan layout global dan spesifik
        fig_hist.update_layout(**PLOTLY_LAYOUT)
        fig_hist.update_layout(
            height=320,
            bargap=0.05,
            xaxis_tickformat='$,.0f'
        )
        # Vertical median line
        fig_hist.add_vline(x=med_sal, line_dash='dash', line_color='#ffe066',
                        annotation_text=f"Median: ${med_sal:,.0f}",
                        annotation_position='top right',
                        annotation_font_color='#ffe066')
        st.plotly_chart(fig_hist, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c6:
        st.markdown("""<div class='chart-box'>
        <div class='chart-title'>Salary by Industry & Size</div>
        <div class='chart-subtitle'>Gaji Berdasarkan Industri & Ukuran Perusahaan</div>
        """, unsafe_allow_html=True)

        df_bubble = df_f.groupby(['industry_name','company_size']).agg(
            salary=('yearly_salary_est','median'),
            count=('job_posting_id','count')
        ).reset_index().dropna()

        if not df_bubble.empty and len(df_bubble) > 1:
            fig_bub = px.scatter(
                df_bubble, x='company_size', y='salary',
                size='count', color='industry_name',
                color_discrete_sequence=COLORS,
                hover_name='industry_name',
                hover_data={'company_size':True,'salary':':.0f','count':True},
                labels={'company_size':'Ukuran Perusahaan','salary':'Median Gaji (USD)',
                        'count':'Jumlah Lowongan'},
                size_max=40,
            )
            # FIX: Pisahkan layout global dan spesifik
            fig_bub.update_layout(**PLOTLY_LAYOUT)
            fig_bub.update_layout(
                height=320,
                yaxis_tickformat='$,.0f',
                legend=dict(orientation='v', x=1.01)
            )
            st.plotly_chart(fig_bub, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Data tidak cukup untuk scatter plot.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # ROW 4: Top Skills Table + Pay Period Pie
    # ─────────────────────────────────────────────
    st.markdown("<div class='section-header'>// SKILL & STRUKTUR GAJI</div>", unsafe_allow_html=True)
    c7, c8 = st.columns([3, 2])

    with c7:
        st.markdown("""<div class='chart-box'>
        <div class='chart-title'>Skills Leaderboard</div>
        <div class='chart-subtitle'>Skill dengan Median Gaji Tertinggi</div>
        """, unsafe_allow_html=True)

        if 'skill_name' in df_eda_f.columns:
            skill_board = (df_eda_f[df_eda_f['skill_name'].notna()]
                        .groupby(['skill_name','skill_category'])
                        .agg(median_salary=('yearly_salary_est','median'),
                                job_count=('job_posting_id','nunique'))
                        .reset_index()
                        .sort_values('median_salary', ascending=False)
                        .head(15))

            fig_skill_bar = px.bar(
                skill_board.sort_values('median_salary'),
                x='median_salary', y='skill_name',
                orientation='h',
                color='skill_category',
                color_discrete_map={'Technical':'#00e5ff','Non-Technical':'#ff4f7b','Unknown':'#7a8aaa'},
                text=skill_board.sort_values('median_salary')['median_salary'].apply(
                    lambda v: f'${v/1000:.0f}K'),
                hover_data={'job_count':True},
                labels={'median_salary':'Median Gaji (USD)','skill_name':'','skill_category':'Kategori'},
            )
            fig_skill_bar.update_traces(textposition='outside')
            # FIX: Pisahkan layout global dan spesifik
            fig_skill_bar.update_layout(**PLOTLY_LAYOUT)
            fig_skill_bar.update_layout(
                height=420,
                xaxis_tickformat='$,.0f'
            )
            st.plotly_chart(fig_skill_bar, use_container_width=True, config={'displayModeBar': False})
        st.markdown("</div>", unsafe_allow_html=True)

    with c8:
        st.markdown("""<div class='chart-box'>
        <div class='chart-title'>Pay Period Distribution</div>
        <div class='chart-subtitle'>Proporsi Struktur Pembayaran</div>
        """, unsafe_allow_html=True)

        if 'pay_period' in df_f.columns:
            pp_counts = df_f['pay_period'].value_counts().reset_index()
            pp_counts.columns = ['pay_period','count']
            fig_pie = px.pie(
                pp_counts, names='pay_period', values='count',
                color_discrete_sequence=COLORS,
                hole=0.55,
            )
            # FIX: Pisahkan layout global dan spesifik
            fig_pie.update_layout(**PLOTLY_LAYOUT)
            fig_pie.update_layout(
                height=280,
                legend=dict(orientation='h', y=-0.1)
            )
            fig_pie.update_traces(textinfo='percent+label', textfont_size=12)
            st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

        # Summary stats table
        st.markdown("**Statistik Ringkasan**")
        stats = df_f['yearly_salary_est'].describe().rename({
            'count':'Jumlah','mean':'Rata-rata','std':'Std Dev',
            'min':'Min','25%':'Q1','50%':'Median','75%':'Q3','max':'Max'
        })
        stats_df = pd.DataFrame({'Metrik': stats.index, 'Nilai': stats.values})
        stats_df['Nilai'] = stats_df['Nilai'].apply(lambda v: f'${v:,.0f}' if stats_df.index[stats_df['Nilai']==v].tolist() else f'{v:.0f}')
        st.dataframe(
            stats_df.style.set_properties(**{
                'background-color':'transparent',
                'color':'#e8edf5',
                'border':'none'
            }),
            hide_index=True, use_container_width=True, height=260
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # FOOTER
    # ─────────────────────────────────────────────
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='text-align:center;color:#7a8aaa;font-size:12px;font-family:Space Mono,monospace;padding:12px 0 24px'>
        {'✅ Data Real' if real_data else '⚠️ Data Demo'} &nbsp;|&nbsp;
        {total_jobs:,} lowongan terfilter &nbsp;|&nbsp;
        {n_industry} industri &nbsp;|&nbsp;
        Rentang: ${sal_range[0]:,} – ${sal_range[1]:,}
    </div>
    """, unsafe_allow_html=True)