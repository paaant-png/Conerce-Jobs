import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_jobs():
    # Keywords focused on your request
    keywords = ["E-commerce", "Quick Commerce", "Marketing"]
    all_jobs = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for word in keywords:
        # LinkedIn India Guest API URL
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={word}&location=India&geoId=102713980&start=0"
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            cards = soup.find_all('div', class_='base-search-card__info')

            for card in cards:
                all_jobs.append({
                    "title": card.find('h3', class_='base-search-card__title').text.strip(),
                    "company": card.find('h4', class_='base-search-card__subtitle').text.strip(),
                    "location": card.find('span', class_='job-search-card__location').text.strip(),
                    "link": card.parent.find('a', class_='base-card__full-link')['href'],
                    "category": word
                })
            time.sleep(2) 
        except Exception as e:
            print(f"Error: {e}")

    with open('jobs.json', 'w') as f:
        json.dump(all_jobs, f, indent=4)

if __name__ == "__main__":
    scrape_jobs()
