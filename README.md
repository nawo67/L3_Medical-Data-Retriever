# PubMed, Wikipedia and LiSSa Data Retrieval

This project involves retrieving data from PubMed, Wikipedia and LiSSa using asynchronous Python programming with asyncio and aiohttp. It aims to fetch scientific article metadata from PubMed and LiSSa based on MeSH terms and also gather additional information from Wikipedia related to those terms.

## Features

### Data Retriever (`interface.py`)
The interface of our data recovery tool offers several features:
- **Sources selection**
    - You can choose from several sources to retrieve your data: PubMed, Wikipedia and LiSSa. Simply check the sources you need.
- **Language selection**
    - The program lets you choose between two languages: English and French.  
    *Note that PubMed is only available in English and LiSSa only in French.*
- **Search type selection**
    - The search is carried out using MeSH, a biomedical thesaurus. MeSH offers three main reference elements in its tree structure: the MeSH descriptor, the unique ID and the MeSH name. Searches are performed using these references, depending on the type of search chosen.  
    *Note that searching by MeSH descriptor allows you to search by depth, obtaining data from lower levels according to the depth specified by the user.*
- **MeSH tree window**
    - Offers an interface to browse and select MeSH terms via the MeSH Tree.
    - Accessible within the main interface for streamlined MeSH term selection and data retrieval.
- **Folder name selection**
    - Recovered data is saved in .csv format with the name specified by the user in the interface. It is possible to overwrite the previous file if it has the same name, according to the user's choice.
- **Loading bar**
    - Although the program's asynchronicity allows great optimization, data retrieval can take a long time. The loading bar therefore indicates the time remaining.  
    
<br>

Les données récupérées sont organisées dans un fichier CSV avec les colonnes suivantes :
- **url** : L'URL de la source de données.
- **mesh descriptor** : Le descripteur MeSH utilisé pour la recherche.
- **unique id** : L'identifiant unique associé au descripteur MeSH.
- **page title** : Le titre de la page (pour les sources comme Wikipedia).
- **page content** : Le contenu de la page récupérée.

#### Exemple de structure du fichier CSV :
| url |mesh descriptor|unique id| page title| page content |
|-----|---------------|---------|-----------|--------------|
| https://pubmed.ncbi.nlm.nih.gov/12345678/ | A08.800.950.500.800;A09.846;A14.549.885.779 | D018987 | Taste bud | ... |
| https://fr.wikipedia.org/wiki/Maladie_cardio-vasculaire | A08.800.950.500.800 | D002318 | Maladies cardiovasculaires | ... |
| https://lissa.fr/document/666 | A08.800.950.500.800 | D018987 | Papille gustative | ... |

### Statistic retriever (`statistics_retriever.py`)

  A statistics interface is available. It creates a folder with the name chosen by the user, enabling statistics to be retrieved from the data files selected by the user on the interface.

## Requirements

- Aiohttp (`pip install aiohttp`)
- Aiofiles (`pip install aiofiles`)
- Beautiful Soup 4 (`pip install beautifulsoup4`)
- Requests (`pip install requests`)
- PyQT5 (`pip install pyqt5`)
- Asyncio (`pip install asyncio`)

if `pip` doesn't work, use `pip3`
(or use "requirements.txt")

## Installation

1. Clone the repository:

`git clone https://gitlab-etu.fil.univ-lille.fr/jacques/data_disease_pubmed_wikipedia.git`

2. Install dependencies:

`pip install -r requirements.txt`

## Usage

### Launching the Interface

For the following commands, you need to move to the retriever folder:

To use the interface for retrieving PubMed, Wikipedia and LiSSa data:

```bash 
~.../retriever$ python interface.py
```

To use the statistic retriever:

```bash
~.../retriever$ python statistics_retriever.py
```

if `python` doesn't work, use `python3`

## Search Instructions

When you run interface.py, you will be prompted to enter various parameters for retrieving data. The interface guides you through the process of fetching data from PubMed, Wikipedia, and LiSSa.  

#### PubMed Data Retrieval:

    For PubMed searches, multiple scientific articles are retrieved in a single query. You can specify the number of articles to be retrieved per page, as well as the total number of pages to be retrieved and the year of publication to be searched.

    - Enter the number of IDs per page (limited to 10,20,50,100,200) (nbId).
    - Enter the number of pages to fetch (up to 50) (nbPage).
    - Enter the starting page number (nbPageMin).
    - Enter the year to search within (y).

#### Wikipedia Data Retrieval:

    Wikipedia search finds only one page

    - Enter the topic to search on Wikipedia (topic).

#### LiSSa Data Retrieval:

    LiSSa retrieves documents based on a specific search term. You can specify the number of documents per page and the total number of pages to be retrieved.
    
    - Enter the number of IDs per page (nbId).
    - Enter the number of pages to fetch (nbPage).
    - Enter the search term (search).

