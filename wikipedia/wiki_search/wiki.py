import aiohttp
from bs4 import BeautifulSoup

async def fetch(url, params):
    """
    Fetches JSON data of a given URL with parameters asynchronously.

    Args:
        url (str): The URL to fetch.
        params (dict): The parameters for the GET request.

    Returns:
        dict: JSON data retrieved from the URL.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params or {}) as response:
            return await response.json()

async def fetch(url):
    """
    Fetches the content of a given URL asynchronously.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The text content of the response.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
        
async def get_content_from_title_via_api(title, langage):
    """
    Retrieves content from the Wikipedia API based on the given title and language.

    Args:
        title (str): The title of the Wikipedia page to retrieve.
        langage (int): Language identifier (1 for French, 0 for English).

    Returns:
        tuple: A tuple containing the title, link, and content of the Wikipedia page if successful,
               or (None, None, None) if no content is found.
    """
    if langage == 1:
        url = "https://fr.wikipedia.org/w/api.php"
    else :            
        url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": "",
        "titles": title,
        "redirects": 1
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                page = next(iter(data['query']['pages'].values()))
                if 'extract' in page:
                    title_in_wiki = page['title']
                    link = "https://en.wikipedia.org/wiki/" + title_in_wiki.replace(" ", "_")
                    content = page['extract']
                    if content.strip() == '':
                        return None, None, None
                    return title_in_wiki, link, content
            else:
                print("Erreur de récupération")
    return None, None, None

async def get_french_link(english_link):
    """
    Retrieves the link to the French language version of a Wikipedia page given its English link.

    Args:
        english_link (str): The link to the English Wikipedia page.

    Returns:
        str: The link to the corresponding French Wikipedia page if found, otherwise None.
    """
    response = await fetch(english_link)
    soup = BeautifulSoup(response, 'html.parser')
    links_langage = soup.find_all('a', class_='interlanguage-link-target')
    french_link = None
    for link_l in links_langage:
        if 'Français' in link_l.text:
            french_link = link_l.get('href')
    return french_link
        
async def save_to_csv(link, mesh, UI, title, content, filename, writer):
    """
    Saves data to a CSV file asynchronously.

    Args:
        link (str): The link to the Wikipedia page.
        mesh (str): The MeSH codes associated with the content.
        UI (str): The Unique ID associated with the content.
        title (str): The title of the Wikipedia page.
        content (str): The content of the Wikipedia page.
        filename (str): The name of the CSV file to save the data to.
        writer (csv.writer): The CSV writer object.

    Returns:
        None
    """
    await writer.writerow([link, mesh, UI, title, content])
    bold = '\033[1m'
    end = '\033[0m'
    underline = '\033[4m'
    print(f"{bold}{underline}WIKIPEDIA :{end} Data from {bold}{title, mesh, UI}{end} successfully saved in {bold}{filename}.csv{end} .")