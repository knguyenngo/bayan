import scrape_functions as sf
import time

forms = {"i": [247, 468, 36],
         "ii": [26, 6, 1],
         "iii": [7, 4, 1],
         "iv": [70, 20, 3],
         "v": [9, 2, 1],
         "vi": [2, 1, 1],
         "vii": [2, 1, 0],
         "viii": [20, 4, 1],
         "ix": [1, 1, 0],
         "x": [8, 2, 1],
         "xi": [0, 1, 0],
         "xii": [1, 1, 1]
         }

data_dir = sf.find_project_root() / "backend" / "data"

def main():
    start = time.time()

    verbs, nouns, adjectives = [], [], []
    i = 1

    for f, p in forms.items():

        verb_url = f"https://corpus.quran.com/search.jsp?q=pos%3AV+({f})&s=1&page="
        noun_url = f"https://corpus.quran.com/search.jsp?q=pos%3AN+({f})&s=1&page="
        adj_url = f"https://corpus.quran.com/search.jsp?q=pos%3AADJ+({f})&s=1&page="

        v = sf.get_words(verb_url, p[0], "verb", i)
        n = sf.get_words(noun_url, p[1], "noun", i)
        a = sf.get_words(adj_url, p[2], "adjective", i)

        verbs.extend(v)
        nouns.extend(n)
        adjectives.extend(a)

        i += 1

    # Sort by surah number
    verbs = sorted(verbs, key=lambda x:(int(x[0]), int(x[1])))
    nouns = sorted(nouns, key=lambda x:(int(x[0]), int(x[1])))
    adjectives = sorted(adjectives, key=lambda x:(int(x[0]), int(x[1])))

    sf.save_rows(verbs, data_dir / "verbs.csv")
    sf.save_rows(nouns, data_dir / "nouns.csv")
    sf.save_rows(adjectives, data_dir / "adjectives.csv")

    end = time.time()
    print(f"Total execution time: {end-start} seconds")

if __name__ == "__main__":
    main()
