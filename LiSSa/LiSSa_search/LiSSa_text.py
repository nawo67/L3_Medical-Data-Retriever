import asyncio

from LiSSa.LiSSa_search.LiSSa import LiSSaReq
from MeSH.meshData_func import englishToFrench

def LiSSaReqText(search, filename, nb_pages, nb_data_pages, meshTree, progress_bar, lissa_progress_label):
    """
    Searches LiSSa for text converted to French and retrieves data based on the search results.

    Parameters:
    search (str): The search term to convert to French and use for the LiSSa search.
    filename (str): The name of the file to save the results.
    nb_pages (int): The number of pages to search for each search term.
    nb_data_pages (int): The number of data pages to retrieve for each search term.
    meshTree (list): The mesh data to use for finding mesh terms.
    progress_bar (QProgressBar): The progress bar to update.
    lissa_progress_label (QLabel): The progress label to update.

    Returns:
    bool: Always returns False.
    """
    search = englishToFrench(search, meshTree)
    asyncio.run(LiSSaReq(search, filename, nb_pages, nb_data_pages, meshTree, progress_bar, lissa_progress_label))
    
    return False