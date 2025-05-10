from transformers import pipeline
import pandas as pd

print("✅ Loading sentiment analysis pipeline...")
sentiment_pipeline = pipeline("sentiment-analysis")

print("✅ Reading CSV file...")
df = pd.read_csv(r"aljazeera_articles_tariffs.csv") #adjust here

# Ensure Content is treated as text
print("✅ Converting 'Content' to string type...")
df['Content'] = df['Content'].astype(str)

print("🔍 Starting sentiment analysis...")

# Analyze sentiment
def get_sentiment(text):
    try:
        text = str(text)
        if not text.strip():
            print("⚠️ Skipped empty content.")
            return pd.Series(["EMPTY", 0.0])
        
        result = sentiment_pipeline(text[:512])[0]  # limit to 512 chars
        print(f"✅ Analyzed sentiment: {result['label']} (Confidence: {result['score']:.2f})")
        return pd.Series([result['label'], result['score']])
    
    except Exception as e:
        print(f"❌ Error in sentiment analysis: {e}")
        return pd.Series(["ERROR", 0.0])

# Apply function row by row
df[['Sentiment', 'Confidence']] = df['Content'].apply(get_sentiment)

print("💾 Saving results to 'aljazeera_articles_with_sentiment.csv'...")
df.to_csv("aljazeera_articles_with_sentiment_Tariffs.csv", index=False)

print("🎉 Done! CSV with sentiment saved successfully.")