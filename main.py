import asyncio
import json
import re
from itertools import cycle

from config import log, BASE_URL, URL_FOR_DRESSES, WORKERS, FILE_PATH
from playwright.async_api import async_playwright


class Bershka:
    def __init__(self):
        log.info('scrapping Breshka using Python Playwright')
        self.catalog_count = 0
        self.browser = None
        self.context = None
        self.playwright = None
        self.main_page = None
        self.page_pool = None
        self.asyncio_tasks = list()
        self.links = ['/ww/halter-neckline-midi-dress-c0p159392243.html?colorId=251']
        self.pages = list()
        self.result = list()
        self.semaphore = asyncio.Semaphore(WORKERS)  # Limiting concurrent tasks to 2
        self.processed = list()

    async def launch_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False, args=["--start-maximized"])

    async def create_main_page(self):
        main_page_context = await self.browser.new_context(no_viewport=True)
        # await main_page_context.add_cookies(COOKIES)
        self.main_page = await main_page_context.new_page()
        await self.main_page.goto(BASE_URL, timeout=100000)
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
        self.pages.append(self.main_page)
        self.page_pool = cycle(self.pages)

    async def get_new_page(self):
        return next(self.page_pool)

    async def goto_section_dresses(self):
        log.info(f'navigating to {URL_FOR_DRESSES}')
        await self.main_page.goto(URL_FOR_DRESSES, timeout=100000)
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
        while itemc < 20:  # self.catalog_count:
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

    async def scrape_product_data(self, url, page=None, item_is_variation: bool = False) -> dict | None:
        if url in self.processed:
            log.info(f'urls already processed. {url}')
            return
        else:
            self.processed.append(url)

        log.info(f'item is variation : {item_is_variation}, variation url is : {url}')

        if page is None:
            page = await self.get_new_page()

        result = dict()

        # data point 1 : URL
        url = BASE_URL + url
        result['url'] = url
        await page.goto(url, timeout=100000)
        log.info(f"scraping : {url}")
        await page.wait_for_load_state('domcontentloaded')
        await page.wait_for_load_state('networkidle')
        # data point 2 : Item Name
        itemName = await page.locator("xpath=//*[@class='product-title']").inner_text()
        log.info(f'scraping : {url} | item name : {itemName}')
        result['item name'] = itemName
        # data point 3 : references ( color variations ) not reliable
        itemrefs = await page.locator("xpath=//*[@class='product-reference']").inner_text()
        log.info(f'scraping : {url} | item refs : {itemrefs}')
        result['description'] = itemrefs
        # data point 4 : sizes available
        itemSizes = await page.locator('.ui--dot-item.is-dot.is-naked').all()
        available_sizes = list()
        for size in itemSizes:
            aria_controls = await size.get_attribute('aria-controls')
            if aria_controls != 'aria-modal-NotifyMeModal':
                aria_label = await size.get_attribute('aria-label')
                log.info(f"scraping : {url} | sizes available : {aria_label}")
                available_sizes.append(aria_label)
        result['available sizes'] = available_sizes
        # data point 5 : sizes not in stock
        out_of_stock = list()
        itemSizeNA = await page.locator("xpath=//*[@class='ui--dot-item is-dot is-disabled is-naked']").all()
        for size in itemSizeNA:
            aria_label = await size.get_attribute('aria-label')
            log.info(f"scraping : {url} | sizes not available : {aria_label}")
            out_of_stock.append(aria_label)
        result['out of stock'] = out_of_stock
        # data point 6 : price in euros
        itemPrice = await page.locator("xpath=//*[@class='current-price-elem']").first.inner_text()
        log.info(f"scraping : {url} | item price : {itemPrice.split(' & ')[0]}")
        result['price'] = itemPrice
        # data point 7 : colour options
        # //*[@class='colors-bar']
        itemColours = await page.locator("xpath=//*[@class='colors-bar']").all()
        variations = [{}]
        if not item_is_variation:
            if len(itemColours) > 0:
                log.info(f'scraping : {url} | ITEM HAS VARIATIONS')
                links = await page.locator("xpath=//a[@role='option']").all()
                link_urls = [await link.get_attribute('href') for link in links]
                log.info(f'scraping : {url} | variation URLS are {link_urls}')
                for link in link_urls:
                    res = await self.scrape_product_data(url=link, item_is_variation=True)
                    # alt_name = await link.get_attribute('aria-label')
                    # variations.append(
                    #     {
                    #         'variation_url': await link.get_attribute('href'),
                    #         'variation_name': alt_name,
                    #         'variation_image_url': await page.locator(
                    #             f"xpath=//img[@alt='{alt_name}' and @class='image-item-wrapper__skeleton']").get_attribute(
                    #             'src')
                    #     }
                    # )
                    variations.append(res)
                    log.info(f'scraping : {url} | variation data of item is {variations}')
            else:
                variations.append({})
        result['variations'] = variations

        # data point 8: product image
        itemImg = await page.locator(
            "xpath=//img[@data-qa-anchor='pdpMainImage' and @class='image-item']").first.get_attribute('src')
        result['main_img'] = itemImg
        if not item_is_variation:
            self.result.append(result)
        log.info(f'scraping : {url} | final result is {result}')
        return result

    async def close_all(self):
        # Write dictionary to JSON file

        with open(FILE_PATH, "w") as json_file:
            json.dump(self.result, json_file)

        await self.context.close()
        await self.browser.close()
        await self.playwright.stop()


async def main():
    sc = Bershka()
    await sc.launch_browser()
    await sc.create_main_page()
    await sc.goto_section_dresses()
    # await sc.get_catalog_count()
    # await sc.load_all_items()
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
