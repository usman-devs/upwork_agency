import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_upwork_jobs():
    """Scrapes Upwork job listings and returns structured data"""
    url = "https://www.upwork.com/nx/jobs/search/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        
        jobs = []
        for job in soup.select('.job-tile'):
            # Safely extract data with fallbacks
            title = job.select_one('h2').text.strip() if job.select_one('h2') else "No Title Available"
            description = job.select_one('.description').text.strip() if job.select_one('.description') else "No Description Available"
            
            # Get relative job URL and convert to absolute
            relative_url = job.find('a')['href'] if job.find('a') else None
            url = f"https://www.upwork.com{relative_url}" if relative_url else None
            
            # Extract and format posting time
            posted = job.select_one('.posted-time').text.strip() if job.select_one('.posted-time') else None
            
            jobs.append({
                'title': title,
                'description': description,
                'url': url,
                'posted': posted,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M')
            })
        
        return jobs
    
    except requests.exceptions.RequestException as e:
        print(f"Network error while scraping Upwork: {e}")
    except Exception as e:
        print(f"Unexpected error while scraping: {e}")
    
    return []  # Always return a list, even on failure