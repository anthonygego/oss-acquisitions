import os
import csv
import json
import argparse
import requests
from math import log, floor


def latex_escape(value):
    return value.replace("&", "\\&") \
           .replace("$", "\\$") \
           .replace("%", "\\%") \
           .replace("#", "\\#") \
           .replace("_", "\\_") \
           .replace("{", "\\{") \
           .replace("}", "\\}")


def human_format(number):
    number = float(number)
    units = ['', 'K', 'M', 'B', 'T', 'P']
    k = 1000.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k**magnitude, units[magnitude])


# URL To the Zotero translation server
ZTS_URL = "http://127.0.0.1:1969"

# Parse arguments
parser = argparse.ArgumentParser(description="Processes entries in list.csv and generates acquisitions.tex and acquisitions.bib")
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


# Get CSV legnth
csv_length = idx

# Write cache to file
with open("cache.json", "w") as jsonfile:
    json.dump(biblio, jsonfile, indent=4)

# Export to bibtex format
r = requests.post(ZTS_URL + "/export?format=biblatex", json=list(biblio.values()))

# Write result to file
with open('acquisitions.bib', 'w') as f:
    f.write(r.text)

# Write LaTeX file
# Currently done separately to handle multiple-line to single biblio entry cases more easily
with open("acquisitions.tex", "w") as texfile:

    def table_header():
        texfile.write("\\begin{table}\n\\centering\n")
        texfile.write("\\begin{scriptsize}\n\\begin{tabular}{|l|l|l|r|l|l|l|}\n\t\\hline\n")
        texfile.write("\t\\rowcolor{gray!25}\\textbf{Date}&\\textbf{Acquirer}&\\textbf{Acquiree}&\\textbf{Price}&\\textbf{Main activities/assets}&\\textbf{Source}&\\textbf{Ref.}\\\\\n\t\hline\n")

    def table_footer(idx1, idx2):
        table_count = (idx1 - 1) // 44 + 1
        texfile.write("\\end{tabular}\n\\end{scriptsize}\n")
        texfile.write("\\caption{{List of main OSS company acquisitions ({} to {}/{})}}\n\\label{{table_oss_acquisitions_{}}}\n\\end{{table}}\n".format(idx1, idx2, csv_length, table_count))

    table_header()

    with open("list.csv") as csvfile:
        row_reader = csv.reader(csvfile)
        last_first_idx = 1
        for idx, row in enumerate(row_reader):
            # Skip head line
            if idx == 0:
                continue

            # Generate LaTeX line
            citation_key = biblio[row[7]]["citationKey"]
            currencies = {"EUR": "€", "USD": "$"}
            row = row[0:3] + ([human_format(row[3]) + currencies.get(row[4], "")] if row[3] else [""]) + row[5:7]
            row = list(map(latex_escape, row))
            texfile.write("\t{}&{}&{}&{}&{}&{}&\\cite{{{}}}\\\\\n\t\\hline\n".format(*row, citation_key))

            # Print new table
            if idx % 44 == 0:
                table_footer(last_first_idx, idx)
                table_header()
                last_first_idx = idx + 1

        table_footer(last_first_idx, idx)

