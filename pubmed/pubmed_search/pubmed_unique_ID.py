import asyncio

from pubmed.pubmed_search.pubmed_Req import Req

def ReqUI(nbId, nbPage, nbPageMin, search, fileName, y, openType, meshTree, pbar, pubmedProgressBar):
    """
    Runs a PubMed request using a search term to find a corresponding MeSH term and fetches data based on it.

    Parameters:
    nbId (int): The number of IDs per page to fetch.
    nbPage (int): The number of pages to fetch.
    nbPageMin (int): The starting page number.
    search (str): The search term to use for finding a MeSH term.
    fileName (str): The name of the file to save the results.
    y (int): The year to search within.
    openType (str): The file open mode, e.g., 'w' for write, 'a' for append.
    meshTree (list): The mesh data to use for finding MeSH terms.
    pbar (QProgressBar): The progress bar to update.
    pubmedProgressBar (QLabel): The progress label to update.

    Returns:
    bool: Always returns False. Could be used for error handling or future expansion.
    """
    title = None

    # Search for the MeSH term in the meshTree
    for line in meshTree:
        if search in line:
            title = line.split("|")[1]
            break
    
    print(title)
    
    # If a MeSH term is found, run the asynchronous request
    if title:
        asyncio.run(Req(nbId, nbPage, nbPageMin, title+"[MeSH Terms]", fileName, y, openType, meshTree, pbar, pubmedProgressBar))

    return False