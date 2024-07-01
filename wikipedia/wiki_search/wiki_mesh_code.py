import csv
import os
import aiofiles
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from MeSH.meshData_func import depthMeshCode, MeshToUniqueID, UniqueIDToMesh
import wikipedia.wiki_search.wiki as wiki
from PyQt5.QtWidgets import QApplication

# Constants for styling console output
bold = '\033[1m'
end = '\033[0m'
underline = '\033[4m'
red = '\033[91m'


nb_tasks = 0
nb_tasks_done = 0
successed_tasks = 0
failed_tasks = 0

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

async def get_wiki_data_mesh_code(mesh, meshTree, pbar, wikiProgressLabel, french_or_english):
    """
    Retrieves Wikipedia data for a given MeSH code.

    Args:
        mesh (str): The MeSH code to search for.
        meshTree (list): The list representing the MeSH tree structure.
        pbar: Progress bar for displaying progress.
        wikiProgressLabel: Label for displaying progress.
        french_or_english: Flag indicating whether to fetch French (1) or English (0) content.

    Returns:
        tuple: A tuple containing the link, MeSH code, UI, title, and content if successful.
        bool: False if the data could not be retrieved.
    """
    global nb_tasks
    global nb_tasks_done
    global failed_tasks
    global successed_tasks
    main_code = mesh[:3]
    url = f"https://en.wikipedia.org/wiki/List_of_MeSH_codes_({main_code})"
    response = await fetch(url)
    soup = BeautifulSoup(response, 'html.parser')    
    div = soup.find('div', {'class': 'mw-parser-output'})
    ui = None
    en_link = None
    for li in div.find_all('li') + div.find_all('h3'):
        if (mesh + " ") in li.text:
            li_elements = li.find_all('li')
            if not li_elements:
                all_a = li.find_all('a')
                if len(all_a) < 3:
                    print(f"{red}{bold}{underline}WIKIPEDIA :{end}{red}{bold} Error :{end}{red} Pas de page Wikipédia correspondant au code meSH : {bold}{mesh}{end}")
                    nb_tasks_done += 1
                    failed_tasks += 1
                    pbar.setValue(int(nb_tasks_done/nb_tasks*100))
                    wikiProgressLabel.setText(f"WIKIPEDIA {int(nb_tasks_done/nb_tasks*100)}% [Failed : {failed_tasks} Done : {successed_tasks}] {nb_tasks_done} / {nb_tasks}")
                    QApplication.processEvents()
                    return False
                second_a_tag = all_a[2]
                en_link = "https://en.wikipedia.org" + second_a_tag['href']

    if en_link is None:
        print(f"{red}{bold}{underline}WIKIPEDIA :{end}{red}{bold} Error :{end}{red} Pas de page Wikipédia correspondant au code meSH : {bold}{mesh}{end}")
        nb_tasks_done += 1
        failed_tasks += 1
        pbar.setValue(int(nb_tasks_done / nb_tasks * 100))
        wikiProgressLabel.setText(f"WIKIPEDIA {int(nb_tasks_done/nb_tasks*100)}% [Failed : {failed_tasks} Done : {successed_tasks}] {nb_tasks_done} / {nb_tasks}")
        QApplication.processEvents()
        return False
    
    if french_or_english == 1 :
        link = await wiki.get_french_link(en_link)
        if link==None:
            print(f"{red}{bold}{underline}WIKIPEDIA :{end}{red}{bold} Error :{end}{red} Pas de page Wikipédia correspondant au code meSH : {bold}{mesh}{end}")
            nb_tasks_done += 1
            failed_tasks += 1
            pbar.setValue(int(nb_tasks_done/nb_tasks*100))
            wikiProgressLabel.setText(f"WIKIPEDIA {int(nb_tasks_done/nb_tasks*100)}% [Failed : {failed_tasks} Done : {successed_tasks}] {nb_tasks_done} / {nb_tasks}")
            QApplication.processEvents()
            return False
        response = await fetch(link)
    if french_or_english == 0 :
        response = await fetch(en_link)
    soup = BeautifulSoup(response, 'html.parser')
    span_tag = soup.find('span', class_='mw-page-title-main')
    title = None
    ui = MeshToUniqueID(mesh, meshTree)[0]
    mesh = UniqueIDToMesh(ui, meshTree)
    mesh = ';'.join(mesh)
    if span_tag:
        title = span_tag.string.strip()
    if title:
        wiki_content = await wiki.get_content_from_title_via_api(title,french_or_english)
        if wiki_content != (None, None, None):
            title, link, content = wiki_content
            nb_tasks_done += 1
            successed_tasks += 1
            pbar.setValue(int(nb_tasks_done/nb_tasks*100))
            wikiProgressLabel.setText(f"WIKIPEDIA {int(nb_tasks_done/nb_tasks*100)}% [Failed : {failed_tasks} Done : {successed_tasks}] {nb_tasks_done} / {nb_tasks}")
            QApplication.processEvents()
            return link, mesh, ui, title, content
        else:
            print(f"{red}{bold}{underline}WIKIPEDIA :{end}{red}{bold} Error :{end}{red} Pas de page Wikipédia correspondant au code meSH : {bold}{mesh}{end}")
            nb_tasks_done += 1
            failed_tasks += 1
            pbar.setValue(int(nb_tasks_done/nb_tasks*100))
            wikiProgressLabel.setText(f"WIKIPEDIA {int(nb_tasks_done/nb_tasks*100)}% [Failed : {failed_tasks} Done : {successed_tasks}] {nb_tasks_done} / {nb_tasks}")
            QApplication.processEvents()
            return False
    else:
        print(f"{red}{bold}{underline}WIKIPEDIA :{end}{red}{bold} Error :{end}{red} Pas de page Wikipédia correspondant au code meSH : {bold}{mesh}{end}")
        nb_tasks_done += 1
        failed_tasks +=1
        pbar.setValue(int(nb_tasks_done/nb_tasks*100))
        wikiProgressLabel.setText(f"WIKIPEDIA {int(nb_tasks_done/nb_tasks*100)}% [Failed : {failed_tasks} Done : {successed_tasks}] {nb_tasks_done} / {nb_tasks}")
        QApplication.processEvents()
        return False         

