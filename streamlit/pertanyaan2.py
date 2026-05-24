import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from load_data import df_posting, df_job_skills


    # ─── Data Loading ─────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Memuat data...")
def load_data():
    df_posting
    df_job_skills
    return df_posting, df_job_skills



@st.cache_data
def prepare_atr(df_posting, df_job_skills):
    df_atr = df_posting[df_posting['views'] > 0].copy()
    df_atr['atr'] = df_atr['applies'] / df_atr['views']
    skill_complexity = df_job_skills.groupby('job_posting_id').size().reset_index(name='skill_count')
    df_atr = df_atr.merge(skill_complexity, on='job_posting_id', how='left')
    df_atr['skill_count'] = df_atr['skill_count'].fillna(0).astype(int)
    return df_atr



# ─── Apply Filters ────────────────────────────────────────────────────────────
def remote_label(val):
    if val == 1:
        return "Remote"
    elif val == 0:
        return "On-site"
    return "Tidak Diketahui"
    


def visualisasi_pertanyaan():
    # ─── Page Config ──────────────────────────────────────────────────────────────
    st.set_page_config(
        page_title="LinkedIn Job Posting Dashboard",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ─── Custom CSS ───────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Space Mono', monospace;
        letter-spacing: -0.03em;
    }
    .metric-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        color: #f8fafc;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        font-family: 'Space Mono', monospace;
        color: #38bdf8;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 4px;
    }
    .section-header {
        border-left: 4px solid #38bdf8;
        padding-left: 12px;
        margin: 1.5rem 0 1rem 0;
    }
    .stSidebar {
        background-color: #0f172a !important;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 12px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)



    df_posting, df_job_skills = load_data()

    # ─── Data Preparation ─────────────────────────────────────────────────────────


    df_atr = prepare_atr(df_posting, df_job_skills)

    # ─── Sidebar Controls ─────────────────────────────────────────────────────────
    with st.sidebar:

        # ATR range filter
        atr_min, atr_max = float(df_atr['atr'].min()), float(df_atr['atr'].quantile(0.99))
        atr_range = st.slider(
            "Rentang ATR (Apply-Through-Rate)",
            min_value=0.0,
            max_value=round(atr_max, 2),
            value=(0.0, round(atr_max, 2)),
            step=0.01,
        )

        # Remote filter
        remote_options = st.multiselect(
            "Kebijakan Remote",
            options=["Remote", "On-site", "Tidak Diketahui"],
            default=["Remote", "On-site", "Tidak Diketahui"],
        )

        # Skill count filter
        skill_max = int(df_atr['skill_count'].max())
        skill_range = st.slider(
            "Jumlah Skill yang Dibutuhkan",
            min_value=0,
            max_value=skill_max,
            value=(0, skill_max),
        )

        # Top N locations
        top_n = st.slider("Tampilkan Top-N Lokasi", min_value=5, max_value=30, value=10, step=1)

        # Min postings for location stability
        min_postings = st.number_input(
            "Min. Postingan per Lokasi (stabilitas data)",
            min_value=1, max_value=500, value=50, step=10,
        )



    df_atr['remote_label'] = df_atr['remote_allowed'].apply(remote_label)

    df_filtered = df_atr[
        (df_atr['atr'] >= atr_range[0]) &
        (df_atr['atr'] <= atr_range[1]) &
        (df_atr['remote_label'].isin(remote_options)) &
        (df_atr['skill_count'] >= skill_range[0]) &
        (df_atr['skill_count'] <= skill_range[1])
    ].copy()

    # ─── Title ────────────────────────────────────────────────────────────────────
    st.title("💼 Apply-Through-Rate (ATR) Dashboard")
    st.markdown("Eksplorasi interaktif faktor-faktor yang memengaruhi tingkat lamaran kerja.")

    # ─── KPI Cards ────────────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Postingan (Filter)", f"{len(df_filtered):,}")
    with c2:
        st.metric("Rata-rata ATR", f"{df_filtered['atr'].mean():.3f}")
    with c3:
        st.metric("Median ATR", f"{df_filtered['atr'].median():.3f}")
    with c4:
        st.metric("Rata-rata Skill", f"{df_filtered['skill_count'].mean():.1f}")

    st.markdown("")

    # ─── Tab Layout ───────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏢 Remote vs On-site",
        "🔧 Kompleksitas Skill",
        "📍 Analisis Lokasi",
        "📊 Distribusi & Korelasi",
    ])

    # ══════════════════════════════════════════════════════════════════════════════
    # TAB 1 – Remote vs On-site
    # ══════════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown('<div class="section-header"><h3>ATR berdasarkan Kebijakan Remote</h3></div>', unsafe_allow_html=True)

        col_a, col_b = st.columns([2, 1])

        with col_a:
            remote_agg = (
                df_filtered.groupby('remote_label')['atr']
                .agg(['mean', 'median', 'count'])
                .reset_index()
                .rename(columns={'mean': 'Rata-rata ATR', 'median': 'Median ATR', 'count': 'Jumlah'})
            )

            chart_type = st.radio("Tipe Chart", ["Bar Chart", "Box Plot"], horizontal=True, key="remote_chart")

            if chart_type == "Bar Chart":
                metric_col = st.radio("Metrik", ["Rata-rata ATR", "Median ATR"], horizontal=True, key="remote_metric")
                fig = px.bar(
                    remote_agg, x='remote_label', y=metric_col,
                    color='remote_label',
                    color_discrete_sequence=['#38bdf8', '#818cf8', '#fb7185'],
                    text=metric_col,
                    title=f"{metric_col} per Kebijakan Remote",
                    labels={'remote_label': 'Kebijakan', metric_col: 'ATR'},
                )
                fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
            else:
                fig = px.box(
                    df_filtered, x='remote_label', y='atr',
                    color='remote_label',
                    color_discrete_sequence=['#38bdf8', '#818cf8', '#fb7185'],
                    title="Distribusi ATR per Kebijakan Remote",
                    labels={'remote_label': 'Kebijakan', 'atr': 'ATR'},
                    points='outliers',
                )

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                font_family='DM Sans',
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown("#### Ringkasan Statistik")
            st.dataframe(
                remote_agg.style.format({'Rata-rata ATR': '{:.4f}', 'Median ATR': '{:.4f}', 'Jumlah': '{:,}'}),
                use_container_width=True,
            )

            st.markdown("#### Proporsi Postingan")
            fig_pie = px.pie(
                remote_agg, values='Jumlah', names='remote_label',
                color_discrete_sequence=['#38bdf8', '#818cf8', '#fb7185'],
                hole=0.4,
            )
            fig_pie.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family='DM Sans',
                showlegend=True,
                margin=dict(t=10, b=10),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════════
    # TAB 2 – Skill Complexity
    # ══════════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="section-header"><h3>Pola ATR berdasarkan Jumlah Skill</h3></div>', unsafe_allow_html=True)

        col_left, col_right = st.columns([3, 1])

        with col_right:
            agg_method = st.selectbox("Metode Agregasi", ["mean", "median"], key="skill_agg")
            show_ci = st.checkbox("Tampilkan Confidence Band", value=True)
            max_skill_display = st.slider(
                "Batas Skill Count (untuk kejelasan)",
                min_value=1, max_value=int(df_filtered['skill_count'].max()),
                value=min(20, int(df_filtered['skill_count'].max())),
            )

        skill_agg = (
            df_filtered[df_filtered['skill_count'] <= max_skill_display]
            .groupby('skill_count')['atr']
            .agg(['mean', 'median', 'std', 'count'])
            .reset_index()
        )
        skill_agg['ci'] = 1.96 * skill_agg['std'] / np.sqrt(skill_agg['count'])
        y_col = 'mean' if agg_method == 'mean' else 'median'

        with col_left:
            fig2 = go.Figure()
            if show_ci and agg_method == 'mean':
                fig2.add_trace(go.Scatter(
                    x=pd.concat([skill_agg['skill_count'], skill_agg['skill_count'][::-1]]),
                    y=pd.concat([skill_agg['mean'] + skill_agg['ci'], (skill_agg['mean'] - skill_agg['ci'])[::-1]]),
                    fill='toself', fillcolor='rgba(56,189,248,0.15)',
                    line=dict(color='rgba(0,0,0,0)'),
                    name='95% CI',
                ))
            fig2.add_trace(go.Scatter(
                x=skill_agg['skill_count'], y=skill_agg[y_col],
                mode='lines+markers',
                line=dict(color='#38bdf8', width=2.5),
                marker=dict(size=7, color='#38bdf8'),
                name=f'ATR ({agg_method})',
            ))
            fig2.update_layout(
                title=f"ATR ({agg_method}) vs Jumlah Skill",
                xaxis_title="Jumlah Skill (Kompleksitas)",
                yaxis_title="ATR",
                plot_bgcolor='rgba(15,23,42,0.5)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family='DM Sans',
                hovermode='x unified',
                xaxis=dict(showgrid=True, gridcolor='#1e293b'),
                yaxis=dict(showgrid=True, gridcolor='#1e293b'),
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Heatmap: skill count × remote × ATR
        st.markdown("#### Heatmap: ATR berdasarkan Skill Count × Kebijakan Remote")
        heat_data = (
            df_filtered[df_filtered['skill_count'] <= max_skill_display]
            .groupby(['skill_count', 'remote_label'])['atr']
            .mean()
            .reset_index()
            .pivot(index='remote_label', columns='skill_count', values='atr')
        )
        fig_heat = px.imshow(
            heat_data, color_continuous_scale='Blues',
            labels=dict(x="Skill Count", y="Kebijakan Remote", color="ATR"),
            aspect='auto',
        )
        fig_heat.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font_family='DM Sans',
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════════
    # TAB 3 – Location Analysis
    # ══════════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown('<div class="section-header"><h3>Analisis ATR berdasarkan Lokasi</h3></div>', unsafe_allow_html=True)

        sort_order = st.radio("Urutan", ["ATR Tertinggi", "ATR Terendah"], horizontal=True)
        ascending = sort_order == "ATR Terendah"

        location_counts = df_filtered['location'].value_counts()
        top_locations = location_counts[location_counts >= min_postings].index
        df_loc = df_filtered[df_filtered['location'].isin(top_locations)]

        loc_atr = (
            df_loc.groupby('location')['atr']
            .agg(['mean', 'median', 'count'])
            .reset_index()
            .rename(columns={'mean': 'Rata-rata ATR', 'median': 'Median ATR', 'count': 'Jumlah Postingan'})
            .sort_values('Rata-rata ATR', ascending=ascending)
            .head(top_n)
        )

        col1, col2 = st.columns([3, 2])
        with col1:
            fig3 = px.bar(
                loc_atr, x='Rata-rata ATR', y='location',
                orientation='h',
                color='Rata-rata ATR',
                color_continuous_scale='Teal',
                text='Rata-rata ATR',
                hover_data=['Jumlah Postingan', 'Median ATR'],
                title=f"Top {top_n} Lokasi – {'Tertinggi' if not ascending else 'Terendah'}",
                labels={'location': 'Lokasi'},
            )
            fig3.update_traces(texttemplate='%{text:.3f}', textposition='outside')
            fig3.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family='DM Sans',
                coloraxis_showscale=False,
                yaxis={'categoryorder': 'total ascending' if not ascending else 'total descending'},
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col2:
            st.markdown("#### Tabel Detail Lokasi")
            st.dataframe(
                loc_atr.reset_index(drop=True).style.format({
                    'Rata-rata ATR': '{:.4f}',
                    'Median ATR': '{:.4f}',
                    'Jumlah Postingan': '{:,}',
                }).background_gradient(subset=['Rata-rata ATR'], cmap='Blues'),
                use_container_width=True,
                height=400,
            )

        # Interactive search
        st.markdown("#### 🔍 Cari Lokasi Spesifik")
        search_loc = st.text_input("Ketik nama lokasi (contoh: New York, California):")
        if search_loc:
            result = (
                df_filtered[df_filtered['location'].str.contains(search_loc, case=False, na=False)]
                .groupby('location')['atr']
                .agg(['mean', 'median', 'count'])
                .reset_index()
                .rename(columns={'mean': 'Rata-rata ATR', 'median': 'Median ATR', 'count': 'Jumlah Postingan'})
                .sort_values('Rata-rata ATR', ascending=False)
            )
            if len(result) > 0:
                st.dataframe(result.style.format({'Rata-rata ATR': '{:.4f}', 'Median ATR': '{:.4f}'}), use_container_width=True)
            else:
                st.info("Lokasi tidak ditemukan dalam data yang difilter.")

    # ══════════════════════════════════════════════════════════════════════════════
    # TAB 4 – Distribution & Correlation
    # ══════════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown('<div class="section-header"><h3>Distribusi ATR & Korelasi</h3></div>', unsafe_allow_html=True)

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            nbins = st.slider("Jumlah Bin Histogram", 10, 100, 40)
            fig_hist = px.histogram(
                df_filtered, x='atr', nbins=nbins,
                color_discrete_sequence=['#38bdf8'],
                title="Distribusi ATR (setelah filter)",
                labels={'atr': 'ATR', 'count': 'Jumlah'},
                marginal='box',
            )
            fig_hist.update_layout(
                plot_bgcolor='rgba(15,23,42,0.5)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family='DM Sans',
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_d2:
            fig_scatter = px.scatter(
                df_filtered.sample(min(3000, len(df_filtered)), random_state=42),
                x='skill_count', y='atr',
                color='remote_label',
                color_discrete_sequence=['#38bdf8', '#818cf8', '#fb7185'],
                opacity=0.5,
                title="Scatter: Skill Count vs ATR",
                labels={'skill_count': 'Jumlah Skill', 'atr': 'ATR', 'remote_label': 'Remote'},
                trendline='lowess',
            )
            fig_scatter.update_layout(
                plot_bgcolor='rgba(15,23,42,0.5)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_family='DM Sans',
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        # Percentile analysis
        st.markdown("#### 📈 Analisis Persentil ATR")
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        perc_values = np.percentile(df_filtered['atr'].dropna(), percentiles)
        perc_df = pd.DataFrame({'Persentil': [f"P{p}" for p in percentiles], 'ATR': perc_values})

        fig_perc = px.line(
            perc_df, x='Persentil', y='ATR',
            markers=True,
            color_discrete_sequence=['#38bdf8'],
            title="Distribusi Persentil ATR",
        )
        fig_perc.update_traces(marker=dict(size=10))
        fig_perc.update_layout(
            plot_bgcolor='rgba(15,23,42,0.5)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family='DM Sans',
        )
        st.plotly_chart(fig_perc, use_container_width=True)

    # ─── Footer ───────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.caption("📊 Dashboard ATR — LinkedIn Job Postings | Dibuat dengan Streamlit & Plotly")