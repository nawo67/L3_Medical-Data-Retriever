def depthMeshFrenchTitle(code, depth, mesh):
    """
    Finds French titles in the mesh data that correspond to the given code and depth.

    Parameters:
    code (str): The code to search for.
    depth (int): The depth level to consider.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of French titles corresponding to the given code and depth.
    """
    meshToTitles = set([line.split("|")[0] for line in mesh if code in line.split("|")[2] and len(code) + depth*4 >= len(line.split("|")[2])])
    return list(meshToTitles)

def depthMeshEnglishTitle(code, depth, mesh):
    """
    Finds English titles in the mesh data that correspond to the given code and depth.

    Parameters:
    code (str): The code to search for.
    depth (int): The depth level to consider.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of English titles corresponding to the given code and depth.
    """
    meshToTitles = set([line.split("|")[1] for line in mesh if code in line.split("|")[2] and len(code) + depth*4 >= len(line.split("|")[2])])
    return list(meshToTitles)

def depthMeshCode(code, depth, mesh):
    """
    Finds mesh codes in the mesh data that correspond to the given code and depth.

    Parameters:
    code (str): The code to search for.
    depth (int): The depth level to consider.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of mesh codes corresponding to the given code and depth.
    """
    meshToMeshs = set([line.split("|")[2] for line in mesh if code in line.split("|")[2] and len(code) + depth*4 >= len(line.split("|")[2])])
    return list(meshToMeshs)

def textInData(text, mesh):
    """
    Checks if the given text is present in any titles in the mesh data.

    Parameters:
    text (str): The text to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    bool: True if the text is present in any title, False otherwise.
    """
    textAvailable = set([line.split("|")[1] for line in mesh if text.lower() == line.split("|")[1].lower() or text.lower() == line.split("|")[0].lower()])
    return len(textAvailable) != 0

def meshInData(code, mesh):
    """
    Checks if the given mesh code is present in the mesh data.

    Parameters:
    code (str): The mesh code to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    bool: True if the mesh code is present, False otherwise.
    """
    meshAvailable = set([line.split("|")[2] for line in mesh if code == line.split("|")[2]])
    return len(meshAvailable) != 0

def uiInData(ui, mesh):
    """
    Checks if the given Unique Identifier (UI) is present in the mesh data.

    Parameters:
    ui (str): The Unique Identifier to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    bool: True if the UI is present, False otherwise.
    """
    uiAvailable = set([line.split("|")[3] for line in mesh if ui == line.split("|")[3]])
    return len(uiAvailable) != 0

def meshSuggestion(code, mesh):
    """
    Suggests titles and their corresponding mesh codes that match the given code.

    Parameters:
    code (str): The code to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of strings in the format 'mesh code (French title / English title)' for matching entries.
    """
    meshToTitles = set([f"{line.split('|')[2]} ({line.split('|')[0]} / {line.split('|')[1]})" for line in mesh if code in line.split("|")[2]])
    return list(meshToTitles)

def wikiSuggestion(code, mesh):
    """
    Suggests English titles from the mesh data that contain the given code as a substring.

    Parameters:
    code (str): The code to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of English titles containing the given code.
    """
    textToTitles = set([line.split('|')[1] for line in mesh if code.lower() in line.split('|')[1].lower()])
    return list(textToTitles)

def wikiFrenchSuggestion(code, mesh):
    """
    Suggests French titles from the mesh data that contain the given code as a substring.

    Parameters:
    code (str): The code to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of French titles containing the given code.
    """
    textToTitles = set([line.split('|')[0] for line in mesh if code.lower() in line.split('|')[0].lower()])
    return list(textToTitles)

def UiSuggestion(code, mesh):
    """
    Suggests titles and their corresponding UIs that match the given code.

    Parameters:
    code (str): The code to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of strings in the format 'UI (French title / English title)' for matching entries.
    """
    uiToTitles = set([f"{line.split('|')[3]} ({line.split('|')[0]} / {line.split('|')[1]})" for line in mesh if code in line.split("|")[3]])
    return list(uiToTitles)

def englishToFrench(title, mesh):
    """
    Finds the French title corresponding to the given English title.

    Parameters:
    title (str): The English title to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    str: The French title corresponding to the given English title.
    """
    frenchTitle = set([line.split('|')[0] for line in mesh if title.lower() == line.split('|')[1].lower() or title.lower() == line.split('|')[0].lower()])
    return list(frenchTitle)[0]

