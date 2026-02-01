import asyncio
from playwright.async_api import async_playwright
import json
import requests
from bs4 import BeautifulSoup

def scrape_linkedin():
    jobs = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Marketing&location=India"
    try:
        res = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        for card in soup.find_all('div', class_='base-search-card__info'):
            jobs.append({
                "title": card.find('h3').text.strip(),
                "company": card.find('h4').text.strip(),
                "location": card.find('span', class_='job-search-card__location').text.strip(),
                "link": card.parent.find('a')['href'],
                "category": "LinkedIn",
                "experience": "1-3 Years"
            })
    except: print("LinkedIn connection issue.")
    return jobs

async def scrape_corporate(browser, url, company_name):
    jobs = []
    # Using a high-quality User-Agent to bypass simple bot filters
    context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    page = await context.new_page()
    try:
        print(f"Syncing {company_name}...")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        
        # Wait for the job card container to exist
        await page.wait_for_selector(".jobs-list-item", timeout=20000)
        
        items = await page.query_selector_all(".jobs-list-item")
        for item in items:
            title_node = await item.query_selector(".job-title")
            link_node = await item.query_selector("a")
            
            if title_node and link_node:
                jobs.append({
                    "title": (await title_node.inner_text()).strip(),
                    "company": company_name,
                    "location": "India",
                    "link": await link_node.get_attribute("href"),
                    "category": "Direct Hire",
                    "experience": "Mid-Senior"
                })
    except Exception as e:
        print(f"{company_name} sync error: Site took too long to load.")
    finally:
        await context.close()
    return jobs

async def main():
    linkedin_jobs = scrape_linkedin()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Add your corporate URLs here
        pepsi = await scrape_corporate(browser, "https://www.pepsicojobs.com/india/jobs", "PepsiCo")
        mars = await scrape_corporate(browser, "https://careers.mars.com/in/en/search-results?keywords=marketing", "Mars")
        
        all_jobs = linkedin_jobs + pepsi + mars
        
        with open('jobs.json', 'w') as f:
            json.dump(all_jobs, f, indent=4)
        await browser.close()
    print(f"Done. {len(all_jobs)} jobs processed.")

if __name__ == "__main__":
    asyncio.run(main())
