import scrape_functions as sf
import time, requests
from concurrent.futures import ThreadPoolExecutor
data_dir = sf.find_project_root() / "data" 

# Sort results by surah:ayat
def sort_results(results):
    return sorted(results, key=lambda x:(int(x[0]), int(x[1])))

# Return data from current URL
def process_url(url, pos, form_num):
    s = requests.Session()
    num_pages = sf.find_max_page(s, url)
    if num_pages > 0:
        rows = sf.get_words(s, url, num_pages, pos, form_num)
        s.close()
        return rows
    s.close()
    return []

def main():
    # New ThreadPool and requests Session
    s = requests.Session()
    executor = ThreadPoolExecutor(max_workers=10)

    # Start counting execution time
    start = time.time()

    # Get all possible links to process
    all_links = sf.get_links(s)

    for pos, links in all_links.items():
        i = 1
        futures = []

        # Go through each URL
        for url in links:
            future = executor.submit(process_url, url, pos, i)
            futures.append(future)
            i += 1

        current_pos = []
        for future in futures:
            rows = future.result()
            current_pos.extend(rows)

        # Sort and save all rows of current POS to CSV
        current_pos = sort_results(current_pos)
        sf.save_rows(current_pos, data_dir / f"{pos}.csv")

    end = time.time()
    print(f"Total execution time: {end-start} seconds")

    # Close ThreadPool and requests Session
    executor.shutdown(wait=True)
    s.close()

if __name__ == "__main__":
    main()
