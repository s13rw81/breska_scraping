import asyncio
import re

from config import URL_FOR_DRESSES, SLEEP_SHORT, SLEEP_LONG, BASE_URL
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(no_viewport=True)
        await page.goto(URL_FOR_DRESSES)
        print('page title ', await page.title())
        # find number of dresses in catagory
        await asyncio.sleep(SLEEP_LONG)
        # await expect(page.get_by_text("GO!")).to_be_visible()
        await page.get_by_role("button", name=re.compile("GO!", re.IGNORECASE)).click()
        # await page.locator(':nth-match(:text("abc"), 27)').click()
        await asyncio.sleep(SLEEP_LONG)
        await page.goto(URL_FOR_DRESSES)
        await asyncio.sleep(SLEEP_SHORT)
        # get count of items in catagory
        await page.locator('.bskico-filter').click()
        await asyncio.sleep(SLEEP_SHORT)
        # //*[@class='bsk-button bsk-button--block bsk-button--center']
        items = await page.locator(
            "xpath=//*[@class='bsk-button bsk-button--block bsk-button--center']").all_inner_texts()
        # items = await page.get_by_role('.bsk-button bsk-button--block bsk-button--center').all_inner_texts()
        print(items, type(items))
        res = int(''.join([c for c in items[0] if c.isnumeric()]))
        print(res, type(res))
        # //*[@class='touch-area-wrapper bsk-drawer__close is-naked']
        await page.click('#aria-button-drawer')
        # await page.locator('.touch-area-wrapper bsk-drawer__close is-naked').click()

        # now start picking cotton
        # scroll to the bottom of the page
        itemc = 0

        while itemc < res:
            await page.keyboard.down('ArrowDown')
            itemc = await page.locator("xpath=//*[@class='grid-item normal']").count()
            print(itemc, type(itemc))

        links = await page.query_selector_all('a.grid-card-link')
        links = [await link.get_attribute('href') for link in links]

        # loop through the pages
        for link in links[:10]:
            url = BASE_URL + link
            print(url)
            await page.goto(url)
            await asyncio.sleep(SLEEP_LONG)
            itemName = page.get_by_role('h1').inner_text()
            print(itemName)

        await asyncio.sleep(SLEEP_LONG)
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
