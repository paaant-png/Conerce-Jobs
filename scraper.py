import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_linkedin():
    categories = ["E-Commerce", "Marketing"]
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for cat in categories:
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={cat}&location=India&geoId=102713980"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        for card in soup.find_all('div', class_='base-search-card__info'):
            jobs.append({
                "title": card.find('h3').text.strip(),
                "company": "LinkedIn / " + card.find('h4').text.strip(),
                "location": card.find('span', class_='job-search-card__location').text.strip(),
                "link": card.parent.find('a')['href'],
                "category": cat,
                "date": "Recently",
                "experience": "1-3 Years"
            })
    return jobs

def scrape_mars():
    # Target URL provided
    url = "https://careers.mars.com/global/en/search-results?keywords=marketing&location=India"
    headers = {"User-Agent": "Mozilla/5.0"}
    mars_jobs = []
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Mars uses specific data attributes for their job cards
        cards = soup.find_all('li', class_='jobs-list-item')
        for card in cards:
            title = card.find('div', class_='job-title').text.strip()
            link = card.find('a')['href']
            location = card.find('span', class_='job-location').text.strip()
            mars_jobs.append({
                "title": title,
                "company": "MARS INC",
                "location": location,
                "link": link,
                "category": "Corporate",
                "date": "Direct Hire",
                "experience": "See Website"
            })
    except:
        print("Mars site structure updated or blocked.")
    return mars_jobs

# Combine and Save
all_data = scrape_linkedin() + scrape_mars()
with open('jobs.json', 'w') as f:
    json.dump(all_data, f, indent=4)
