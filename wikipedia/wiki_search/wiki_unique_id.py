import csv
import os
import aiofiles
import aiohttp
import asyncio
import wikipedia.wiki_search.wiki as wiki
from MeSH.meshData_func import UniqueIDToTitle, titleToMesh, UniqueIDToFrenchTitle, UniqueIDToMesh
from PyQt5.QtWidgets import QApplication

# Constants for styling console output
bold = '\033[1m'
end = '\033[0m'
underline = '\033[4m'
red = '\033[91m'

# Global counters for task progress tracking
nb_tasks = 0
nb_tasks_done = 0
successed_tasks = 0
failed_tasks = 0

async def fetch(url, params):
    """
    Fetches the content of a given URL asynchronously with parameters.

    Args:
        url (str): The URL to fetch.
        params (dict): The parameters for the GET request.

    Returns:
        dict: The JSON content of the response.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()

async def get_wiki_data_UI(ui,meshTree, pbar, wikiProgressLabel, french_or_english):
    """
    Retrieves Wikipedia data for a given unique ID (UI).

    Args:
        ui (str): The unique ID to search for.
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
    en_title = UniqueIDToTitle(ui,meshTree)[0].lower()
    fr_title = UniqueIDToFrenchTitle(ui,meshTree)[0].lower()
    mesh = UniqueIDToMesh(ui, meshTree)
    mesh = ';'.join(mesh)
    if french_or_english == 1 :
        wiki_content = await wiki.get_content_from_title_via_api(fr_title, 1)
        if wiki_content != (None, None, None):
            nb_tasks_done += 1
            successed_tasks +=1
            pbar.setValue(int(nb_tasks_done / nb_tasks * 100))
            wikiProgressLabel.setText(f"WIKIPEDIA {int(nb_tasks_done/nb_tasks*100)}% [Failed : {failed_tasks} Done : {successed_tasks}] {nb_tasks_done} / {nb_tasks}")
            QApplication.processEvents()
            title, link, content = wiki_content
            return link, mesh, ui, title, content
        else:
            nb_tasks_done += 1
            failed_tasks += 1
            pbar.setValue(int(nb_tasks_done / nb_tasks * 100))
            wikiProgressLabel.setText(f"WIKIPEDIA {int(nb_tasks_done/nb_tasks*100)}% [Failed : {failed_tasks} Done : {successed_tasks}] {nb_tasks_done} / {nb_tasks}")
            QApplication.processEvents()
            print(f"{red}{bold}{underline}WIKIPEDIA :{end}{red}{bold} Error :{end}{red} Pas de page Wikipédia correspondant au titre : {bold}{fr_title}{end}")
            print(f"Erreur de récupération : Pas de page Wikipédia correspondant au unique ID {ui}")
            return False
    if french_or_english == 0:
        wiki_content = await wiki.get_content_from_title_via_api(en_title, 0)
        if wiki_content != (None, None, None):
            nb_tasks_done += 1
            successed_tasks += 1
            pbar.setValue(int(nb_tasks_done / nb_tasks * 100))
            wikiProgressLabel.setText(f"WIKIPEDIA {int(nb_tasks_done/nb_tasks*100)}% [Failed : {failed_tasks} Done : {successed_tasks}] {nb_tasks_done} / {nb_tasks}")
            QApplication.processEvents()
            title, link, content = wiki_content
            return link, mesh, ui, title, content
        else:
            nb_tasks_done += 1
            failed_tasks += 1
            pbar.setValue(int(nb_tasks_done / nb_tasks * 100))
            wikiProgressLabel.setText(f"WIKIPEDIA {int(nb_tasks_done/nb_tasks*100)}% [Failed : {failed_tasks} Done : {successed_tasks}] {nb_tasks_done} / {nb_tasks}")
            QApplication.processEvents()
            print(f"{red}{bold}{underline}WIKIPEDIA :{end}{red}{bold} Error :{end}{red} Pas de page Wikipédia correspondant au titre : {bold}{en_title}{end}")
            print(f"Erreur de récupération : Pas de page Wikipédia correspondant au unique ID {ui}")
            return False

async def launch(topic, filename, openType, meshTree, pbar, wikiProgressLabel, french, english):
    """
    Launches the process to retrieve Wikipedia data for a given unique ID (UI).

    Args:
        topic (str): The unique ID (UI) to search for.
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
    failed_tasks = 0
    successed_tasks = 0
    nb_tasks_done = 0
    french_tasks = []
    english_tasks = []
    if french:
        french_tasks.append(get_wiki_data_UI(topic, meshTree, pbar, wikiProgressLabel, 1))
    if english:
        english_tasks.append(get_wiki_data_UI(topic, meshTree, pbar, wikiProgressLabel, 0))
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
