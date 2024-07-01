import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv

async def fetch(session, url):
    """
    Fetch the content of a given URL.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        url (str): The URL to fetch.

    Returns:
        str: The response text if the request is successful.
        None: If the request fails.
    """
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Error: Received status code {response.status} for URL: {url}")
                return None
    except aiohttp.ClientError as e:
        print(f"Client error: {e} for URL: {url}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e} for URL: {url}")
        return None

async def process_url(session, url, englishName, mesh, uniqueID):
    """
    Process a URL to extract the French name and write it to a CSV file.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        url (str): The URL to process.
        englishName (str): The english name associated with the URL.
        mesh (str): The MeSH code associated with the URL.
        uniqueID (str): The unique id associated with the URL.
    """
    while True:
        response = await fetch(session, url)
        if response:
            soup = BeautifulSoup(response, 'html.parser')
            responses = soup.find('span', {'class' : 'dbotitle-label'})
            if responses:
                frenchName = responses.get_text()
                with open('meshNewData.bin', 'a', encoding="utf-8", newline='') as f:
                    writer = csv.writer(f, delimiter='|')
                    writer.writerow([frenchName, englishName, mesh, uniqueID])
                print(f"Processed: {englishName} - {mesh} - {uniqueID}")
            else:
                print(f"No french name found for {englishName} - {mesh} - {uniqueID}")
            break  # Exit the loop if successful
        else:
            print(f"Retrying for {englishName} - {mesh} - {uniqueID}")
            await asyncio.sleep(1)  # Wait a bit before retrying

async def getFrenchName():
    """
    Read the MeSH data from files and process each URL to extract the MeSH Unique ID.
    """
    # Read existing data to avoid duplicate processing
    with open('meshNewData.bin', 'r', encoding="utf-8", newline='') as meshTree:
        mesh2 = meshTree.read().splitlines()
        mesh2 = [line.split("|")[1:] for line in mesh2]

    # Read new data to process
    with open('meshData.bin', 'r', encoding="utf-8", newline='') as meshTree:
        mesh = meshTree.read().splitlines()
        mesh = [line.split("|") for line in mesh]

    # Filter out already processed entries
    mesh = [[title, mesh, code] for title, mesh, code in mesh if [title, mesh, code] not in mesh2]

    # Create aiohttp session and process URLs
    async with aiohttp.ClientSession() as session:
            tasks = []
            for englishName, mesh, uniqueID in mesh:
                url = f" https://www.hetop.eu/hetop/fr/?rr=MSH_{uniqueID[0]}_{uniqueID[1:]}&q=MSH_{uniqueID[0]}_{uniqueID[1:]}"
                tasks.append(asyncio.create_task(process_url(session, url, englishName, mesh, uniqueID)))

            await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(getFrenchName())
