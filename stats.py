import aiofiles
import aiofiles.os
import asyncio
import csv
from os.path import exists
from MeSH.meshData_func import UniqueIDToTitle, UniqueIDToFrenchTitle

async def read_file(file_path):
    """
    Asynchronously reads the contents of a file.

    Args:
        file_path (str): Path to the file to read.

    Returns:
        str: Content of the file as a string.
    """
    async with aiofiles.open(file_path, 'r', encoding='utf-8', newline='') as f:
        return await f.read()

async def write_file(file_path, data):
    """
    Asynchronously writes data to a CSV file.

    Args:
        file_path (str): Path to the file to write.
        data (list of lists): Data to write into the CSV file.

    Writes data into the specified CSV file with '|' delimiter.
    """
    async with aiofiles.open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='|')
        for line in data:
            await writer.writerow(line)

async def process_file(file, meshTree):
    """
    Asynchronously processes a CSV file, extracting and analyzing data.

    Args:
        file (str): Path to the CSV file.
        meshTree (list of str): List of mesh data from a file.

    Returns:
        tuple: A tuple containing statistics and filtered data lines.

    This function reads the CSV file, processes each row to extract
    Mesh IDs, titles, and abstracts, then calculates statistics based
    on occurrences of Mesh titles in titles and abstracts.
    """
    async with aiofiles.open(file, encoding="utf-8", newline='') as f:
        reader = csv.reader(await f.readlines(), delimiter='|')
        urls = []
        meshlists = set()
        uilists = set()
        titles = ""
        abstracts = ""
        abstractsList = []

        for row in reader:
            urls.append(row[0])

            for mesh in row[1].split(";"):
                meshlists.add(mesh)
            
            for ui in row[2].split(";"):
                uilists.add(ui)

            titles += row[3] + " "
            abstracts += row[4] + " "
            abstractsList.append(row[4])

    lines = []
    if file.split(".")[0].split("_")[-1] == 'en':
        for ui in uilists:
            title = UniqueIDToTitle(ui, meshTree)[0].lower()
            lines.append([title, titles.count(title), abstracts.count(title), sum([1 for text in abstractsList if title in text])])
    elif file.split(".")[0].split("_")[-1] == 'fr':
        for ui in uilists:
            title = UniqueIDToFrenchTitle(ui, meshTree)[0].lower()
            lines.append([title, titles.count(title), abstracts.count(title), sum([1 for text in abstractsList if title in text])])
    
    lines.sort(key=lambda l: (l[2], l[1]), reverse=True)

    filtered_lines = [line for line in lines if line[1] != 0 and line[2] != 0]

    stats = [file, len(urls), len(titles.split(" ")), len(abstracts.split(" ")), len((titles + abstracts).split(" "))]
    return (stats, filtered_lines)

async def stats(files, folder_name):
    """
    Asynchronously computes statistics across multiple CSV files.

    Args:
        files (list of str): List of CSV files to process.
        folder_name (str): Name of the folder for output files.

    This function creates statistics and filtered data for each file,
    then writes the aggregated statistics and filtered data to respective
    CSV files in the 'stats' folder.
    """
    if not exists(f'stats/{folder_name}/'):
        await aiofiles.os.makedirs(f'stats/{folder_name}/')

    meshTree = await read_file('MeSH/meshData.bin')
    meshTree = meshTree.splitlines()

    all_stats_file = f'stats/{folder_name}/all_files_stats.csv'
    combined_file = f'stats/{folder_name}/{folder_name}_stats.csv'

    tasks = [process_file(file, meshTree) for file in files]
    results = await asyncio.gather(*tasks)

    all_stats = [result[0] for result in results]
    all_filtered_lines = [line for result in results for line in result[1]]

    await write_file(all_stats_file, all_stats)

    await write_file(combined_file, all_filtered_lines)

    print("Data have been correctly retrieved.")

    return True