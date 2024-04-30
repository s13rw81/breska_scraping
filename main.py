url = 'https://www.bershka.com/ww/women/clothes/dresses-c1010193213.html'
url1 = 'https://www.instagram.com'
import asyncio
from playwright.sync_api import sync_playwright


async def main():

    import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        page = await browser.new_page()
        await page.goto(url)
        print('page title ', await page.title())
        await browser.close()

asyncio.run(main())



if __name__ == '__main__':
    asyncio.run(main())