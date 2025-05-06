import os
import time
import csv
import random
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === 20 User Agents from 2025 ===
user_agents = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
]

def get_article_data(article_url, keyword):
    headers = {'User-Agent': random.choice(user_agents)}
    response = requests.get(article_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    title_tag = soup.find('h1')
    div = soup.find('div', class_='wysiwyg wysiwyg--all-content')

    if not title_tag or not div:
        print(f"❌ Skipped (missing title or content): {article_url}")
        return None

    title = title_tag.get_text(strip=True)
    paragraphs = div.find_all('p')
    content = "\n\n".join(p.get_text(strip=True) for p in paragraphs)

    return {
        'Keyword Searched': keyword,
        'Title': title,
        'Content': content,
        'URL': article_url
    }

def main():
    keyword = input("Enter your search keyword(s): ").strip()
    encoded_keyword = urllib.parse.quote(keyword)
    search_url = f"https://www.aljazeera.com/search/{encoded_keyword}"
    print(f"🔍 Searching for: {keyword}")
    print(f"🌐 URL: {search_url}")

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(search_url)

    print("⏳ Waiting for the search results to load...")
    time.sleep(3)

    print("➡️ Clicking 'Show more' until all results are loaded...")
    while True:
        try:
            show_more = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button.show-more-button"))
            )
            if show_more.is_displayed():
                driver.execute_script("arguments[0].click();", show_more)
                print("🔄 Clicked 'Show more'")
                time.sleep(3)
            else:
                print("✅ Reached end of results.")
                break
        except:
            print("✅ No 'Show more' button found or it has disappeared.")
            break

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    print("📄 Parsing article links from loaded results...")

    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].startswith("https://www.aljazeera.com")]
    print(f"🔗 Found {len(links)} article links.")

    if not links:
        print("⚠️ No articles found. Exiting.")
        return

    file_exists = os.path.isfile('aljazeera_articles.csv')
    with open('aljazeera_articles.csv', 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Keyword Searched', 'Title', 'Content', 'URL']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            print("📝 Creating new CSV file...")
            writer.writeheader()
        else:
            print("📎 Appending to existing CSV file...")

        for idx, link in enumerate(links, 1):
            print(f"({idx}/{len(links)}) 🔍 Scraping: {link}")
            data = get_article_data(link, keyword)
            if data:
                writer.writerow(data)
                print(f"✅ Scraped and saved: {data['Title'][:60]}...")
            else:
                print("⚠️ Failed to scrape article.")
            time.sleep(random.randint(3, 5))

    print("🎉 All done. Articles saved to aljazeera_articles.csv")

if __name__ == "__main__":
    main()
