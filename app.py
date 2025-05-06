import pandas as pd
from dash import Dash, dcc, html, Output, Input
import plotly.express as px
from wordcloud import WordCloud
from io import BytesIO
import base64

# Load and clean data
df = pd.read_csv(r'C:\Users\user\Desktop\google scraping\aljazeera_articles_with_sentiment.csv')
df = df[df['Sentiment'] != 'ERROR']

# Initialize Dash app
app = Dash(__name__)

# Generate word cloud image
def generate_wordcloud(text):
    wc = WordCloud(width=800, height=400, background_color='white').generate(text)
    buf = BytesIO()
    wc.to_image().save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

# App layout
app.layout = html.Div([
    html.H1("📊 Article Sentiment Dashboard"),

    dcc.Graph(id='sentiment-donut'),

    html.Div([
        html.H3("📌 Most Positive Article"),
        html.Div(id='most-positive'),
        html.H3("📌 Most Negative Article"),
        html.Div(id='most-negative'),
    ], style={'marginBottom': '40px'}),

    html.Label("🔎 Select an Article for Word Cloud"),
    dcc.Dropdown(
        id='article-dropdown',
        options=[{'label': title[:100], 'value': title} for title in df['Title']],
        placeholder="Select an article"
    ),

    html.Div(id="wordcloud-container", children=[
        html.H3("☁️ Word Cloud"),
        html.Img(id="wordcloud-img", style={'width': '100%', 'maxWidth': '800px'})
    ])
])

# Update donut chart and top articles
@app.callback(
    Output('sentiment-donut', 'figure'),
    Output('most-positive', 'children'),
    Output('most-negative', 'children'),
    Input('article-dropdown', 'value')
)
def update_dashboard(_):
    sentiment_counts = df['Sentiment'].value_counts()
    donut = px.pie(
        names=sentiment_counts.index,
        values=sentiment_counts.values,
        hole=0.4,
        title="Sentiment Distribution"
    )

    pos = df[df['Sentiment'] == 'POSITIVE'].sort_values(by='Confidence', ascending=False).iloc[0]
    neg = df[df['Sentiment'] == 'NEGATIVE'].sort_values(by='Confidence', ascending=False).iloc[0]

    return donut, f"{pos['Title']} → [Read]({pos['URL']})", f"{neg['Title']} → [Read]({neg['URL']})"

# Show word cloud
@app.callback(
    Output('wordcloud-img', 'src'),
    Input('article-dropdown', 'value')
)
def display_wordcloud(selected_title):
    if not selected_title:
        return ''
    content = df[df['Title'] == selected_title]['Content'].values[0]
    encoded_img = generate_wordcloud(content)
    return "data:image/png;base64," + encoded_img

# Run app with new Dash syntax
if __name__ == '__main__':
    app.run(debug=True)  # ← FIXED: uses app.run now
