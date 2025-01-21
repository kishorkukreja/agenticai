import requests
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Optional, Any
from pytrends.request import TrendReq
import matplotlib.pyplot as plt
from pathlib import Path

class MarketAnalyzer:
    def __init__(self, api_key: str):
        """
        Initialize the MarketAnalyzer with your News API key.
        
        Args:
            api_key: News API key
        """
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
    def fetch_last_7_days_news(self, keywords: Optional[List[str]] = None) -> List[Dict]:
        """
        Fetch news from the last 7 days.
        
        Args:
            keywords: Optional list of keywords to filter news
            
        Returns:
            List of news articles
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        params = {
            'apiKey': self.api_key,
            'from': start_date.strftime('%Y-%m-%d'),
            'to': end_date.strftime('%Y-%m-%d'),
            'language': 'en',
            'sortBy': 'publishedAt'
        }
        
        if keywords:
            params['q'] = ' OR '.join(keywords)
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()['articles']
        except requests.RequestException as e:
            print(f"Error fetching news: {e}")
            return []
    
    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Process and clean the articles data.
        """
        processed_articles = []
        
        for article in articles:
            processed_article = {
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'source': article.get('source', {}).get('name', ''),
                'published_at': article.get('publishedAt', ''),
                'url': article.get('url', '')
            }
            processed_articles.append(processed_article)
        
        return processed_articles

    def query_specialized_news(self, query_str: str, continents: str, country_code: str, categories: List[str]) -> Any:
        """
        Query specialized news using asknews client if available.
        
        Args:
            query_str: Search query
            continents: Geographic region
            country_code: Specific country
            categories: List of categories to search (e.g., ["Business", "Technology"])
        """
        try:
            from asknews_news_client import asknews_news_client
            
            print(f"Querying news for categories {categories} with query: {query_str}")
            response = asknews_news_client().news.search_news(
                query=query_str,
                n_articles=10,
                return_type="dicts",
                method="both",
                continents=[continents],
                countries=[country_code],
                categories=categories,
                strategy='latest news'
            )
            return response
        except ImportError:
            print("asknews_news_client not available, falling back to standard news API")
            keywords = [query_str] + categories
            return self.fetch_last_7_days_news(keywords)

    def get_stock_trends(self, symbols: List[str], timeframe: str = 'today 3-m', geo: str = 'US') -> Dict:
        """
        Get Google Trends data for stock symbols.
        
        Args:
            symbols: List of stock symbols to analyze
            timeframe: Time range for analysis
            geo: Geographic region
            
        Returns:
            Dictionary containing trends data and chart path
        """
        # Build the payload
        self.pytrends.build_payload(symbols, cat=0, timeframe=timeframe, geo=geo, gprop='')
        
        # Get interest over time
        trends_df = self.pytrends.interest_over_time()
        
        # Convert DataFrame to dictionary with date strings as keys
        trends_data = {}
        for column in trends_df.columns:
            if column != 'isPartial':
                trends_data[column] = {
                    date.strftime('%Y-%m-%d'): value 
                    for date, value in trends_df[column].items()
                }
        
        # Create visualization
        plt.figure(figsize=(20, 12))
        trends_df.drop(columns=['isPartial']).plot(title='Google Trends for Stocks')
        plt.xlabel('Date')
        plt.ylabel('Interest Over Time')
        
        # Save plot
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        chart_path = output_dir / 'stock_trends.png'
        plt.savefig(chart_path)
        plt.close()
        
        return {
            'trends_data': trends_data,
            'chart_path': str(chart_path)
        }

def load_env():
    """Load environment variables from .env file"""
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    value = value.strip('\'"')
                    os.environ[key] = value
    except FileNotFoundError:
        print("Warning: .env file not found")
        return False
    return True

def main():
    # Load environment variables
    load_env()
    
    # Get API key from environment variable
    API_KEY = os.getenv('NEWS_API_KEY')
    if not API_KEY:
        raise ValueError("NEWS_API_KEY not found in environment variables. Please add it to your .env file.")
    
    # Initialize the analyzer
    analyzer = MarketAnalyzer(API_KEY)
    
    # Define news queries for different categories
    news_queries = [
        {
            'query': 'market analysis financial trends',
            'categories': ['Business', 'Finance'],
            'description': 'financial_news'
        },
        {
            'query': 'technology innovation AI software',
            'categories': ['Technology', 'Science'],
            'description': 'tech_news'
        },
        {
            'query': 'international relations conflict trade',
            'categories': ['Politics', 'World'],
            'description': 'geopolitical_news'
        }
    ]
    
    # Create output directory
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Fetch specialized news for each category
    all_articles = []
    for query_info in news_queries:
        print(f"\nFetching {query_info['description']}...")
        articles = analyzer.query_specialized_news(
            query_str=query_info['query'],
            continents='North America',  # Can be customized
            country_code='US',          # Can be customized
            categories=query_info['categories']
        )
        
        if articles:
            processed_articles = analyzer.process_articles(articles)
            all_articles.extend(processed_articles)
            
            # Save category-specific news
            with open(output_dir / f"{query_info['description']}.json", 'w') as f:
                json.dump(processed_articles, f, indent=2)
    
    # Save combined news to file
    with open(output_dir / 'all_news.json', 'w') as f:
        json.dump(all_articles, f, indent=2)
    
    # Analyze stock trends
    STOCKS = ["AMZN", "MSFT", "NVDA", "AAPL", "GOOG"]
    print("Analyzing stock trends...")
    stock_trends = analyzer.get_stock_trends(STOCKS)
    
    # Save stock trends data
    with open(output_dir / 'stock_trends.json', 'w') as f:
        json.dump(stock_trends['trends_data'], f, indent=2)
    
    # Print summary
    print(f"\nAnalysis Complete!")
    print(f"Retrieved {len(processed_articles)} news articles")
    print(f"Stock trends chart saved to: {stock_trends['chart_path']}")
    print(f"All data saved to the 'output' directory")

if __name__ == "__main__":
    main()