def frenchToEnglish(title, mesh):
    """
    Finds the English title corresponding to the given French title.

    Parameters:
    title (str): The French title to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    str: The English title corresponding to the given French title.
    """
    englishTitle = set([line.split('|')[1] for line in mesh if title.lower() == line.split('|')[0].lower() or title.lower() == line.split('|')[1].lower()])
    return list(englishTitle)[0]

def titleToMesh(titles, mesh):
    """
    Finds mesh codes corresponding to the given English titles.

    Parameters:
    titles (list of str): The list of English titles to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of mesh codes corresponding to the given English titles.
    """
    titles_set = set(titles)
    return [line.split("|")[2] for line in mesh if line.split("|")[1] in titles_set]

def frenchTitleToMesh(titles, mesh):
    """
    Finds mesh codes corresponding to the given French titles.

    Parameters:
    titles (list of str): The list of French titles to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of mesh codes corresponding to the given French titles.
    """
    titles_set = set(titles)
    return [line.split("|")[2] for line in mesh if line.split("|")[0] in titles_set]

def frenchTitleToUniqueID(titles, mesh):
    """
    Finds Unique Identifiers (UIs) corresponding to the given French titles.

    Parameters:
    titles (list of str): The list of French titles to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of UIs corresponding to the given French titles.
    """
    titles_set = set(titles)
    uniqueids = set([line.split("|")[3] for line in mesh if line.split("|")[0] in titles_set])
    return list(uniqueids)

def UniqueIDToMesh(UI, mesh):
    """
    Finds mesh codes corresponding to the given Unique Identifier (UI).

    Parameters:
    UI (str): The Unique Identifier to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of mesh codes corresponding to the given UI.
    """
    mesh = set([line.split("|")[2] for line in mesh if line.split("|")[3] == UI])
    return list(mesh)

def UniqueIDToTitle(UI, mesh):
    """
    Finds English titles corresponding to the given Unique Identifier (UI).

    Parameters:
    UI (str): The Unique Identifier to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of English titles corresponding to the given UI.
    """
    mesh = set([line.split("|")[1] for line in mesh if line.split("|")[3] == UI])
    return list(mesh)

def MeshToUniqueID(mesh, UI):
    """
    Finds Unique Identifiers (UIs) corresponding to the given mesh code.

    Parameters:
    mesh (str): The mesh code to search for.
    UI (list of str): The UI data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of UIs corresponding to the given mesh code.
    """
    UI = set([line.split("|")[3] for line in UI if line.split("|")[2] == mesh])
    return list(UI)

def titleToUniqueID(titles, mesh):
    """
    Finds Unique Identifiers (UIs) corresponding to the given English titles.

    Parameters:
    titles (list of str): The list of English titles to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of UIs corresponding to the given English titles.
    """
    titles_set = set(titles)
    unique_ids = set([line.split("|")[3] for line in mesh if line.split("|")[1] in titles_set])
    return list(unique_ids)

def UniqueIDToFrenchTitle(UI, mesh):
    """
    Finds French titles corresponding to the given Unique Identifier (UI).

    Parameters:
    UI (str): The Unique Identifier to search for.
    mesh (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of French titles corresponding to the given UI.
    """
    frenchTitle = set([line.split("|")[0] for line in mesh if line.split("|")[3] == UI])
    return list(frenchTitle)

def MeshToFrenchTitle(mesh, meshTree):
    """
    Finds French titles corresponding to the given mesh code.

    Parameters:
    mesh (str): The mesh code to search for.
    meshTree (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of French titles corresponding to the given mesh code.
    """
    frenchTitle = set([line.split("|")[0] for line in meshTree if line.split("|")[2] == mesh])
    return list(frenchTitle)

def MeshToEnglishTitle(mesh, meshTree):
    """
    Finds English titles corresponding to the given mesh code.

    Parameters:
    mesh (str): The mesh code to search for.
    meshTree (list of str): The mesh data, each line is a string with fields separated by '|'.

    Returns:
    list: A list of English titles corresponding to the given mesh code.
    """
    frenchTitle = set([line.split("|")[1] for line in meshTree if line.split("|")[2] == mesh])
    return list(frenchTitle)

if __name__ == "__main__":
    meshTreeFile = open('meshData.bin', 'r', encoding="utf-8", newline='')
    meshTree = meshTreeFile.read().splitlines()
    meshTreeFile.close()
    print(frenchTitleToMesh(["Diabète"], meshTree))