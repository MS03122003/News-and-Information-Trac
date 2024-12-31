import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

# Function to fetch and parse the HTML content
def fetch_news_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching the page: {str(e)}")
        return None
# Function to extract news articles from the page using BeautifulSoup
def extract_news_from_html(html_content, base_url):
    soup = BeautifulSoup(html_content, 'html.parser')
    news_items = []

    #<article> tags or custom patterns
    for article in soup.find_all('article'):
        title_tag = article.find('h2')  # News titles in <h2> tags
        link_tag = article.find('a', href=True)  # Links in <a> tags
        
        if title_tag and link_tag:
            title = title_tag.get_text(strip=True)#<title> tag
            link = link_tag['href']#<link> tag
            summary = article.find('p').get_text(strip=True)if article.find('p')  else None
            date_tag = article.find('time')  # <time> tags
            
            # Parse the date if available
            publish_date = None
            if date_tag and date_tag.get('datetime'):
                publish_date = datetime.fromisoformat(date_tag['datetime'])
            
            # Handle relative URLs
            if not link.startswith('http'):
                link = requests.compat.urljoin(base_url, link)

            # Store news item
            news_items.append({
                'title': title,
                'link': link,
                'summary': summary,
                'publish_date': publish_date
            })

    return news_items
# Categorization based on simple keywords
def categorize_news(news_item):
    categories = {
        'politics': ['government', 'election', 'political', 'policy','DMK','ADMK','BJP','TVK'],
        'sports': ['football', 'basketball', 'sports', 'cricket','player','team','out','goal'],
        'health': ['health', 'virus', 'pandemic', 'covid', 'medicine','infection'],
        'technology': ['technology', 'tech', 'AI', 'innovation', 'software','tesla','hardware'],
        'general': []  # Default category
    }
    
    for category, keywords in categories.items():
        if any(keyword.lower() in news_item['title'].lower() for keyword in keywords):
            return category
    return 'general'

# Filter news items based on user preferences and recency (exclude news older than 7 days)
def filter_news_by_preference(news_items, preferred_categories):
    filtered_items = []
    current_date = datetime.now()

    for item in news_items:
        # Exclude news older than 7 days
        if item['publish_date'] and (current_date - item['publish_date']).days > 7:
            continue
        
        # Filter by user preferences
        if categorize_news(item) in preferred_categories:
            filtered_items.append(item)

    return filtered_items

# Function to display aggregated and categorized news
def display_news(news_items):
    print("Aggregated and Categorized News:\n")
    for item in news_items:
        category = categorize_news(item)
        print(f"Category: {category}")
        print(f"Title: {item['title']}")
        print(f"Summary: {item['summary'] if item['summary'] else 'No summary available.'}")
        print(f"Link: {item['link']}")
        print(f"Published: {item['publish_date'].strftime('%Y-%m-%d') if item['publish_date'] else 'Date not available.'}\n")

# Main program logic
def main():
    # List of trusted local sources (local news URLs)
    urls = [
        'https://www.bbc.com/news',  # Example trusted local sources
        'https://www.thehindu.com/',
        'https://www.cnn.com/world',
        'https://www.nytimes.com/',
        'https://www.dailythanthi.com/',
        'https://tamil.way2news.com/',
        'https://indianexpress.com/',
        'https://www.ndtv.com/india#pfrom=home-ndtv_mainnavigation',
        'https://www.hindustantimes.com/'
        
    ]

    # User preferences (for categories they are interested in)
    print("Available Categories: politics, sports, health, technology, general")
    preferred_categories = input("Enter preferred categories separated by commas: ").strip().lower().split(',')
    # Initialize an empty list to store all news items
    all_news_items = []

    for url in urls:
        print(f"Fetching news from: {url}")
        html_content = fetch_news_page(url)
        if html_content:
            news_items = extract_news_from_html(html_content, url)
            all_news_items.extend(news_items)

    # Filter news by user preferences and recency
    personalized_news = filter_news_by_preference(all_news_items, preferred_categories)
    
    if personalized_news:
        display_news(personalized_news)
    else:
        print("No personalized news items found.")

# Run the main program
if __name__ == '__main__':
    main()
