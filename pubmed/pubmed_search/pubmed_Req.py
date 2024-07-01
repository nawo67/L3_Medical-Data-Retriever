import aiohttp
import aiofiles
import asyncio
import calendar
from bs4 import BeautifulSoup
import csv
import os
from PyQt5.QtWidgets import QApplication
import datetime

from MeSH.meshData_func import titleToMesh, titleToUniqueID

nb_tasks = 0
nb_tasks_done = 0
nb_tasks_failed = 0
timeStart = 0

async def fetch(session, url):
    """
    Fetches the content of the given URL.

    Parameters:
    session (aiohttp.ClientSession): The session to use for making the request.
    url (str): The URL to fetch.

    Returns:
    str: The response text from the URL.
    """
    async with session.get(url) as response:
        return await response.text()

async def process_page(session, url, nbId, writer, meshTree, pbar, pubmedProgressBar):
    """
    Processes a single page of search results from PubMed.

    Parameters:
    session (aiohttp.ClientSession): The session to use for making the request.
    url (str): The URL of the page to process.
    nbId (int): The number of IDs to process.
    writer (csv.writer): The CSV writer to write the results.
    meshTree (list): The mesh data to use for finding codes and unique IDs.
    pbar (QProgressBar): The progress bar to update.
    pubmedProgressBar (QLabel): The progress label to update.

    Returns:
    None
    """
    global nb_tasks_done
    global nb_tasks
    global nb_tasks_failed
    response_text = await fetch(session, url)
    try :
        soup = BeautifulSoup(response_text, 'lxml')
    except :
        soup = BeautifulSoup(response_text, 'html.parser')
    responses = soup.find('pre')

    if responses is not None:
        responses = responses.get_text().split('\r\n\r\n')

        dictList = []
        a = ""
        for i in range(int(nbId)):
            if i < len(responses):
                responses[i] = responses[i].replace('\r\n', ' ').replace('       ', ' ').replace('|', '/').split("- ") 
                dictList.append({})
                for line in responses[i]:
                    if len(line) > 0:
                        line = [d for d in line.split(" ") if d != ""] 
                        
                        if a == 'MH':
                            if 'MH' in dictList[i]:
                                dictList[i][a] = dictList[i][a]+";"+" ".join(line[0:len(line)-1])
                            else:
                                dictList[i][a] = " ".join(line[0:len(line)-1])
                        else:
                            dictList[i][a] = " ".join(line[0:len(line)-1])
                            
                        a = line[-1]

                update_progress_bar(pbar, pubmedProgressBar, 1, 0)
                if 'TI' in dictList[i] and 'AB' in dictList[i] and dictList[i]['AB'] != "" and 'MH' in dictList[i]:
                    meshcodes = titleToMesh([title.split("/")[0] for title in dictList[i]['MH'].split(";")], meshTree)
                    uniqueID = titleToUniqueID([title.split("/")[0] for title in dictList[i]['MH'].split(";")], meshTree)
                    await writer.writerow([url, ";".join(meshcodes), ";".join(uniqueID), dictList[i]['TI'], dictList[i]['AB']])
            else:
                update_progress_bar(pbar, pubmedProgressBar, 0, nbId - i)
                break
    else:
        update_progress_bar(pbar, pubmedProgressBar, 0, nbId)


def update_progress_bar(pbar, pubmedProgressBar, nbIdDone, nbIdFailed):
    """
    Updates the progress bar and label for the PubMed request process.

    Parameters:
    pbar (QProgressBar): The progress bar to update.
    pubmedProgressBar (QLabel): The label to display progress text.
    nbId (int): The number of IDs processed.

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
        pbar.setValue(int(nb_tasks_done/(nb_tasks-nb_tasks_failed)*100))
        pubmedProgressBar.setText(f"PUBMED {int(nb_tasks_done/(nb_tasks-nb_tasks_failed)*100)}% ({nb_tasks_done}/{nb_tasks-nb_tasks_failed}) {int(seconds / 60)}m {int(seconds % 60)}s")
    else:
        pbar.setValue(int(nb_tasks_done/(nb_tasks-nb_tasks_failed)*100))
        pubmedProgressBar.setText(f"PUBMED 0% (0/0) {int(seconds / 60)}m {int(seconds % 60)}s")
    QApplication.processEvents()

async def Req(nbId, nbPage, nbPageMin, search, fileName, y, openType, meshTree, pbar, pubmedProgressBar, nb_tasks__done=0, nb__tasks=1, max_concurrent_requests=40):
    """
    Performs asynchronous requests to PubMed and processes the search results.

    Parameters:
    nbId (int): The number of IDs per page to fetch.
    nbPage (int): The number of pages to fetch.
    nbPageMin (int): The starting page number.
    search (str): The search term to use.
    fileName (str): The name of the file to save the results.
    y (int): The year to search within.
    openType (str): The file open mode, e.g., 'w' for write, 'a' for append.
    meshTree (list): The mesh data to use for finding codes and unique IDs.
    pbar (QProgressBar): The progress bar to update.
    pubmedProgressBar (QLabel): The progress label to update.
    nb_tasks__done (int): The number of tasks already done.
    nb__tasks (int): The total number of tasks.
    max_concurrent_requests (int): The maximum number of concurrent requests.

    Returns:
    None
    """
    global nb_tasks
    global nb_tasks_done
    global nb_tasks_failed
    global timeStart
    if nb_tasks__done == 0:
        nb_tasks_failed = 0
        timeStart = datetime.datetime.now()
    nb_tasks = nb__tasks
    nb_tasks_done = nb_tasks__done
    search = search.replace(" ", "+")
    tasks = []
    connector = aiohttp.TCPConnector(limit_per_host=max_concurrent_requests)
    async with aiohttp.ClientSession(connector=connector) as session:
        if not os.path.exists('pubmed/pubmed_data/'):
            # Create the directory if not existing
            os.makedirs('pubmed/pubmed_data/')
        async with aiofiles.open(f'pubmed/pubmed_data/{fileName}_pubmed_en.csv', openType, encoding="utf-8", newline='') as file:
            writer = csv.writer(file, delimiter='|')
            bold = '\033[1m'
            end = '\033[0m'
            underline = '\033[4m'
            nb_tasks = nb_tasks * 12 * 2 * (nbPage-nbPageMin+1) * nbId
            nb_tasks_done = nb_tasks_done * 12 * 2 * (nbPage-nbPageMin+1) * nbId - nb_tasks_failed
            for m in range(1, 13):
                print(f"{bold}{underline}PUBMED :{end}{bold} {search.split('[')[0].replace('+', ' ')}{end} data search for {bold}{calendar.month_name[m]}{end}... ✓")
                
                for d in range(2):
                    if d == 0:
                        firstDay = 1
                        nbOfDays = 15
                    else:
                        firstDay = 16
                        _, nbOfDays = calendar.monthrange(y, m)
                    for j in range(nbPageMin, nbPageMin + nbPage):
                        url = f"https://pubmed.ncbi.nlm.nih.gov/?term={search}&filter=simsearch1.fha&filter=dates.{y}%2F{m}%2F{firstDay}-{y}%2F{m}%2F{nbOfDays}&sort=date&format=pubmed&page={j}&size={nbId}"
                        tasks.append(process_page(session, url, nbId, writer, meshTree, pbar, pubmedProgressBar))

                        if len(tasks) >= max_concurrent_requests:
                            await asyncio.gather(*tasks)
                            tasks = []

            if tasks:
                await asyncio.gather(*tasks)

