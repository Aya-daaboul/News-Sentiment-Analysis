import os
import pandas as pd
import dash
from dash import Dash, html, dcc, Input, Output, State, ctx
from transformers import pipeline

# Define the CSV folder path
csv_folder = r"C:\Users\user\Desktop\google scraping\csvs with SA"
csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]

# Initialize Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Choose A Keyword", style={'textAlign': 'center'}),

    dcc.Dropdown(
        id='csv-selector',
        options=[
            {
                'label': f.replace("aljazeera_articles_with_sentiment_", "").replace(".csv", "").replace("_", " "),
                'value': f
            } for f in csv_files
        ],
        placeholder="Select a CSV file...",
        style={'width': '50%', 'margin': 'auto'}
    ),
    html.Br(),

    dcc.Loading(
        id="loading-article-dropdown",
        type="default",
        children=html.Div([
            dcc.Dropdown(id='article-selector', placeholder='Select an article'),
        ], style={'width': '50%', 'margin': 'auto'})
    ),
    html.Br(),

    dcc.Loading(
        id="loading-summary",
        type="default",
        children=html.Div([
            html.H4("Summary:"),
            html.Div(id='summary-output', style={'whiteSpace': 'pre-line', 'margin': 'auto', 'width': '70%'}),
            html.Div(id='error-output', style={'color': 'red', 'textAlign': 'center'}),
        ])
    )
])

# Global DataFrame cache
df_cache = {}

@app.callback(
    Output('article-selector', 'options'),
    Output('summary-output', 'children'),
    Output('error-output', 'children'),
    Input('csv-selector', 'value'),
    Input('article-selector', 'value')
)
def unified_callback(csv_filename, selected_article_index):
    triggered = ctx.triggered_id
    print(f"[DEBUG] Triggered by: {triggered}")

    # Load CSV and update dropdown
    if triggered == 'csv-selector':
        if not csv_filename:
            return [], "", ""

        csv_path = os.path.join(csv_folder, csv_filename)
        print(f"[DEBUG] Loading CSV: {csv_path}")
        try:
            df = pd.read_csv(csv_path)

            if 'Title' not in df.columns or 'Content' not in df.columns:
                return [], "", "Error: CSV must contain 'Title' and 'Content' columns."

            df = df.dropna(subset=['Title', 'Content'])
            df_cache['data'] = df

            options = [{'label': row['Title'], 'value': idx} for idx, row in df.iterrows()]
            print(f"[DEBUG] Loaded {len(options)} titles.")
            return options, "", ""
        except Exception as e:
            print(f"[ERROR] Failed to load CSV: {e}")
            return [], "", f"Error loading CSV: {e}"

    # Summarize article when one is selected
    elif triggered == 'article-selector':
        try:
            df = df_cache.get('data')
            if df is None:
                return [], "", "Error: No data loaded."

            article_text = df.iloc[selected_article_index]['Content']
            print("[DEBUG] Loaded article content.")

            print("[DEBUG] Initializing summarizer...")
            summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
            print("[DEBUG] Summarizer initialized.")

            if len(article_text) > 1000:
                article_text = article_text[:1000]
                print("[DEBUG] Article content truncated to 1000 characters.")

            print("[DEBUG] Starting summarization...")
            summary = summarizer(article_text, max_length=130, min_length=30, do_sample=False)[0]['summary_text']
            print("[DEBUG] Summary complete.")
            return dash.no_update, summary, ""
        except Exception as e:
            print(f"[ERROR] Summarization failed: {e}")
            return dash.no_update, "", f"Error during summarization: {e}"

    return dash.no_update, "", ""


if __name__ == '__main__':
    app.run(debug=True)
