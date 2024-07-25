import os
import re
import csv
from datetime import datetime

import asyncio
import aiofiles
from aiocsv import AsyncDictWriter
import aiohttp
from bs4 import BeautifulSoup, SoupStrainer

from utils import fetch, Progress

DATA_PATH = os.path.join(os.getcwd(), 'data')
CURRENT_DATA_PATH = os.path.join(DATA_PATH, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
BASE_URL = "https://books.toscrape.com/"
LINK_STRAINER = SoupStrainer('section')
FIELDNAMES = [
    'product_page_url',
    'universal_product_code',
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


# Function to get the URL for each category in the homepage navigation bar
async def get_categories_links(session: aiohttp.ClientSession) -> list | None:
    if html := await fetch(session, BASE_URL):
        nav = SoupStrainer(class_="nav nav-list")
        soup = BeautifulSoup(html, 'html.parser', parse_only=nav)
        categories_links = [link.get('href') for link in soup.findAll('a')]
        return categories_links[1:]


# Function to get url of all books in every page for selected category
async def get_links_by_category(session: aiohttp.ClientSession, category_url: str) -> list | None:
    next_page = True
    links = []
    while next_page:
        if html := await fetch(session, BASE_URL + category_url):
            soup = BeautifulSoup(html, 'html.parser', parse_only=LINK_STRAINER)
            for line in soup.findAll("h3"):
                links.append(f"{BASE_URL}catalogue{line.a['href'][8:]}")
            # check if other pages exist
            if next_page := soup.find(class_='next'):
                category_url = "/".join(category_url.split('/')[:-1]) + f"/{next_page.a['href']}"
            else:
                return links
        else:
            print(f'Category url: {category_url} not found\n')
            next_page = False


# Function to get data for each book in a category, save the data to a CSV file, and save the images
async def get_data_by_category(session: aiohttp.ClientSession, category_url: str, progress: Progress) -> None:
    if links := await get_links_by_category(session, category_url):
        category_name = category_url.split('/')[-2].split('_')[0]

        # Create a directory for images and define the path of the CSV file
        category_path = os.path.join(CURRENT_DATA_PATH, category_name)
        os.mkdir(category_path)
        os.mkdir(os.path.join(category_path, category_name + '_img'))
        csv_path = f'{CURRENT_DATA_PATH}/{category_name}/{category_name}.csv'

        async with aiofiles.open(csv_path, mode='w', encoding='utf-8', newline='') as csvfile:
            writer = AsyncDictWriter(csvfile, FIELDNAMES, restval="NULL", quoting=csv.QUOTE_ALL)
            await writer.writeheader()
            for link in links:
                if html := await fetch(session, link):
                    soup = BeautifulSoup(html, 'html.parser')
                    table_content = [content.text for content in soup.findAll('td')]
                    description_title = soup.find(id='product_description')
                    description = description_title.find_next('p').text if description_title else ''
                    data = {
                        'product_page_url': link,
                        'universal_product_code': table_content[0],
                        'title': soup.find('h1').text,
                        'price_including_tax': table_content[3],
                        'price_excluding_tax': table_content[2],
                        'number_available': re.findall(r'\d+', table_content[5])[0],
                        'product_description': description,
                        'category': category_name,
                        'review_rating': table_content[-1],
                        'image_url': soup.find(class_='item active').find('img')['src'].replace('../../', BASE_URL)
                    }
                    await save_data(session, writer, data)
        progress.up()
    else:
        print(f'Get data fail to url {category_url}\n')


# Function to save data to a CSV file and download images
async def save_data(session: aiohttp.ClientSession, writer: aiofiles, data: dict) -> None:
    # add new data to csv file
    await writer.writerow(data)
    # download image
    url = data.get('image_url')
    category = data.get('category')
    ipc = data.get('universal_ product_code')
    file_path = f'{CURRENT_DATA_PATH}/{category}/{category}_img/{ipc}.jpg'
    async with session.get(url) as response:
        if response.status == 200:
            with open(file_path, 'wb') as file:
                async for chunk in response.content.iter_chunked(1024):
                    file.write(chunk)
        else:
            print(f'download image of ipc n°{ipc} failed\n')


async def main():
    """
    Main function to asynchronously fetch and process book data from multiple categories.
    - Establishes an HTTP session using aiohttp.
    - Retrieves all category links.
    - Downloads and saves book data and images for each category.
    """ 
    async with aiohttp.ClientSession() as session:
        print('Get all categories...')
        if categories := await get_categories_links(session):
            print('Download and save all books data and images.')
            progress_bar = Progress('Download and save', len(categories))
            tasks = [get_data_by_category(session, category, progress_bar) for category in categories]
            await asyncio.gather(*tasks)
            print('Books scraping complete !')
        else:
            print('Get categories urls failure\n')


if __name__ == '__main__':
    asyncio.run(main())
