import asyncio
import re
from itertools import cycle

from config import log, BASE_URL, URL_FOR_DRESSES, WORKERS
from playwright.async_api import async_playwright


class Bershka:
    def __init__(self):
        log.info('scrapping Breshka using Python Playwright')
        self.page_pool = None
        self.catalog_count = 0
        self.links = list()
        self.main_page = None
        self.browser = None
        self.playwright = None
        self.pages = list()
        self.semaphore = asyncio.Semaphore(WORKERS)  # Limiting concurrent tasks to 2
        self.asyncio_tasks = list()
        self.context = None

    async def launch_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False, args=["--start-maximized"])

    async def create_main_page(self):
        main_page_context = await self.browser.new_context(no_viewport=True)
        # await main_page_context.add_cookies(COOKIES)
        self.main_page = await main_page_context.new_page()
        await self.main_page.goto(BASE_URL)
        await self.main_page.wait_for_load_state('domcontentloaded')
        await self.main_page.wait_for_load_state('networkidle')
        log.info(f'page title {await self.main_page.title()}')
        await self.main_page.get_by_role("button", name=re.compile("GO!", re.IGNORECASE)).click()
        await self.main_page.wait_for_load_state('domcontentloaded')
        await self.main_page.wait_for_load_state('networkidle')
        self.context = main_page_context

    async def create_additional_pages(self):
        log.info('creating addition pages')
        for i in range(WORKERS):
            new_page = await self.context.new_page()
            self.pages.append(new_page)

        self.page_pool = cycle(self.pages)

    async def get_new_page(self):
        return next(self.page_pool)

    async def goto_section_dresses(self):
        log.info(f'navigating to {URL_FOR_DRESSES}')
        await self.main_page.goto(URL_FOR_DRESSES)
        await self.main_page.wait_for_load_state('domcontentloaded')
        await self.main_page.wait_for_load_state('networkidle')

        log.info(f'page title {await self.main_page.title()}')


    async def get_catalog_count(self):
        filter_btn = self.main_page.locator('.bskico-filter')
        await filter_btn.wait_for()
        await filter_btn.click()

        item_count = self.main_page.locator("xpath=//*[@class='bsk-button bsk-button--block bsk-button--center']")
        await item_count.wait_for()
        items = await item_count.all_inner_texts()

        self.catalog_count = int(''.join([c for c in items[0] if c.isnumeric()]))
        log.info(f'total items in catalog : {self.catalog_count}')
        await self.main_page.click('#aria-button-drawer')

    async def load_all_items(self):
        itemc = 0
        while itemc < 40: #self.catalog_count:
            itemc = await self.main_page.locator("xpath=//*[@class='grid-item normal']").count()
            await self.main_page.wait_for_load_state('domcontentloaded')
            await self.main_page.wait_for_load_state('networkidle')

            await self.main_page.keyboard.press('ArrowDown')
            await self.main_page.keyboard.press('ArrowDown')
            await self.main_page.keyboard.press('ArrowDown')
            await self.main_page.keyboard.press('ArrowDown')
            await self.main_page.keyboard.press('ArrowDown')
            await self.main_page.keyboard.press('ArrowDown')
            await self.main_page.keyboard.press('ArrowDown')
            await self.main_page.keyboard.press('ArrowDown')
            await self.main_page.keyboard.press('ArrowDown')
            await self.main_page.keyboard.press('ArrowDown')
            await asyncio.sleep(1)
            log.info(f'counted {itemc} items')

        # gather all item links
        links = await self.main_page.query_selector_all('a.grid-card-link')
        self.links = [await link.get_attribute('href') for link in links]

    async def scrape_task(self, url):
        async with self.semaphore:
            page = await self.get_new_page()  # Get the next available page from the pool
            await self.scrape_product_data(url, page)

    async def scrape_product_data(self, url, page):
        url = BASE_URL + url
        await page.goto(url)
        log.info(f"scraping : {url}")
        await page.wait_for_load_state('domcontentloaded')
        await page.wait_for_load_state('networkidle')
        itemName = await page.locator("xpath=//*[@class='product-title']").inner_text()
        log.info(f'item name : {itemName}')
        itemrefs = await page.locator("xpath=//*[@class='product-reference']").inner_text()
        log.info(f'item refs : {itemrefs}')
        itemSizes = await page.locator('.ui--dot-item.is-dot.is-naked').all()
        for size in itemSizes:
            aria_controls = await size.get_attribute('aria-controls')
            if aria_controls != 'aria-modal-NotifyMeModal':
                aria_label = await size.get_attribute('aria-label')
                log.info(f"sizes available : {aria_label}")

        itemSizeNA = await page.locator("xpath=//*[@class='ui--dot-item is-dot is-disabled is-naked']").all()
        for size in itemSizeNA:
            aria_label = await size.get_attribute('aria-label')
            log.info(f"sizes not available : {aria_label}")

        itemPrice = await page.locator("xpath=//*[@class='current-price-elem']").first.inner_text()
        log.info(f"item price : {itemPrice.split(' & ')[0]}")

    async def close_all(self):
        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()


async def main():
    sc = Bershka()
    await sc.launch_browser()
    await sc.create_main_page()
    await sc.goto_section_dresses()
    await sc.get_catalog_count()
    await sc.load_all_items()
    await sc.create_additional_pages()
    # Schedule scraping tasks
    for url in sc.links[:10]:
        # await sc.scrape_product_data(url)
        task = asyncio.create_task(sc.scrape_task(url))
        sc.asyncio_tasks.append(task)

    # Wait for all tasks to complete
    await asyncio.gather(*sc.asyncio_tasks)
    await sc.close_all()


if __name__ == '__main__':
    asyncio.run(main())
