import asyncio
from playwright.async_api import async_playwright
import json

async def scrape_nestle(browser):
    page = await browser.new_page()
    jobs = []
    try:
        # Direct India Jobs URL
        await page.goto("https://www.nestle.in/jobs/search-jobs?keyword=&country=IN&location=&career_area=All", wait_until="networkidle")
        await page.wait_for_selector(".job-title")
        
        job_elements = await page.query_selector_all(".jobs-list-item") # Nestlé list selector
        for job in job_elements:
            title = await job.query_selector(".job-title")
            link = await job.query_selector("a")
            loc = await job.query_selector(".job-location")
            
            if title and link:
                jobs.append({
                    "title": await title.inner_text(),
                    "company": "Nestlé India",
                    "location": await loc.inner_text() if loc else "India",
                    "link": "https://www.nestle.in" + await link.get_attribute("href"),
                    "category": "FMCG",
                    "date": "Direct"
                })
    except Exception as e: print(f"Nestle Error: {e}")
    return jobs

async def scrape_unilever(browser):
    page = await browser.new_page()
    jobs = []
    try:
        await page.goto("https://careers.unilever.com/en/india", wait_until="networkidle")
        await page.wait_for_selector(".jobs-list-item")
        
        job_elements = await page.query_selector_all(".jobs-list-item")
        for job in job_elements:
            title = await job.query_selector(".job-title")
            loc = await job.query_selector(".job-location")
            link = await job.query_selector("a")
            
            if title:
                jobs.append({
                    "title": await title.inner_text(),
                    "company": "Unilever India",
                    "location": await loc.inner_text() if loc else "India",
                    "link": await link.get_attribute("href"),
                    "category": "FMCG",
                    "date": "Direct"
                })
    except Exception as e: print(f"Unilever Error: {e}")
    return jobs

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Add your previous scrapers (Coke, Pepsi, etc.) here as well
        nestle_jobs = await scrape_nestle(browser)
        unilever_jobs = await scrape_unilever(browser)
        
        all_data = nestle_jobs + unilever_jobs
        with open('jobs.json', 'w') as f:
            json.dump(all_data, f, indent=4)
        await browser.close()
        print(f"Scraped {len(all_data)} FMCG roles.")

if __name__ == "__main__":
    asyncio.run(main())
