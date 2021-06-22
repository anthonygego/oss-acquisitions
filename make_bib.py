import os
import csv
import json
import argparse
import requests

# URL To the Zotero translation server
ZTS_URL = "http://127.0.0.1:1969"

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-u", "--update-cache", help="increase output verbosity", action="store_true")
args = parser.parse_args()

# Load cache if exists
biblio = {}
if not args.update_cache and os.path.exists("cache.json"):
    print("Load existing cache")
    with open("cache.json") as jsonfile:
        biblio = json.load(jsonfile)

# Process entries line per line
with open("list.csv") as csvfile:
    row_reader = csv.reader(csvfile)
    for idx, row in enumerate(row_reader):
        # Skip head line
        if idx == 0:
            continue

        # Process URL
        print("Processing line {}".format(idx))
        url = row[7]
        if url in biblio:
            # Use cache
            print("Line already in cache")
            bib_entry = biblio[url]
        else:
            # Request server
            try:
                r = requests.post(ZTS_URL + "/web", data=url, headers={'Content-type': 'text/plain'})
                bib_entry = r.json()[0]
            except Exception as e:
                print("ERROR at line {}, url[{}]: {}".format(str(idx), url, str(e)))
                continue

        # Remove abstract if exists
        bib_entry.pop("abstractNote", None)

        # Set the citation key
        bib_entry["citationKey"] = "oss_acquisition_" + str(idx)

        # Add entry to bibliography
        biblio[url] = bib_entry

# Write cache to file
with open("cache.json", "w") as jsonfile:
    json.dump(biblio, jsonfile, indent=4)

# Export to bibtex format
r = requests.post(ZTS_URL + "/export?format=bibtex", json=list(biblio.values()))

# Write result to file
with open('output.bib', 'w') as f:
    f.write(r.text)

