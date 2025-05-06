from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import random
import time

# ✅ User agents (important for preventing blocking)
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
]

def get_random_user_agent():
    return random.choice(user_agents)

# 🎛️ Setup Chrome WebDriver with headless options
def get_driver():
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument(f"user-agent={get_random_user_agent()}")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--allow-running-insecure-content")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# 📄 Scrape individual article
def scrape_gulf_article(url, driver):
    print(f"🌐 Visiting: {url}")
    try:
        driver.get(url)
        time.sleep(12)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract title
        title_tag = soup.find('h1')
        title = title_tag.get_text(strip=True) if title_tag else "No title found"

        # Extract content
        paragraphs = soup.select("div.article-body p")
        if not paragraphs:
            print("❌ No content found.")
            return None, None

        content = "\n\n".join(p.get_text(strip=True) for p in paragraphs)
        print("✅ Article scraped successfully.")
        return title, content

    except Exception as e:
        print(f"❌ Error scraping article: {e}")
        return None, None

# 🔍 Scrape Gulf News search results
def scrape_gulfnews_articles(keyword):
    search_url = f"https://gulfnews.com/search?q={keyword}&sort=score"
    print(f"\n🔍 Searching Gulf News for: {keyword}")
    print(f"📎 URL: {search_url}\n")

    driver = get_driver()
    driver.get(search_url)
    time.sleep(12)  # Important: wait for content to load fully

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Gather article links
    article_tags = soup.select('a.card')
    article_urls = []

    for tag in article_tags:
        link = tag.get('href')
        if link and link.startswith("https://gulfnews.com/") and "/photos/" not in link and "/videos/" not in link:
            article_urls.append(link)

    print(f"📄 Found {len(article_urls)} articles\n")

    data = []
    for i, url in enumerate(article_urls):
        print(f"\n🔎 Scraping Article {i+1}/{len(article_urls)}...")
        title, content = scrape_gulf_article(url, driver)

        if title and content:
            data.append({
                'Title': title,
                'Content': content,
                'URL': url
            })
        else:
            print("⚠️ Skipped due to missing data.")

        time.sleep(1.5)

    driver.quit()
    print("\n✅ Done scraping Gulf News.")
    return pd.DataFrame(data)

# 🚀 Run the scraper
if __name__ == "__main__":
    keyword = input("🔍 What do you want to search on Gulf News? ").strip()
    df = scrape_gulfnews_articles(keyword)

    if not df.empty:
        print("\n📦 Preview of scraped data:")
        print(df.head())
        csv_name = f"gulfnews_articles_{keyword}.csv"
        df.to_csv(csv_name, index=False, encoding='utf-8')
        print(f"\n💾 Data saved to {csv_name}")
    else:
        print("😢 No articles were scraped.")
