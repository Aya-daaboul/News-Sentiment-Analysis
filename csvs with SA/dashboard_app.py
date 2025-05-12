import pandas as pd 
from dash import Dash, dcc, html, Output, Input
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from io import BytesIO
import base64
import os

# Initialize app
app = Dash(__name__)
app.title = "Sentiment Dashboard"

# Folder and CSVs
csv_folder = r"C:\Users\user\Desktop\google scraping\csvs with SA"
csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]

# Layout
app.layout = html.Div([
    html.H1("Choose A Keyword", style={'textAlign': 'center'}),
    
    dcc.Dropdown(
        id='csv-selector',
        options=[
            {'label': f.replace("aljazeera_articles_with_sentiment_", "").replace(".csv", "").replace("_", " "), 'value': f}
            for f in csv_files
        ],
        placeholder="Select a CSV file...",
        style={'width': '50%', 'margin': 'auto'}
    ),

    html.Br(),

    dcc.Loading(
        id="loading-sentiment",
        type="default",
        children=html.Div(id='sentiment-output')
    ),

    html.Br(),

    dcc.Loading(
        id="loading-similarity",
        type="default",
        children=html.Div([
            dcc.Dropdown(id='article1', placeholder='Select Article 1'),
            dcc.Dropdown(id='article2', placeholder='Select Article 2'),
            html.Div(id='similarity-output')
        ], style={'width': '50%', 'margin': 'auto'})
    ),

    html.Br(),

    dcc.Loading(
        id="loading-wordcloud",
        type="default",
        children=html.Div([
            dcc.Dropdown(id='wordcloud-article', placeholder='Select article for word cloud'),
            html.Img(id='wordcloud-img')
        ], style={'width': '50%', 'margin': 'auto'})
    ),
])

# Global DataFrame
loaded_df = pd.DataFrame()

# Load CSV and update dropdowns
@app.callback(
    Output('sentiment-output', 'children'),
    Output('article1', 'options'),
    Output('article2', 'options'),
    Output('wordcloud-article', 'options'),
    Input('csv-selector', 'value')
)
def load_csv(filename):
    global loaded_df
    try:
        if not filename:
            return html.Div("Please select a CSV file."), [], [], []
        
        df = pd.read_csv(os.path.join(csv_folder, filename))
        df.columns = df.columns.str.strip()
        loaded_df = df

        sentiment_counts = df['Sentiment'].value_counts(normalize=True) * 100
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            hole=0.5,
            title="Sentiment Distribution",
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        article_options = [{'label': row['Title'], 'value': idx} for idx, row in df.iterrows()]
        return dcc.Graph(figure=fig), article_options, article_options, article_options

    except Exception as e:
        return html.Div("An error has occurred. Please contact your admin.", style={'color': 'red'}), [], [], []

# Cosine similarity callback
@app.callback(
    Output('similarity-output', 'children'),
    Input('article1', 'value'),
    Input('article2', 'value')
)
def compute_similarity(idx1, idx2):
    try:
        if idx1 is None or idx2 is None or loaded_df.empty:
            return ""

        content1 = loaded_df.loc[idx1, 'Content']
        content2 = loaded_df.loc[idx2, 'Content']

        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform([content1, content2])
        sim_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

        return f"Cosine Similarity: {sim_score:.2f}"

    except Exception:
        return html.Div("An error has occurred. Please contact your admin.", style={'color': 'red'})

# Word cloud callback
@app.callback(
    Output('wordcloud-img', 'src'),
    Input('wordcloud-article', 'value')
)
def generate_wordcloud(idx):
    try:
        if idx is None or loaded_df.empty:
            return ""

        text = loaded_df.loc[idx, 'Content']
        stopwords = set(STOPWORDS)

        wc = WordCloud(
            width=800,
            height=400,
            background_color='white',
            stopwords=stopwords
        ).generate(text)

        img = BytesIO()
        wc.to_image().save(img, format='PNG')
        img.seek(0)
        encoded = base64.b64encode(img.read()).decode()
        return f'data:image/png;base64,{encoded}'

    except Exception:
        return ""

# Run app
if __name__ == '__main__':
    app.run(debug=True)