async def launch(topic, depth, filename, openType, meshTree, pbar, wikiProgressLabel, french , english):
    """
    Launches the process to retrieve Wikipedia data for MeSH codes related to a topic.

    Args:
        topic (str): The topic to search for.
        depth (int): The depth of the MeSH tree to search.
        filename (str): The name of the output CSV file.
        openType (str): The mode in which the file is opened.
        meshTree (list): The list representing the MeSH tree structure.
        pbar: Progress bar for displaying progress.
        wikiProgressLabel: Label for displaying progress.
        french: Flag indicating whether to fetch French content.
        english: Flag indicating whether to fetch English content.
    """
    global nb_tasks
    global nb_tasks_done
    global failed_tasks
    global successed_tasks
    nb_tasks_done = 0
    failed_tasks = 0
    successed_tasks = 0
    meshs = depthMeshCode(topic, depth, meshTree)
    french_tasks = []
    english_tasks = []
    for mesh in meshs:
        if french:
            french_tasks.append(get_wiki_data_mesh_code(mesh, meshTree, pbar, wikiProgressLabel, 1))
        if english:
            english_tasks.append(get_wiki_data_mesh_code(mesh, meshTree, pbar, wikiProgressLabel, 0))
    nb_tasks = len(french_tasks)+len(english_tasks)
    english_results = await asyncio.gather(*english_tasks)
    french_results = await asyncio.gather(*french_tasks)
    if not os.path.exists('wikipedia/wiki_data'):
        # Create the directory if not existing
        os.makedirs('wikipedia/wiki_data')
    if english_results != []:
        async with aiofiles.open("wikipedia/wiki_data/" + filename + "_en.csv", openType, newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')
            for wiki_data in english_results:
                if wiki_data:
                    link, mesh, UI, title, content = wiki_data
                    await wiki.save_to_csv(link, mesh, UI, title, content, filename, writer)
    if french_results != []:
        async with aiofiles.open("wikipedia/wiki_data/" + filename + "_fr.csv", openType, newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')
            for wiki_data in french_results:
                if wiki_data:
                    link, mesh, UI, title, content = wiki_data
                    await wiki.save_to_csv(link, mesh, UI, title, content, filename, writer)
    return False
