# List of OSS acquisitions since 2000

This repo aims at building a list of open-source software companies acquisitions.


### Selection criteria
For entering in the list, at least one of the two companies involved in the acquisition should match one of these criteria:
- The main asset(s) are one or several open-source software.
- The main activity is done through open-source software.
- The main activity is aimed at helping open-source communities.

### Available data
The current fields in the table are:
- Date: Approximate date at which the acquisition was announced.
- Acquirer: Name of the acquirer.
- Target: Name of the acquiree.
- Amount: Amount spent for the acquisition.
- Currency: Currency associated with the amount spent.
- Main activities/assets: Short description of the acquiree main activities or assets.
- Closed/Open: Are the acquiree main assets open-source or closed-source software ?
- Reference : A link to the press release or a news article that relates the acquisition.

# License

This work is provided under Creative Commons Attribution 4.0 International (CC BY 4.0) license.

# How to contribute

Pull-requests are welcome if you want to bring additions, fixes, ...

# Producing LaTeX tables and bibliographies

A Python script ``make_bib.py`` is available in the repo to automatically produce LaTeX tables BibLaTeX bibliographies.
You need to have the Zotero Translation Server installed first on port 1969.

### Running the Zotero Translation Server
The [Zotero Translation Server](https://github.com/zotero/translation-server) is available as a Docker container. To download and run it:

    $ docker pull zotero/translation-server
    $ docker run -d -p 1969:1969 --rm --name translation-server zotero/translation-server
    
### Running the script
You can simply run the script using Python in the same folder as the ``list.csv``file.
    
    $ python make_bib.py

It stores bibliographical info in a JSON cache file and can take an ``-u`` argument in order to update the cache.
