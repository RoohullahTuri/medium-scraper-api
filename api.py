"""
Medium Article Search API
Part B: API to search scraped articles and return top 10 similar articles by claps
"""

from flask import Flask, request, jsonify
import csv
import re
from typing import List, Dict
from collections import Counter
import os

app = Flask(__name__)

# Path to the CSV file with scraped data
CSV_FILE = 'scrapping_results.csv'


def load_articles() -> List[Dict]:
    """Load all articles from the CSV file"""
    articles = []
    
    if not os.path.exists(CSV_FILE):
        return articles
    
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Convert claps to int for sorting
                try:
                    row['claps'] = int(row.get('claps', 0) or 0)
                except (ValueError, TypeError):
                    row['claps'] = 0
                articles.append(row)
    except Exception as e:
        print(f"Error loading articles: {str(e)}")
    
    return articles


def calculate_similarity(text: str, keywords: str, article: Dict) -> float:
    """
    Calculate similarity score between input text/keywords and an article
    
    Args:
        text: Input text or keywords
        keywords: Keywords from the article
        article: Article dictionary
        
    Returns:
        Similarity score (0-1)
    """
    # Normalize input text
    input_lower = text.lower()
    input_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', input_lower))
    
    # Get article text and keywords
    article_text = (article.get('text', '') + ' ' + article.get('title', '') + 
                   ' ' + article.get('subtitle', '') + ' ' + article.get('keywords', '')).lower()
    article_keywords = article.get('keywords', '').lower()
    
    # Extract words from article
    article_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', article_text))
    
    # Calculate word overlap
    if not input_words:
        return 0.0
    
    # Jaccard similarity (intersection over union)
    intersection = len(input_words & article_words)
    union = len(input_words | article_words)
    
    if union == 0:
        return 0.0
    
    similarity = intersection / union
    
    # Boost score if keywords match
    if article_keywords:
        keyword_matches = sum(1 for word in input_words if word in article_keywords)
        if keyword_matches > 0:
            similarity += keyword_matches * 0.1
    
    return min(similarity, 1.0)


def find_similar_articles(input_text: str, articles: List[Dict], top_n: int = 10) -> List[Dict]:
    """
    Find top N similar articles based on input text/keywords, sorted by claps
    
    Args:
        input_text: Input text or keywords to search for
        articles: List of article dictionaries
        top_n: Number of top articles to return
        
    Returns:
        List of top N similar articles sorted by claps
    """
    if not articles:
        return []
    
    # Calculate similarity scores
    scored_articles = []
    for article in articles:
        similarity = calculate_similarity(input_text, article.get('keywords', ''), article)
        scored_articles.append({
            'article': article,
            'similarity': similarity,
            'claps': article.get('claps', 0)
        })
    
    # Filter articles with some similarity (threshold > 0)
    similar_articles = [item for item in scored_articles if item['similarity'] > 0]
    
    # Sort by similarity first, then by claps (descending)
    similar_articles.sort(key=lambda x: (x['similarity'], x['claps']), reverse=True)
    
    # Get top N articles
    top_articles = similar_articles[:top_n]
    
    # Format results
    results = []
    for item in top_articles:
        article = item['article']
        results.append({
            'url': article.get('url', ''),
            'title': article.get('title', ''),
            'claps': article.get('claps', 0),
            'similarity_score': round(item['similarity'], 3)
        })
    
    return results


@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Medium Article Search API is running',
        'endpoints': {
            '/search': 'POST - Search for similar articles (body: {"query": "your text/keywords"})',
            '/articles': 'GET - Get total number of articles'
        }
    })


@app.route('/search', methods=['POST'])
def search_articles():
    """
    Search endpoint - accepts text/keywords and returns top 10 similar articles
    
    Expected JSON body:
    {
        "query": "your search text or keywords"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        # Load articles
        articles = load_articles()
        
        if not articles:
            return jsonify({
                'error': 'No articles found. Please ensure scrapping_results.csv exists and contains data.',
                'results': []
            }), 404
        
        # Find similar articles
        results = find_similar_articles(query, articles, top_n=10)
        
        return jsonify({
            'query': query,
            'total_articles': len(articles),
            'results_count': len(results),
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/articles', methods=['GET'])
def get_articles_count():
    """Get total number of articles in the database"""
    articles = load_articles()
    return jsonify({
        'total_articles': len(articles),
        'csv_file': CSV_FILE,
        'file_exists': os.path.exists(CSV_FILE)
    })


@app.route('/search', methods=['GET'])
def search_articles_get():
    """
    GET endpoint for search (alternative to POST)
    Query parameter: ?q=your+search+text
    """
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    # Load articles
    articles = load_articles()
    
    if not articles:
        return jsonify({
            'error': 'No articles found. Please ensure scrapping_results.csv exists and contains data.',
            'results': []
        }), 404
    
    # Find similar articles
    results = find_similar_articles(query, articles, top_n=10)
    
    return jsonify({
        'query': query,
        'total_articles': len(articles),
        'results_count': len(results),
        'results': results
    })


if __name__ == '__main__':
    # For production (e.g., on free hosting platforms)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

