import scrape_functions as sf
import time, requests
from concurrent.futures import ThreadPoolExecutor

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

data_dir = sf.find_project_root() / "data" 

def main():
    verbs, nouns, adjectives, futures = [], [], [], []
    i = 1

    s = requests.Session()
    executor = ThreadPoolExecutor(max_workers=10)

    start = time.time()

    for f, p in forms.items():

        verb_url = f"https://corpus.quran.com/search.jsp?q=pos%3AV+({f})&s=1&page="
        noun_url = f"https://corpus.quran.com/search.jsp?q=pos%3AN+({f})&s=1&page="
        adj_url = f"https://corpus.quran.com/search.jsp?q=pos%3AADJ+({f})&s=1&page="

        v = executor.submit(sf.get_words, s, verb_url, p[0], "verb", i)
        n = executor.submit(sf.get_words, s, noun_url, p[1], "noun", i)
        a = executor.submit(sf.get_words, s, adj_url, p[2], "adjective", i)

        futures.extend([v, n, a])

        i += 1

    for future in futures:
        r = future.result()
        if r:
            pos = r[0][5]
            if pos == "verb":
                verbs.extend(r)
            elif pos == "noun":
                nouns.extend(r)
            elif pos == "adjective":
                adjectives.extend(r)

    # Sort by surah number
    verbs = sorted(verbs, key=lambda x:(int(x[0]), int(x[1])))
    nouns = sorted(nouns, key=lambda x:(int(x[0]), int(x[1])))
    adjectives = sorted(adjectives, key=lambda x:(int(x[0]), int(x[1])))

    sf.save_rows(verbs, data_dir / "t-verbs.csv")
    sf.save_rows(nouns, data_dir / "t-nouns.csv")
    sf.save_rows(adjectives, data_dir / "t-adjectives.csv")

    end = time.time()
    print(f"Total execution time: {end-start} seconds")

    executor.shutdown(wait=True)
    s.close()

if __name__ == "__main__":
    main()
