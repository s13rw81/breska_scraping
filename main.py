import asyncio
from playwright.sync_api import sync_playwright, expect
from config import URL_FOR_DRESSES
import re


async def main():
    import asyncio


from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()
        await page.goto(URL_FOR_DRESSES)
        print('page title ', await page.title())
        # find number of dresses in catagory
        await asyncio.sleep(10)
        # await expect(page.get_by_text("GO!")).to_be_visible()
        await page.get_by_role("button", name=re.compile("GO!", re.IGNORECASE)).click()
        # await page.locator(':nth-match(:text("abc"), 27)').click()
        await asyncio.sleep(10)
        await page.goto(URL_FOR_DRESSES)
        await asyncio.sleep(10)
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
