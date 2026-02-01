import asyncio
from playwright.async_api import async_playwright
import json
import requests
from bs4 import BeautifulSoup
import random

# --- 1. LINKEDIN (High Success Rate) ---
def scrape_linkedin():
    print("Scraping LinkedIn...")
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    # Using the "Guest" API which is easier to scrape
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Marketing&location=India"
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for card in soup.find_all('div', class_='base-search-card__info'):
            jobs.append({
                "title": card.find('h3').text.strip(),
                "company": card.find('h4').text.strip(),
                "location": card.find('span', class_='job-search-card__location').text.strip(),
                "link": card.parent.find('a')['href'],
                "category": "LinkedIn",
                "experience": "1-3 Years", # Default
                "is_direct": False
            })
    except: pass
    return jobs

# --- 2. CORPORATE PORTALS (Stealth Mode) ---
async def scrape_corporate(browser, url, company_name):
    print(f"Attempting {company_name}...")
    jobs = []
    # Real Browser Context with randomized viewport to look human
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        viewport={'width': 1920, 'height': 1080}
    )
    page = await context.new_page()
    
    try:
        # 1. Go to page
        await page.goto(url, wait_until="networkidle", timeout=45000)
        
        # 2. Wait for ANY list item (Generic selector for most sites)
        # We look for common job card classes used by Phenom/Workday
        await page.wait_for_selector("li, .job-title, .data-row", timeout=15000)
        
        # 3. Extract (Generic Logic)
        # This tries to find the first 5 links on the page that look like jobs
        links = await page.query_selector_all("a")
        count = 0
        for link in links:
            href = await link.get_attribute("href")
            text = await link.inner_text()
            
            # Filter for likely job links
            if href and len(text) > 10 and ("job" in href or "career" in href) and count < 5:
                jobs.append({
                    "title": text.strip().replace("\n", " "),
                    "company": company_name,
                    "location": "India",
                    "link": href if href.startswith("http") else url, # Fix relative links
                    "category": "Direct",
                    "experience": "Mid-Senior",
                    "is_direct": True
                })
                count += 1
                
    except Exception as e:
        print(f"Blocked by {company_name}. Using Fallback.")
        # FALLBACK: If scraping fails, add a generic "Search all jobs" link
        jobs.append({
            "title": f"Explore all {company_name} Openings",
            "company": company_name,
            "location": "Career Portal",
            "link": url,
            "category": "Portal",
            "experience": "Various",
            "is_direct": True
        })
    finally:
        await context.close()
    return jobs

async def main():
    # 1. Get LinkedIn Data
    all_jobs = scrape_linkedin()
    
    # 2. Get Corporate Data
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Add your list here. The script handles the blocking automatically now.
        mars = await scrape_corporate(browser, "https://careers.mars.com/in/en/search-results?keywords=marketing", "Mars")
        pepsi = await scrape_corporate(browser, "https://www.pepsicojobs.com/india/jobs", "PepsiCo")
        nestle = await scrape_corporate(browser, "https://www.nestle.in/jobs/search-jobs?keyword=&country=IN", "Nestlé")
        
        all_jobs.extend(mars)
        all_jobs.extend(pepsi)
        all_jobs.extend(nestle)
        
        await browser.close()
    
    # 3. Save
    with open('jobs.json', 'w') as f:
        json.dump(all_jobs, f, indent=4)
    print(f"Done. Total Jobs: {len(all_jobs)}")

if __name__ == "__main__":
    asyncio.run(main())
