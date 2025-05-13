import pandas as pd
import streamlit as st
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from io import BytesIO
import base64
import os

# Set page config
st.set_page_config(page_title="Sentiment Dashboard", layout="centered")

# Title
st.title("Sentiment Dashboard")

# Data folder (ensure this is correct path)
csv_folder = os.path.join(os.getcwd(), "csvs_with_SA")


# Check if folder exists and has CSV files
if not os.path.exists(csv_folder):
    st.error("Data folder does not exist.")
else:
    csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]

# CSV file selection
selected_csv = st.selectbox(
    "Choose A Keyword",
    options=csv_files,
    format_func=lambda f: f.replace("aljazeera_articles_with_sentiment_", "").replace(".csv", "").replace("_", " ")
)

# Load data
if selected_csv:
    try:
        df = pd.read_csv(os.path.join(csv_folder, selected_csv))
        df.columns = df.columns.str.strip()  # Clean column names

        # Sentiment Distribution (Pie chart)
        sentiment_counts = df['Sentiment'].value_counts(normalize=True) * 100
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            hole=0.5,
            title="Sentiment Distribution",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)  # Replaced deprecated use_column_width

        # Article selection for similarity
        article_titles = df['Title'].tolist()
        idx1 = st.selectbox("Select Article 1", options=range(len(article_titles)), format_func=lambda i: article_titles[i])
        idx2 = st.selectbox("Select Article 2", options=range(len(article_titles)), format_func=lambda i: article_titles[i])

        if idx1 is not None and idx2 is not None:
            content1 = df.loc[idx1, 'Content']
            content2 = df.loc[idx2, 'Content']
            tfidf = TfidfVectorizer(stop_words='english')
            tfidf_matrix = tfidf.fit_transform([content1, content2])
            sim_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            st.markdown(f"*Cosine Similarity:* {sim_score:.2f}")

        # Word Cloud generation
        wc_idx = st.selectbox("Select Article for Word Cloud", options=range(len(article_titles)), format_func=lambda i: article_titles[i])
        if wc_idx is not None:
            text = df.loc[wc_idx, 'Content']
            stopwords = set(STOPWORDS)
            wc = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords).generate(text)

            img = BytesIO()
            wc.to_image().save(img, format='PNG')
            img.seek(0)
            st.image(img, use_container_width=True)  # Replaced deprecated use_column_width

    except Exception as e:
        st.error(f"An error occurred while processing the CSV file: {e}")
else:
    st.write("Please select a CSV file from the dropdown.")