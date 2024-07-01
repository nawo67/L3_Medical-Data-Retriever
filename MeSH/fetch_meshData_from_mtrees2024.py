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

async def process_url(session, url, title, code):
    """
    Process a URL to extract the MeSH Unique ID and write it to a CSV file.

    Args:
        session (aiohttp.ClientSession): The aiohttp client session.
        url (str): The URL to process.
        title (str): The title associated with the URL.
        code (str): The MeSH code associated with the URL.
    """
    while True:
        response = await fetch(session, url)
        if response:
            soup = BeautifulSoup(response, 'html.parser')
            responses = soup.find(lambda tag: tag.name == "p" and "MeSH Unique ID:" in tag.text)
            if responses:
                uniqueID = responses.get_text().split(": ")[-1]
                with open('meshData.bin', 'a', encoding="utf-8", newline='') as f:
                    writer = csv.writer(f, delimiter='|')
                    writer.writerow([title, code, uniqueID])
                print(f"Processed: {title} - {code}")
            else:
                print(f"No unique ID found for {title} - {code}")
            break  # Exit the loop if successful
        else:
            print(f"Retrying for {title} - {code}")
            await asyncio.sleep(1)  # Wait a bit before retrying

async def getUniqueID():
    """
    Read the MeSH data from files and process each URL to extract the MeSH Unique ID.
    """
    # Read existing data to avoid duplicate processing
    with open('meshData.bin', 'r', encoding="utf-8", newline='') as meshTree:
        mesh2 = meshTree.read().splitlines()
        mesh2 = [line.split("|")[:2] for line in mesh2]

    # Read new data to process
    with open('mtrees2024.bin', 'r', encoding="utf-8", newline='') as meshTree:
        mesh = meshTree.read().splitlines()
        mesh = [line.split(";") for line in mesh]

    # Filter out already processed entries
    mesh = [[title, code] for title, code in mesh if [title, code] not in mesh2]

    # Create aiohttp session and process URLs
    async with aiohttp.ClientSession() as session:
            tasks = []
            for title, code in mesh:
                url = f"https://www.ncbi.nlm.nih.gov/mesh/{code}"
                tasks.append(asyncio.create_task(process_url(session, url, title, code)))

            await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(getUniqueID())
