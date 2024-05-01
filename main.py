import asyncio
import re
from itertools import cycle

from config import SLEEP_SHORT, SLEEP_LONG, log, BASE_URL, URL_FOR_DRESSES, WORKERS
from playwright.async_api import async_playwright


class Bershka:
    def __init__(self):
        self.page_pool = None
        self.catalog_count = 0
        self.links = list()
        self.main_page = None
        self.browser = None
        self.playwright = None
        self.pages = list()
        log.info('scrapping Breshka using Python Playwright')
        self.semaphore = asyncio.Semaphore(WORKERS)  # Limiting concurrent tasks to 4
        self.asyncio_tasks = list()

    async def launch_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False, args=["--start-maximized"])
    async def create_main_page(self):
        self.main_page = await self.browser.new_page(no_viewport=True)
        await self.main_page.goto(BASE_URL)
        log.info(f'page title {await self.main_page.title()}')
        await asyncio.sleep(SLEEP_LONG)
        await self.main_page.get_by_role("button", name=re.compile("GO!", re.IGNORECASE)).click()
        await asyncio.sleep(SLEEP_LONG)

    async def create_additional_pages(self):
        log.info('creating addition pages')
        for i in range(WORKERS):
            self.pages.append(await self.browser.new_page(no_viewport=True))
        self.page_pool = cycle(self.pages)
        # await self.main_page.bring_to_front()

    async def get_new_page(self):
        return next(self.page_pool)

    async def goto_section_dresses(self):
        log.info(f'navigating to {URL_FOR_DRESSES}')
        await self.main_page.goto(URL_FOR_DRESSES)
        await asyncio.sleep(SLEEP_LONG)
        log.info(f'page title {await self.main_page.title()}')
        await asyncio.sleep(SLEEP_LONG)
        await asyncio.sleep(SLEEP_LONG)

    async def get_catalog_count(self):
        await self.main_page.locator('.bskico-filter').click()
        await asyncio.sleep(SLEEP_SHORT)
        # //*[@class='bsk-button bsk-button--block bsk-button--center']
        items = await self.main_page.locator(
            "xpath=//*[@class='bsk-button bsk-button--block bsk-button--center']").all_inner_texts()
        # items = await page.get_by_role('.bsk-button bsk-button--block bsk-button--center').all_inner_texts()
        self.catalog_count = int(''.join([c for c in items[0] if c.isnumeric()]))
        log.info(f'total items in catalog : {self.catalog_count}')
        await self.main_page.click('#aria-button-drawer')

    async def load_all_items(self):
        itemc = 0
        while itemc < self.catalog_count:
            await self.main_page.keyboard.down('ArrowDown')
            itemc = await self.main_page.locator("xpath=//*[@class='grid-item normal']").count()

        # gather all item links
        links = await self.main_page.query_selector_all('a.grid-card-link')
        self.links = [await link.get_attribute('href') for link in links]

    async def scrape_task(self, url):
        async with self.semaphore:
            page = await self.get_new_page()  # Get the next available page from the pool
            await self.scrape_product_data(url, page)

    async def scrape_product_data(self, url, page):
        url = BASE_URL + url
        log.info(f"scraping : {url}")
        await page.goto(url)
        await asyncio.sleep(SLEEP_LONG)
        await page.get_by_role("button", name=re.compile("GO!", re.IGNORECASE)).click()
        await asyncio.sleep(SLEEP_SHORT)
        await page.goto(url)
        itemName = await page.locator("xpath=//*[@class='product-title']").inner_text()
        log.info(f'item name : {itemName}')
        itemrefs = await page.locator("xpath=//*[@class='product-reference']").inner_text()
        log.info(f'item refs : {itemrefs}')
        itemSizes = await page.query_selector_all('.ui--dot-item.is-dot.is-naked')
        log.info(f'item sizes :{itemSizes}')
        await asyncio.sleep(SLEEP_SHORT)
        for size in itemSizes:
            aria_controls = await size.get_attribute('aria-controls')
            if aria_controls != 'aria-modal-NotifyMeModal':
                aria_label = await size.get_attribute('aria-label')
                log.info(f"sizes available : {aria_label}")

        # //*[@class='ui--dot-item is-dot is-disabled is-naked']
        itemSizeNA = await page.query_selector_all("xpath=//*[@class='ui--dot-item is-dot is-disabled is-naked']")
        for size in itemSizeNA:
            aria_label = await size.get_attribute('aria-label')
            log.info(f"sizes not available : {aria_label}")

        itemPrice = await page.locator("xpath=//*[@class='current-price-elem']").first.inner_text()
        log.info(f"item price : {itemPrice.split(' & ')[0]}")

    async def close_all(self):
        self.browser.close()
        self.playwright.close()


async def main():
    sc = Bershka()
    await sc.launch_browser()
    await sc.create_main_page()
    await sc.goto_section_dresses()
    await sc.get_catalog_count()
    await sc.load_all_items()
    await sc.create_additional_pages()
    # Schedule scraping tasks
    for url in sc.links:

        task = asyncio.create_task(sc.scrape_task(url))
        sc.asyncio_tasks.append(task)

    # Wait for all tasks to complete
    await asyncio.gather(*sc.asyncio_tasks)
    await sc.close_all()


if __name__ == '__main__':
    asyncio.run(main())
