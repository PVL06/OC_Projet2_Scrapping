import os
import re
import csv
from datetime import datetime

import asyncio
import aiofiles
from aiocsv import AsyncDictWriter
import aiohttp
import aiohttp.client_exceptions
from bs4 import BeautifulSoup, SoupStrainer

DATA_PATH = os.path.join(os.getcwd(), 'data')
CURRENT_DATA_PATH = os.path.join(DATA_PATH, datetime.now().strftime("%Y%m%d%H%M%S"))
BASE_URL = "https://books.toscrape.com/"
LINK_STRAINER = SoupStrainer('section')
FIELDNAMES = [
    'product_page_url',
    'universal_ product_code',
    'title',
    'price_including_tax',
    'price_excluding_tax',
    'number_available',
    'product_description',
    'category',
    'review_rating',
    'image_url',
    ]

if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)
os.mkdir(CURRENT_DATA_PATH)


# Custom request function with error control
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


# Get link of all books in every page for selected category 
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


# Get data for each book in category
async def get_data_by_category(session: aiohttp.ClientSession, category_url: str) -> None:
    if links := await get_links_by_category(session, category_url):
        category_name = category_url.split('/')[-2].split('_')[0]

        category_path = os.path.join(CURRENT_DATA_PATH, category_name)
        os.mkdir(category_path)
        os.mkdir(os.path.join(category_path, category_name + '_img'))
        file_path = f'{CURRENT_DATA_PATH}/{category_name}/{category_name}.csv'

        async with aiofiles.open(file_path, mode='w', encoding='utf-8', newline='') as csvfile:
            writer = AsyncDictWriter(csvfile, FIELDNAMES, restval="NULL", quoting=csv.QUOTE_ALL)
            await writer.writeheader()
            for link in links:
                if html := await fetch(session, link):
                    soup = BeautifulSoup(html, 'html.parser')
                    title = soup.find('h1').text
                    table_content = [content.text for content in soup.findAll('td')]
                    description_title = soup.find(id='product_description')
                    description = description_title.find_next('p').text if description_title else ''
                    img_url = soup.find(class_='item active').find('img')['src'].replace('../../', BASE_URL)
                    data = {
                        'product_page_url': link,
                        'universal_ product_code': table_content[0],
                        'title': title,
                        'price_including_tax': table_content[3],
                        'price_excluding_tax': table_content[2],
                        'number_available': re.findall(r'\d+', table_content[5])[0],
                        'product_description': description,
                        'category': category_name,
                        'review_rating': table_content[-1],
                        'image_url': img_url
                    }
                    await writer.writerow(data)
                    await get_img(session, img_url, category_name, title)
        print(f'{category_name} download complete !')
    else:
        print(f'Get data fail to url {link}')

# Downloading image and save
async def get_img(session, url, category, title):
    pattern = re.compile("[:',.#;!?%&()#/\"* ]")
    formated_title = pattern.sub('_', title)
    file_path = f'{CURRENT_DATA_PATH}/{category}/{category}_img/{formated_title}.jpg'
    async with session.get(url) as response:
        if response.status == 200:
            with open(file_path, 'wb') as file:
                async for chunk in response.content.iter_chunked(10):
                    file.write(chunk)



async def main():
    async with aiohttp.ClientSession() as session:
        if categories := await get_categories_links(session):
            tasks = [get_data_by_category(session, category) for category in categories] # limiteur pour tests
            await asyncio.gather(*tasks)
            print("Full download complete !")
        else:
            print('Get categories url failure')


if __name__ == '__main__':
    asyncio.run(main())