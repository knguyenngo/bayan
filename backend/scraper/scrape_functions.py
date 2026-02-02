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

# Get all words of a specific part of speech
# Returns list of rows: [[s, a, p, eng, ara, pos]]
def get_words(session, url, num_pages, part_of_speech, word_form):
    rows = []
    i = 1

    while i <= num_pages:
        # Set page URL
        page_url= f"{url}{i}"

        # Get HTML from session object
        response = session.get(page_url)
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

    return rows

# Return dict of links for all POS and their forms
def get_links(session):
    response = session.get("https://corpus.quran.com/morphologicalsearch.jsp")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    # Find pos and forms in search boxes
    pos = soup.find(id="partOfSpeechList")
    forms = soup.find(id="formList").find_all("option")

    pos_dict, list_of_forms, all_links = {}, [], {}

    # Find all parts of speech
    for p in pos:
        options = p.find_all("option")
        if options:
            for o in options:
                # Part of Speech : Abbreviation
                pos_dict[o.text] = o.get("value")

    # Find all possible forms of a word
    for f in forms:
        value = f.get("value")
        if value != "none":
            list_of_forms.append(value)

    # Find all links of every part of speech and their forms
    for pos, abbreviation in pos_dict.items():
        list_of_urls = []
        # Create links for current part of speech with all forms
        for f in list_of_forms:
            url = f"https://corpus.quran.com/search.jsp?q=pos%3A{abbreviation}+{f}&s=1&page="
            list_of_urls.append(url)
        # Append list of urls to dict with POS as key
        all_links[pos] = list_of_urls

    return all_links

# Find the maximum number of pages for the current POS and the current form
def find_max_page(session, original_url):
    max = 1
    current_page = 1

    while True:
        url = f"{original_url}{current_page}"
        response = session.get(url)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # Find navigation panel of current page
        navPane = soup.find("div", class_="navigationPane")

        # If curr page has navPane, check its values
        if navPane:
            end_of_nav = int(navPane.find_all("a")[-2].text)
            if end_of_nav == 2:
                return 2
            # If current end of nav is greater than max, replace and set index at current
            if end_of_nav > max:
                max = end_of_nav
                current_page = end_of_nav
            # If equal, go to end of nav page
            elif end_of_nav == max:
                current_page = end_of_nav
            # End of nav page and current navbar end is less than max, then we are already at last page
            elif end_of_nav < max:
                return max
        # If page has no navPane, then it only has one page
        else:
            return max

# Save dataframe to CSV
def save_rows(rows, file_name):
    df = pd.DataFrame(rows,
                      columns=['surah', 'ayat', 'position', 'english', 'arabic', 'pos', 'form'])
    df.to_csv(file_name, index=False)

