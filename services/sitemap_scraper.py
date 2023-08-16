import os
import json
import aiohttp
import asyncio
import pandas as pd
from usp.tree import sitemap_tree_for_homepage
from datetime import datetime
from pathlib import Path


async def fetch_sitemap(session, url, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            # Fetch the sitemap tree for the given URL
            tree = sitemap_tree_for_homepage(url)

            # Extract URLs from the tree structure
            urls = []
            if tree:
                urls = [page.url for page in tree.all_pages()]

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
    semaphore = asyncio.Semaphore(20)
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
    output_path = Path("/savedDocuments") / filename

    # Save the data as a CSV
    pd.DataFrame(data).to_csv(output_path)
