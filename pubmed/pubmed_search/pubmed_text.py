import asyncio

from pubmed.pubmed_search.pubmed_Req import Req

def ReqText(nbId, nbPage, nbPageMin, search, fileName, y, openType, meshTree, pbar, pubmedProgressBar):
    """
    Runs the PubMed request using asyncio to fetch and process data.

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

    Returns:
    bool: Always returns False (could be used for error handling or future expansion).
    """
    asyncio.run(Req(nbId, nbPage, nbPageMin, search, fileName, y, openType, meshTree, pbar, pubmedProgressBar))
    
    return False