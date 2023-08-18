import os
import json
import aiohttp
import asyncio
import pandas as pd
from usp.tree import sitemap_tree_for_homepage
from datetime import datetime
from pathlib import Path
from flask_socketio import  emit


async def fetch_sitemap(session, url, semaphore: asyncio.Semaphore, processed_urls, total_urls):
    async with semaphore:
        try:
            # Fetch the sitemap tree for the given URL
            tree = sitemap_tree_for_homepage(url)

            # Extract URLs from the tree structure
            urls = []
            if tree:
                urls = [page.url for page in tree.all_pages()]

            processed_urls[0] += 1
            percentage = (processed_urls[0] / total_urls) * 100

            emit('progress', {'percentage': percentage})

            return url, urls

        except aiohttp.InvalidURL:
            print(f"Error fetching sitemap for {url}. Error: Invalid URL or relative URL provided.")
            return url, []
        except aiohttp.ClientConnectionError:
            print(f"Error fetching sitemap for {url}. Error: Cannot connect to host.")
            return url, []
        except Exception as e:
            print(f"Error fetching sitemap for {url}. Error: {e}")
            return url, []


async def get_urls_from_data_folder(urls, industryName):
    semaphore = asyncio.Semaphore(1)

    total_urls = len(urls)
    processed_urls = [0]

    # Creating an asynchronous session to fetch sitemaps
    async with aiohttp.ClientSession() as session:
        # Pass the semaphore to each fetch_sitemap task
        results = await asyncio.gather(*(fetch_sitemap(session, url, semaphore) for url in urls))

    # Preparing data to be stored in a DataFrame
    data = {'URL': [], 'SubURL': []}
    for main_url, sub_urls in results:
        for sub_url in sub_urls:
            data['URL'].append(main_url)
            data['SubURL'].append(sub_url)

    # Prepare the filename with a readable datetime format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{industryName}_{timestamp}.csv"

    # Use pathlib to handle paths
    output_dir = Path("savedDocuments")
    output_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist
    output_path = output_dir / filename
    # Save the data as a CSV
    pd.DataFrame(data).to_csv(output_path)
