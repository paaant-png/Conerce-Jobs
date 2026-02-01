import requests
from bs4 import BeautifulSoup
import json
import time
import random

def scrape_linkedin_india():
    # Professional Categories
    categories = ["E-Commerce", "Quick Commerce", "Brand Marketing", "Digital Marketing"]
    all_jobs = []
    
    # Mimic a real browser to avoid instant blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    for category in categories:
        print(f"Fetching {category}...")
        # LinkedIn Guest API for India (geoId 102713980)
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={category}&location=India&geoId=102713980&start=0"
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all('div', class_='base-search-card__info')

            for card in job_cards:
                title = card.find('h3', class_='base-search-card__title').text.strip()
                company = card.find('h4', class_='base-search-card__subtitle').text.strip()
                location = card.find('span', class_='job-search-card__location').text.strip()
                link = card.parent.find('a', class_='base-card__full-link')['href']
                
                # Date logic
                date_tag = card.find('time')
                posted_date = date_tag.text.strip() if date_tag else "Recently"

                all_jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "link": link,
                    "category": category,
                    "date": posted_date,
                    "experience": "1-3 Years" # Default professional highlight
                })
            
            # Be polite to LinkedIn to prevent IP ban
            time.sleep(random.uniform(3, 7)) 
            
        except Exception as e:
            print(f"Error scraping {category}: {e}")

    # Save data for the website
    with open('jobs.json', 'w') as f:
        json.dump(all_jobs, f, indent=4)
    print(f"Successfully saved {len(all_jobs)} jobs.")

if __name__ == "__main__":
    scrape_linkedin_india()
