# todo gerer les erreurs des request et logger, voir si retry ou pas (limiter)
# todo rajouter en fin de programme si visualisation des erreurs

import asyncio

import aiohttp
import aiohttp.client_exceptions
from bs4 import BeautifulSoup, SoupStrainer



BASE_URL = "https://books.toscrape.com/"
LINK_STRAINER = SoupStrainer('section')
BOOK_STRAINER = SoupStrainer(class_='col-sm-6 product_main') # Warning : Take only the product info, not image link
BOOKS = []


# Custom request with error control
async def fetch(session: aiohttp.ClientSession, url: str) -> str | None:
    try:
        async with session.get(url) as response:
            if response.status == 200:
                html = await response.text()
            else:
                print(f'Fetch error {response.status} for url : {url}')
                return None
    except aiohttp.client_exceptions.ClientConnectorError:
        print(f'Client connection error')
    else:
        return html
    

# Get url for each category in the home page nav bar
async def get_categories_links(session: aiohttp.ClientSession) -> list | None:
    if html := await fetch(session, BASE_URL):
        nav = SoupStrainer(class_="nav nav-list")
        soup = BeautifulSoup(html, 'html.parser', parse_only=nav)
        categories_links = [link.get('href') for link in soup.findAll('a')]
        return categories_links[1:]


# Get links of all books in every pages for one category 
async def get_links_by_category(session: aiohttp.ClientSession, category_url: str) -> list | None:
    next_page = True
    links = []
    while next_page:
        if html:= await fetch(session, BASE_URL + category_url):
            soup = BeautifulSoup(html, 'html.parser', parse_only=LINK_STRAINER)
            for line in soup.findAll("h3"):
                links.append(f"{BASE_URL}catalogue{line.a['href'][8:]}")
            if next_page := soup.find(class_='next'):
                category_url = "/".join(category_url.split('/')[:-1]) + f"/{next_page.a['href']}"
            else:
                return links
        else:
            print(f'Category url: {category_url} not found')
            next_page = False


# Get title, price and availability for each book in category
async def get_data_by_category(session: aiohttp.ClientSession, category_url: str) -> None:
    links = await get_links_by_category(session, category_url)
    if links:
        category_name = category_url.split('/')[-2].split('_')[0]
        for link in links:
            html = await fetch(session, link)
            if html:
                soup = BeautifulSoup(html, 'html.parser', parse_only=BOOK_STRAINER)
                title = soup.find('h1').text
                price = soup.find(class_='price_color').text
                available = soup.find(class_="instock availability").text.strip()
                book_data = {'title': title, 'price': price, 'available': available}
                for key, value in book_data.items():
                    if not value:
                        print(f'In category {category_name} the {key} value is not available')
                        book_data[key] = 'None'
                BOOKS.append(book_data)
        print(f'{category_name} download complete !')
    else:
        # todo log error no links category
        pass


async def main():
    async with aiohttp.ClientSession() as session:
        categories = await get_categories_links(session)
        if categories:
            tasks = [get_data_by_category(session, category) for category in categories[:10]] # limiter a 10 pour tests
            await asyncio.gather(*tasks)
            print("Download complete !")
        else:
            # todo log error
            pass


if __name__ == '__main__':
    asyncio.run(main())