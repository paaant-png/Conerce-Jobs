import asyncio
from playwright.async_api import async_playwright
import json
import requests
from bs4 import BeautifulSoup

# --- FAST SCRAPERS (Standard Requests) ---
def scrape_linkedin():
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0"}
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
                "category": "LINKEDIN",
                "date": "Recently"
            })
    except: pass
    return jobs

# --- DYNAMIC SCRAPERS (Playwright) ---
async def scrape_corporate_portals():
    corporate_jobs = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 1. Mars
        try:
            await page.goto("https://careers.mars.com/in/en/search-results?keywords=marketing", timeout=60000)
            await page.wait_for_selector(".jobs-list-item", timeout=10000)
            items = await page.query_selector_all(".jobs-list-item")
            for item in items:
                title = await item.query_selector(".job-title")
                link = await item.query_selector("a")
                corporate_jobs.append({
                    "title": await title.inner_text(),
                    "company": "Mars, Inc.",
                    "location": "India",
                    "link": await link.get_attribute("href"),
                    "category": "DIRECT",
                    "date": "Direct"
                })
        except: print("Mars timed out")

        # 2. PepsiCo
        try:
            await page.goto("https://www.pepsicojobs.com/india/jobs", timeout=60000)
            await page.wait_for_selector(".jobs-list-item", timeout=10000)
            items = await page.query_selector_all(".jobs-list-item")
            for item in items:
                title = await item.query_selector(".job-title")
                corporate_jobs.append({
                    "title": await title.inner_text(),
                    "company": "PepsiCo India",
                    "location": "India",
                    "link": await (await item.query_selector("a")).get_attribute("href"),
                    "category": "DIRECT",
                    "date": "Direct"
                })
        except: print("PepsiCo timed out")

        await browser.close()
    return corporate_jobs

async def main():
    print("Starting sync...")
    linkedin_data = scrape_linkedin()
    corporate_data = await scrape_corporate_portals()
    
    final_list = linkedin_data + corporate_data
    
    with open('jobs.json', 'w') as f:
        json.dump(final_list, f, indent=4)
    print(f"Success: {len(final_list)} jobs saved.")

if __name__ == "__main__":
    asyncio.run(main())
