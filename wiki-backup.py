# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Wiki Backup                                                                 #
# v. 20241023                                                                 #
#                                                                             #
# MIT License                                                                 #
# Copyright (c) 2024 /bandowashere                                            #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



# import dependencies
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm



# define functions
def getZimLinks(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    texts = []

    # get all links and texts
    for a in soup.find_all('a', href=True):
        links.append(a['href'])
    for text in soup.find_all(string=True):
        texts.append(text)

    # get file sizes
    fileDateAndSizes = []
    for i in range(len(texts)):
        if len(texts[i].split()) != 3:  # only get lists that include file sizes
            continue
        try:  # some texts[i].split()[2] might not be an integer
            date = texts[i].split()[0]
            size =  str(int(texts[i].split()[2]) / 1000 / 1000 / 1000)  # in gb
            fileDateAndSizes.append([date, size])
        except:
            continue

    wikiLinks = list(zip(links, fileDateAndSizes))
    return wikiLinks

def getZimFile(url):
    # define the filename. The last part of the URL
    filename = url.split("/")[-1]

    # send a GET request with streaming enabled for large files
    response = requests.get(url, stream = True)

    if response.status_code == 200:
        # get the total file size (if available)
        totalSize = int(response.headers.get('content-length', 0))

        # open the file for writing in binary mode
        with open(filename, "wb") as f:
            
            # create a progress bar for the download
            with tqdm(unit='B', 
                      unit_scale=True, 
                      miniters=1, 
                      desc='Downloading', 
                      total=totalSize) as pbar:
                
                for chunk in response.iter_content(1024):
                    # write data to the file and update the progress bar
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))

        print(f"Downloaded {filename} successfully!")

    else:
        print(f"Download failed! Status code: {response.status_code}")



# entry
if __name__ == '__main__':
    # initialize variables
    URLBASE = "https://dumps.wikimedia.org/other/kiwix/zim/"
    WIKIS = ["wikibooks/",
             "wikinews/",
             "wikipedia/",
             "wikiquote/",
             "wikisource/",
             "wikiversity/",
             "wikivoyage/",
             "wiktionary/"]
    
    # determine which wiki to backup
    for wiki in WIKIS:
        wikiLinks = getZimLinks(URLBASE + wiki)

        answer = ''
        urls = []
        while True:
            totalFilesize = 0
            for link in wikiLinks:
                totalFilesize += float(link[1][1])
            print(f"{wiki} filesize: {int(totalFilesize)} gb")
            answer = input(f"Backup {wiki} (y/n)? ")
            print()
            
            if answer == 'y':
                for link in wikiLinks:
                    url = URLBASE + wiki + link[0]
                    urls.append(url)
                break
            elif answer == 'n':
                break
            else:
                continue

        if answer != 'y':
            continue
        else:  
            for i in range(len(urls)):
                if i == 0:
                    continue  # skip the first link
                getZimFile(urls[i])  # backup here
            # comment this break out out to go through all wikis; not just one
            break