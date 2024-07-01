import asyncio

from LiSSa.LiSSa_search.LiSSa import LiSSaReq
from MeSH.meshData_func import depthMeshFrenchTitle

def LiSSaReqMesh(search, filename, nb_pages, nb_data_pages, depth, meshTree, progress_bar, lissa_progress_label):
    """
    Searches LiSSa for multiple MeSH terms at different depths and retrieves data based on the search results.

    Parameters:
    search (str): The search term used to generate MeSH titles.
    filename (str): The name of the file to save the results.
    nb_pages (int): The number of pages to search for each MeSH term.
    nb_data_pages (int): The number of data pages to retrieve for each MeSH term.
    depth (int): The depth in the MeSH tree to search for related terms.
    meshTree (list): The mesh data to use for finding mesh terms.
    progress_bar (QProgressBar): The progress bar to update.
    lissa_progress_label (QLabel): The progress label to update.

    Returns:
    bool: Always returns False.
    """
    # Generate a list of titles based on the depth in the MeSH tree
    titleList = depthMeshFrenchTitle(search, depth, meshTree)
    # Loop through the titles and perform PubMed requests
    for i, title in enumerate(titleList):
        asyncio.run(LiSSaReq(title, filename, nb_pages, nb_data_pages, meshTree, progress_bar, lissa_progress_label, len(titleList), i))

    return False