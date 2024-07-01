import asyncio

from LiSSa.LiSSa_search.LiSSa import LiSSaReq

def LiSSaReqUI(search, filename, nb_pages, nb_data_pages, meshTree, progress_bar, lissa_progress_label):
    """
    Searches LiSSa for a unique ID and retrieves data based on the search results.

    Parameters:
    search (str): The unique ID to search for.
    filename (str): The name of the file to save the results.
    nb_pages (int): The number of pages to search for each unique ID.
    nb_data_pages (int): The number of data pages to retrieve for each unique ID.
    meshTree (list): The mesh data to use for finding mesh terms.
    progress_bar (QProgressBar): The progress bar to update.
    lissa_progress_label (QLabel): The progress label to update.

    Returns:
    bool: Always returns False.
    """
    title = None

    # Search for the MeSH term in the meshTree
    for line in meshTree:
        if search in line:
            title = line.split("|")[0]
            break
    
    if title:
        asyncio.run(LiSSaReq(title, filename, nb_pages, nb_data_pages, meshTree, progress_bar, lissa_progress_label))

    return False