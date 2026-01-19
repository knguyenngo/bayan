import requests, json
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup

# Find root folder
def find_project_root():
    current = Path(__file__).parent
    while current != current.parent:
        if current.name == "bayan":
            return current
        current = current.parent
    return Path(__file__).parent  # Fallback

def get_words(url, num_pages, part_of_speech, word_form):
    rows = []
    i = 1

    while i <= num_pages:
        page_url= f"{url}{i}"

        response = requests.get(page_url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # All rows with necessary data
        table = soup.find_all("tr")

        for t in table:
            # Find tds containing necessary data
            first_td = t.find("td", class_="c1")
            second_td = t.find("td", class_="c2")
            third_td = t.find("td", class_="c3")

            # If data column
            if first_td:
                # Extract s:a:p, eng, ara
                ayat_surah_no = first_td.find("span", class_="l").string
                english = second_td.find("a").string
                arabic = third_td.find("span").string

                # Populate row: [s, a, p, eng, ara] then append to rows[]
                r = ayat_surah_no[1:len(ayat_surah_no)-1].split(":")
                r.extend([english, arabic, part_of_speech, word_form])
                rows.append(r)
        i += 1

    return sorted(rows, key=lambda x:(int(x[0]), int(x[1])))

def save_rows(rows, file_name):
    df = pd.DataFrame(rows,
                      columns=['surah', 'ayat', 'position', 'english', 'arabic', 'pos', 'form'])
    df.to_csv(file_name, index=False)
