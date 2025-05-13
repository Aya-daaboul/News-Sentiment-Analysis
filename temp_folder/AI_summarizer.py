import os
import pandas as pd
import streamlit as st
from transformers import pipeline

# Set page config
st.set_page_config(page_title="Gawgel (the summarized way)", layout="centered")
st.title("Gawgel (the summarized way)")

# CSV folder path
csv_folder = os.path.dirname(__file__)
csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]

# Select a CSV file
selected_csv = st.selectbox(
    "Choose A CSV File",
    options=csv_files,
    format_func=lambda f: f.replace("aljazeera_articles_with_sentiment_", "").replace(".csv", "").replace("_", " ")
)

# Initialize summarizer (outside function to avoid reloading it every time)
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

summarizer = load_summarizer()

# Load CSV and populate article dropdown
if selected_csv:
    csv_path = os.path.join(csv_folder, selected_csv)
    try:
        df = pd.read_csv(csv_path)

        if 'Title' not in df.columns or 'Content' not in df.columns:
            st.error("CSV must contain 'Title' and 'Content' columns.")
        else:
            df = df.dropna(subset=['Title', 'Content'])

            # Article selector
            article_titles = df['Title'].tolist()
            selected_idx = st.selectbox("Choose an Article", range(len(article_titles)), format_func=lambda i: article_titles[i])

            if selected_idx is not None:
                article_text = df.loc[selected_idx, 'Content']
                st.subheader("Summary")

                with st.spinner("Summarizing..."):
                    if len(article_text) > 1000:
                        article_text = article_text[:1000]  # Truncate long articles

                    summary = summarizer(article_text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
                    st.success(summary)

    except Exception as e:
        st.error(f"Error loading or processing the CSV: {e}")
