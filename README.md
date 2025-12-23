# Medium Article Web Scraper & Search API

This project consists of two parts:
- **Part A**: Web scraper for Medium articles
- **Part B**: API to search and retrieve similar articles

## Part A: Web Scraping

### Features
The scraper extracts the following data from each Medium article:
- Title
- Subtitle
- Text content
- Number of images
- Image URLs
- Number of external links
- Author Name
- Author URL
- Claps
- Reading time
- Keywords

### Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

### Usage

#### Option 1: Using a text file with URLs
Create a file named `urls.txt` with one URL per line:
```
https://medium.com/@user/article1
https://medium.com/@user/article2
```

Then run:
```bash
python scraper.py
```

#### Option 2: Pass URLs as command line arguments
```bash
python scraper.py https://medium.com/@user/article1 https://medium.com/@user/article2
```

#### Option 3: Pass a file with URLs
```bash
python scraper.py urls.txt
```

### Output
The scraper saves all results to `scrapping_results.csv` (as specified in the requirements).

## Part B: API

### Features
- Accepts text/keywords as input
- Returns top 10 similar articles sorted by claps
- Each result includes URL and Title

### Running the API Locally

```bash
python api.py
```

The API will run on `http://localhost:5000`

### API Endpoints

#### 1. Health Check
```
GET /
```
Returns API status and available endpoints.

#### 2. Search Articles (POST)
```
POST /search
Content-Type: application/json

{
    "query": "your search text or keywords"
}
```

#### 3. Search Articles (GET)
```
GET /search?q=your+search+text
```

#### 4. Get Articles Count
```
GET /articles
```

### Example Usage

#### Using curl (POST):
```bash
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning python"}'
```

#### Using curl (GET):
```bash
curl "http://localhost:5000/search?q=machine+learning+python"
```

#### Using Python:
```python
import requests

response = requests.post('http://localhost:5000/search', 
                        json={'query': 'machine learning python'})
results = response.json()
print(results)
```

### Response Format
```json
{
    "query": "machine learning python",
    "total_articles": 1000,
    "results_count": 10,
    "results": [
        {
            "url": "https://medium.com/@user/article1",
            "title": "Article Title",
            "claps": 500,
            "similarity_score": 0.85
        },
        ...
    ]
}
```

## Deployment to Free Hosting Platforms

### Option 1: Render.com
1. Create a new Web Service
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python api.py`
5. Add environment variable `PORT` (Render sets this automatically)

### Option 2: PythonAnywhere
1. Upload your files via the Files tab
2. Create a new Web App
3. Edit the WSGI file to point to your Flask app
4. Reload the web app

### Option 3: Heroku
1. Create a `Procfile`:
```
web: python api.py
```
2. Deploy using Heroku CLI or GitHub integration

### Option 4: Railway.app
1. Connect your repository
2. Railway will auto-detect Python
3. Set start command: `python api.py`

## Important Notes

1. **CSV File**: Make sure `scrapping_results.csv` exists in the same directory as `api.py` when running the API.

2. **Rate Limiting**: The scraper includes a 1-second delay between requests to be respectful. For 58,000 URLs, this will take approximately 16 hours.

3. **Resumable Scraping**: The scraper appends to the CSV file, so you can stop and resume scraping without losing progress.

4. **Error Handling**: The scraper continues even if some URLs fail, logging errors for debugging.

5. **Similarity Algorithm**: The API uses a simple word-overlap similarity algorithm. For better results, you could enhance it with NLP libraries like spaCy or scikit-learn.

## File Structure
```
medium-scraper-project/
├── scraper.py              # Part A: Web scraper
├── api.py                  # Part B: Search API
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── urls.txt               # (Optional) Input URLs file
└── scrapping_results.csv  # Output CSV file (generated)
```

## License
This project is created for educational purposes.

