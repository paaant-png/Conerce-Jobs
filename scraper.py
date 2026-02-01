import asyncio
from playwright.async_api import async_playwright
import json
import requests
from bs4 import BeautifulSoup

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
                "experience": "1-3 Years" # LinkedIn guest doesn't show years, so we default
            })
    except: pass
    return jobs

async def scrape_corporate(browser):
    jobs = []
    page = await browser.new_page()
    
    # PEPSICO
    try:
        await page.goto("https://www.pepsicojobs.com/india/jobs", timeout=60000)
        await page.wait_for_selector(".jobs-list-item", timeout=15000)
        items = await page.query_selector_all(".jobs-list-item")
        for item in items:
            title = await (await item.query_selector(".job-title")).inner_text()
            link = await (await item.query_selector("a")).get_attribute("href")
            jobs.append({
                "title": title.strip(),
                "company": "PepsiCo India",
                "location": "India",
                "link": link,
                "category": "DIRECT",
                "experience": "Mid-Senior"
            })
    except: print("PepsiCo failed")

    # MARS
    try:
        await page.goto("https://careers.mars.com/in/en/search-results?keywords=marketing", timeout=60000)
        await page.wait_for_selector(".jobs-list-item", timeout=15000)
        items = await page.query_selector_all(".jobs-list-item")
        for item in items:
            title = await (await item.query_selector(".job-title")).inner_text()
            link = await (await item.query_selector("a")).get_attribute("href")
            jobs.append({
                "title": title.strip(),
                "company": "Mars, Inc.",
                "location": "India",
                "link": link,
                "category": "DIRECT",
                "experience": "Entry-Mid"
            })
    except: print("Mars failed")

    return jobs

async def main():
    linkedin_data = scrape_linkedin()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        corp_data = await scrape_corporate(browser)
        await browser.close()
    
    final = linkedin_data + corp_data
    with open('jobs.json', 'w') as f:
        json.dump(final, f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())
