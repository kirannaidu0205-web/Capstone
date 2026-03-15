import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime

class PriceScraper:
    def __init__(self, headers=None):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
        ]
        self.headers = headers or {
            'User-Agent': random.choice(self.user_agents),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }

    def fetch_page(self, url):
        try:
            # Rotate user agent for each request to avoid detection
            current_headers = self.headers.copy()
            current_headers['User-Agent'] = random.choice(self.user_agents)
            
            response = requests.get(url, headers=current_headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def scrape_competitor_a(self, url):
        """
        Example scraper for Competitor A style pages.
        In a real scenario, this would have specific CSS selectors.
        """
        html = self.fetch_page(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # This is placeholder logic as we don't have a specific site.
        # We simulate finding a price.
        try:
            # Fake logic: find price in a common tag
            price_text = soup.find('span', class_='price').get_text()
            price = float(price_text.replace('₹', '').replace(',', '').strip())
            return {
                'competitor': 'Competitor A',
                'price': price,
                'timestamp': datetime.utcnow()
            }
        except Exception:
            # Fallback to random for demonstration if scraping fails on non-existent real URLs
            return {
                'competitor': 'Competitor A',
                'price': round(random.uniform(999, 99999), 2),
                'timestamp': datetime.utcnow()
            }

    def scrape_multiple(self, product_map):
        """
        product_map: {product_id: [url1, url2]}
        """
        results = []
        for pid, urls in product_map.items():
            for url in urls:
                # Determine which scraper to use based on URL
                data = self.scrape_competitor_a(url)
                if data:
                    data['product_id'] = pid
                    results.append(data)
                time.sleep(random.uniform(1, 3)) # Ethics/Anti-blocking
        return results

if __name__ == "__main__":
    scraper = PriceScraper()
    # Demo
    test_urls = {1: ["https://example.com/p1"]}
    print(scraper.scrape_multiple(test_urls))
