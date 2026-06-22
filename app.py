import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
from youtube_client import YouTubeClient
from sentiment_analyzer import SentimentAnalyzer
from utils import extract_video_id, clean_text
import requests
from streamlit_lottie import st_lottie
import json
import matplotlib.pyplot as plt
import base64
import os

st.set_page_config(page_title="Sentify | YouTube Intelligence", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

    :root {
        --bg-dark: #0A0E1A;
        --bg-card: rgba(17, 24, 39, 0.75);
        --accent-primary: #6366F1; /* Indigo */
        --accent-secondary: #06B6D4; /* Cyan */
        --text-primary: #F3F4F6;
        --text-secondary: #9CA3AF;
        --border-color: rgba(255, 255, 255, 0.08);
        --success-color: #10B981; /* Emerald */
        --danger-color: #EF4444; /* Rose */
        --neutral-color: #6B7280; /* Gray */
    }

    .stApp {
        background: radial-gradient(circle at 50% 50%, #0F172A 0%, #020617 100%);
        background-attachment: fixed;
        color: var(--text-primary);
        font-family: 'Outfit', sans-serif;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0B0F19 !important;
        border-right: 1px solid var(--border-color);
    }

    /* Card Containers */
    .dashboard-card {
        background: var(--bg-card);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        margin-bottom: 20px;
    }

    .dashboard-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 15px 35px rgba(99, 102, 241, 0.1);
    }

    /* Metric Cards */
    .metric-card {
        background: var(--bg-card);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }

    .metric-card:hover {
        transform: translateY(-2px);
        border-color: var(--accent-primary);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
    }

    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: var(--text-secondary);
        font-weight: 600;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 2.25rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }

    .metric-percentage {
        font-size: 0.85rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 9999px;
        display: inline-block;
        background: rgba(255, 255, 255, 0.04);
    }

    /* Sentiment specific colors */
    .sentiment-positive { color: var(--success-color); }
    .sentiment-negative { color: var(--danger-color); }
    .sentiment-neutral { color: var(--neutral-color); }
    .sentiment-total { color: var(--accent-secondary); }

    /* Button and Input Styling Overrides */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-primary) 0%, #4F46E5 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4) !important;
        width: 100%;
        text-transform: none !important;
        letter-spacing: normal !important;
        font-style: normal !important;
        transform: none !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        letter-spacing: normal !important;
    }

    .stButton > button:active {
        transform: translateY(1px) !important;
    }

    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        font-family: 'Outfit', sans-serif !important;
        transition: all 0.3s ease !important;
        padding: 12px 16px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
        background-color: rgba(255, 255, 255, 0.05) !important;
    }

    /* Subtitle and headings */
    .floating-header {
        text-align: center;
        padding: 40px 0 20px 0;
    }

    .floating-header h1 {
        background: linear-gradient(135deg, #FFFFFF 0%, #A5B4FC 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -1px;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
    <div class="floating-header">
        <h1 style="font-size: 3.5rem; margin-bottom: 0;">SENTIFY</h1>
        <p style="font-size: 1.1rem; color: #888; font-weight: 300; letter-spacing: 4px;">ADVANCED YOUTUBE AUDIENCE INTELLIGENCE</p>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("YouTube API Key", type="password")
    st.markdown("---")
    st.info("Provide your YouTube Data API Key to analyze video comments. Your key is processed securely and never stored.")

col_input, col_btn = st.columns([4, 1])
with col_input:
    video_url = st.text_input("Enter YouTube Video URL or ID", placeholder="Enter YouTube Video URL or ID (e.g., https://www.youtube.com/watch?v=...)", label_visibility="collapsed")
with col_btn:
    analyze_btn = st.button("Analyze Sentiment", type="primary", use_container_width=True)

if 'comments_df' not in st.session_state:
    st.session_state.comments_df = pd.DataFrame()
if 'next_page_token' not in st.session_state:
    st.session_state.next_page_token = None
if 'current_video_id' not in st.session_state:
    st.session_state.current_video_id = None

if analyze_btn:
    if not api_key:
        st.error("Please provide a valid API Key in the sidebar.")
    elif not video_url:
        st.error("Please provide a video URL or ID.")
    else:
        video_id = extract_video_id(video_url)
        
        if not video_id:
            st.error("Invalid YouTube URL or ID.")
        else:
            # Clear previous state on new search
            st.session_state.comments_df = pd.DataFrame()
            st.session_state.next_page_token = None
            st.session_state.current_video_id = video_id
            
            try:
                with st.spinner("Fetching comments..."):
                    client = YouTubeClient(api_key)
                    df, next_token = client.get_video_comments_page(video_id, max_results=100)
                    
                if df is None or df.empty:
                    st.warning("No comments found or API error occurred. Check your API key and quota.")
                else:
                    st.session_state.comments_df = df
                    st.session_state.next_page_token = next_token
            except Exception as e:
                 st.error(f"An unexpected error occurred: {str(e)}")

if st.session_state.current_video_id and st.session_state.next_page_token:
    if st.button("Load Next Page of Comments"):
        with st.spinner("Fetching next page..."):
            try:
                client = YouTubeClient(api_key)
                new_df, next_token = client.get_video_comments_page(
                    st.session_state.current_video_id, 
                    page_token=st.session_state.next_page_token, 
                    max_results=100
                )
                
                if new_df is not None and not new_df.empty:
                    st.session_state.comments_df = pd.concat([st.session_state.comments_df, new_df], ignore_index=True)
                    st.session_state.next_page_token = next_token
                    st.rerun()
            except Exception as e:
                st.error(f"An unexpected error occurred while loading next page: {str(e)}")

if not st.session_state.comments_df.empty:
    df = st.session_state.comments_df.copy()
    
    df['cleaned_text'] = df['text'].apply(clean_text)
    
    with st.spinner("Analyzing sentiment..."):
        analyzer = SentimentAnalyzer()
        df = analyzer.perform_analysis(df)

    st.markdown('<h2 style="text-align:center; font-weight:700; margin-bottom: 25px;">📊 Audience Sentiment Overview</h2>', unsafe_allow_html=True)
    
    sentiment_counts = df['sentiment'].value_counts()
    total_comments = len(df)
    pos_count = sentiment_counts.get('Positive', 0)
    neg_count = sentiment_counts.get('Negative', 0)
    neu_count = sentiment_counts.get('Neutral', 0)

    g1, g2, g3, g4 = st.columns(4)
    
    def metric_card(label, value, percentage, type_class):
        pct_html = f'<div class="metric-percentage">{percentage}</div>' if percentage else ''
        return f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value {type_class}">{value}</div>
            {pct_html}
        </div>
        """

    with g1:
        st.markdown(metric_card("Total Comments", f"{total_comments:,}", "100% Analysis Volume", "sentiment-total"), unsafe_allow_html=True)
    with g2:
        st.markdown(metric_card("Positive Sentiment", f"{pos_count:,}", f"{pos_count/total_comments:.1%} of total", "sentiment-positive"), unsafe_allow_html=True)
    with g3:
        st.markdown(metric_card("Neutral Sentiment", f"{neu_count:,}", f"{neu_count/total_comments:.1%} of total", "sentiment-neutral"), unsafe_allow_html=True)
    with g4:
        st.markdown(metric_card("Negative Sentiment", f"{neg_count:,}", f"{neg_count/total_comments:.1%} of total", "sentiment-negative"), unsafe_allow_html=True)

    # Visualizations
    st.divider()
    v_col1, v_col2 = st.columns([1, 1])
    
    with v_col1:
        st.subheader("📊 Sentiment Mix")
        fig = px.pie(
            values=[pos_count, neg_count, neu_count], 
            names=['Positive', 'Negative', 'Neutral'],
            hole=0.6,
            color_discrete_sequence=['#10B981', '#EF4444', '#64748B']
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            margin=dict(t=0, b=0, l=0, r=0),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)

    with v_col2:
        st.subheader("📈 Raw Volume")
        fig_bar = px.bar(
            x=['Positive', 'Negative', 'Neutral'],
            y=[pos_count, neg_count, neu_count],
            color=['Positive', 'Negative', 'Neutral'],
            color_discrete_map={'Positive': '#10B981', 'Negative': '#EF4444', 'Neutral': '#64748B'}
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis_title="",
            yaxis_title="Count",
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Word Cloud
    st.divider()
    st.subheader("☁️ Keyword Cloud")
    all_cleaned_text = " ".join(df['cleaned_text'].dropna())
    
    if all_cleaned_text.strip():
        wordcloud = WordCloud(
            width=1200, 
            height=500, 
            background_color=None, 
            mode='RGBA',
            colormap='cool',
            font_path=None # Use default
        ).generate(all_cleaned_text)
        
        fig_wc, ax = plt.subplots(figsize=(15, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        fig_wc.patch.set_alpha(0) # Transparent background
        st.pyplot(fig_wc)
    else:
        st.info("Insufficient text for word cloud.")

    # Data Table
    st.divider()
    with st.expander("🔍 Deep Dive: Raw Comment Data"):
        st.dataframe(df[['author', 'text', 'sentiment', 'sentiment_score']], use_container_width=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Export Analysis Results as CSV",
            csv,
            "sentify_report.csv",
            "text/csv",
            key='download-csv'
        )
