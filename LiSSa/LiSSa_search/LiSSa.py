import aiohttp
import aiofiles
import asyncio
from bs4 import BeautifulSoup
import csv
import os
from PyQt5.QtWidgets import QApplication
from MeSH.meshData_func import frenchTitleToUniqueID, frenchTitleToMesh
import datetime

nb_tasks = 0
nb_tasks_done = 0
nb_tasks_failed = 0
timeStart = 0

def is_french(text):
    """
    Determines if a given text is likely in French based on keyword counts.

    Args:
        text (str): The text to analyze.

    Returns:
        bool: True if the text is considered French, False otherwise.
    """
    english_keywords = {'the', 'be', 'to', 'of', 'and', 'in', 'that', 'have', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from'}
    french_keywords = {'le', 'de', 'un', 'être', 'et', 'à', 'il', 'avoir', 'ne', 'je', 'son', 'que', 'se', 'qui', 'ce', 'dans', 'en', 'du', 'elle', 'au', 'ceci', 'mais', 'par', 'pour'}

    text = text.lower()

    english_keyword_count = sum(text.split().count(keyword) for keyword in english_keywords)
    french_keyword_count = sum(text.split().count(keyword) for keyword in french_keywords)

    # If the number of French keywords exceeds English keywords and there is a good number of french keywords, the text is considered French.
    if french_keyword_count > english_keyword_count and french_keyword_count > 15:
        return True
    else:
        return False

async def search_lissa(session, query, page, nb_data_pages):
    """
    Searches LiSSa and retrieves URLs of the search results.

    Parameters:
    session (aiohttp.ClientSession): The session to use for making the request.
    query (str): The search query.
    page (int): The page number of the search results.
    nb_data_pages (int): The number of data pages to retrieve.

    Returns:
    List[str]: A list of URLs of the search results.
    """
    search_url = f'https://www.lissa.fr/dc/api/dc/query?q={query}&p={page}&n={nb_data_pages}&t=NLM&f=true.speps&l=fr&s=MAJOR%3D4%2CMINOR%3D1%2CET_MAN%3D3%2CET_AUTO%3D1%2CNOEXPL%3D3%2CEXPL%3D1%2CAFF%3D0.0%2CYEAR_CURRENT%3D10%2CYEAR_STEP%3D0.6%2CTITLE%3D10%2CSUBTITLE%3D10%2CKEYWORDS_LIST%3D5%2CINDEX_MESH_PUBLICATION_TYPE'+'{MSH_D_016454%3D3%2CMSH_D_017065%3D3%2CMSH_D_016446%3D3%2CMSH_D_016431%3D3%2CMSH_D_017418%3D3}'
    async with session.get(search_url) as response:
        if response.status == 200:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            result_links = soup.find_all('a', class_='\\"nounderline\\"')
            urls = ['https://www.lissa.fr/' + link['href'][2:-2] for link in result_links]
            return urls
        else:
            print(f"Erreur lors de la recherche : {response.status}")
            return []

async def extract_article_data(session, url, query, meshTree, writer, progress_bar, lissa_progress_label):
    """
    Extracts the title and summary of an article given its URL.

    Parameters:
    session (aiohttp.ClientSession): The session to use for making the request.
    url (str): The URL of the article.
    query (str): The search query used.
    meshTree (list): The mesh data to use for finding mesh terms.
    writer (csv.writer): The CSV writer to write the results.
    progress_bar (QProgressBar): The progress bar to update.
    lissa_progress_label (QLabel): The progress label to update.

    Returns:
    None
    """
    global nb_tasks
    global nb_tasks_done
    global nb_tasks_failed
    async with session.get(url) as response:
        if response.status == 200:
            content = await response.text()
            soup = BeautifulSoup(content, 'html.parser')
            
            title_tag = soup.find('h2')  
            title = title_tag.text.strip() if title_tag else 'Titre non trouvé'
            
            section_title_tag = soup.find_all('section-title')
            section_text_tag = soup.find_all('simple-para')
            summary = []
            for i in range(len(section_title_tag)):
                try:
                    summary.append(section_title_tag[i].text+" : "+ section_text_tag[i].text)
                except:
                    pass

            summary = " ".join(summary) if len(summary) > 0 else 'Résumé non trouvé'

            article_data = {'url': url, 'title': title, 'summary': summary}
            
            QApplication.processEvents()
            if article_data['summary'] != 'Résumé non trouvé' and is_french(article_data['summary']):
                await writer.writerow([article_data['url'], ";".join(frenchTitleToMesh([query], meshTree)), ";".join(frenchTitleToUniqueID([query], meshTree)), article_data['title'], article_data['summary']])
                update_progress_bar(progress_bar, lissa_progress_label, 1, 0)    
            else:
                update_progress_bar(progress_bar, lissa_progress_label, 0, 1)
                print("!!!!!!!!!!! Pas de résumé ou en anglais !!!!!!!!!!!")
                print(article_data['url'])
        else:
            update_progress_bar(progress_bar, lissa_progress_label, 0, 1)
            print(f"Erreur lors de la récupération de l'article : {response.status}")
            return {'title': 'Erreur', 'summary': 'Erreur'}

def update_progress_bar(progress_bar, lissa_progress_label, nbIdDone, nbIdFailed):
    """
    Updates the progress bar and label for the LiSSa request process.

    Parameters:
    progress_bar (QProgressBar): The progress bar to update.
    lissa_progress_label (QLabel): The label to display progress text.
    nbIdDone (int): The number of IDs done.
    nbIdFailed (int): The number of IDs failed.

    Returns:
    None
    """
    global nb_tasks
    global nb_tasks_done
    global nb_tasks_failed

    a_timedelta = datetime.datetime.now() - timeStart
    seconds = a_timedelta.total_seconds()
    nb_tasks_done += nbIdDone
    nb_tasks_failed += nbIdFailed
    if (nb_tasks-nb_tasks_failed) != 0:
        progress_bar.setValue(int(nb_tasks_done/(nb_tasks-nb_tasks_failed)*100))
        lissa_progress_label.setText(f"LISSA {int(nb_tasks_done/(nb_tasks-nb_tasks_failed)*100)}% ({nb_tasks_done}/{nb_tasks-nb_tasks_failed}) {int(seconds / 60)}m {int(seconds % 60)}s")
    else:
        progress_bar.setValue(0)
        lissa_progress_label.setText(f"LISSA 0% (0/0) {int(seconds / 60)}m {int(seconds % 60)}s")
    QApplication.processEvents()

async def LiSSaReq(query, filename, nb_pages, nb_data_pages, meshTree, progress_bar, lissa_progress_label, nb__tasks=1, nb__tasks_done=0, max_concurrent_requests=5):
    """
    Searches LiSSa and retrieves data based on the search query.

    Parameters:
    query (str): The search query.
    filename (str): The name of the file to save the results.
    nb_pages (int): The number of pages to search.
    nb_data_pages (int): The number of data pages to retrieve.
    meshTree (list): The mesh data to use for finding mesh terms.
    progress_bar (QProgressBar): The progress bar to update.
    lissa_progress_label (QLabel): The progress label to update.
    nb__tasks (int): The total number of tasks.
    nb__tasks_done (int): The number of tasks done.
    max_concurrent_requests (int): The maximum number of concurrent requests.

    Returns:
    None
    """
    global nb_tasks
    global nb_tasks_done
    global nb_tasks_failed
    global timeStart
    if nb__tasks_done == 0:
        nb_tasks_failed = 0
        timeStart = datetime.datetime.now()
    nb_tasks = nb__tasks * nb_pages * nb_data_pages
    nb_tasks_done = nb__tasks_done * nb_pages * nb_data_pages - nb_tasks_failed
    connector = aiohttp.TCPConnector(limit_per_host=max_concurrent_requests)
    async with aiohttp.ClientSession(connector=connector) as session:
        if not os.path.exists('LiSSa/LiSSa_data/'):
            os.makedirs('LiSSa/LiSSa_data/')
        async with aiofiles.open(f'LiSSa/LiSSa_data/{filename}_lissa_fr.csv', "w", encoding="utf-8", newline='') as file:
            writer = csv.writer(file, delimiter='|')
            for page in range(1, nb_pages+1):
                urls = await search_lissa(session, query, page, nb_data_pages)
                update_progress_bar(progress_bar, lissa_progress_label, 0, nb_data_pages-len(urls))
                tasks = [extract_article_data(session, url, query, meshTree, writer, progress_bar, lissa_progress_label) for url in urls]
                await asyncio.gather(*tasks)