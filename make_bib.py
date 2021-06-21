import csv
import requests

# URL To the Zotero translation server
ZTS_URL = "http://127.0.0.1:1969"


# Process entries line per line
biblio = []
with open("list.csv") as csvfile:
    row_reader = csv.reader(csvfile)
    for idx, row in enumerate(row_reader):
        # Skip head line
        if idx == 0:
            continue

        # Fetch URL
        print("Processing line {}".format(idx))
        url = row[7]

        # Request server
        r = requests.post(ZTS_URL + "/web", data=url, headers={'Content-type': 'text/plain'})

        try:
            bib_entry = r.json()[0]

            # Remove abstract if exists
            bib_entry.pop("abstractNote", None)

            # Set the citation key
            bib_entry["citationKey"] = "oss_acquisition_" + str(idx)

            # Add entry to bibliography
            biblio.append(bib_entry)
        except Exception as e:
            print("ERROR at line {}, url[{}]: {}".format(str(idx), url, str(e)))


# Export to bibtex format
r = requests.post(ZTS_URL + "/export?format=bibtex", json=biblio)

# Write result to file
with open('output.bib', 'w') as f:
    f.write(r.text)

