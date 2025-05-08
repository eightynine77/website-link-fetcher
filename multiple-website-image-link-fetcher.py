import msvcrt
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import datetime

def fetch_all_image_links(url, keyword):
    """Fetches image URLs that contain the keyword from a web page."""
    links = []
    error_message = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=1)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        for img_tag in soup.find_all('img', src=True):
            src_url = img_tag['src']
            if not src_url or src_url.lower().startswith('javascript:'):
                continue
            absolute_link = urljoin(url, src_url)
            if keyword.lower() in absolute_link.lower():  # Filter by keyword
                links.append(absolute_link)

        links = sorted(list(set(links)))
        return links, None

    except requests.exceptions.Timeout:
        return None, f"Timeout: {url}"
    except requests.exceptions.RequestException as e:
        status = f"Status Code: {e.response.status_code}" if e.response else "N/A"
        return None, f"Error fetching {url}: {e} ({status})"
    except Exception as e:
        return None, f"Unexpected error with {url}: {e}"

def save_all_results_to_file(filename, combined_links, script_name, url_count):
    """Saves the combined image links (deduplicated and sorted) to a text file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# All image links fetched by {script_name}\n")
            f.write(f"# From {url_count} URLs\n")
            f.write(f"# Filtered by keyword\n")
            f.write(f"# Generated at: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")
            f.write("#" + "="*60 + "\n")
            f.write(f"# Total image links found: {len(combined_links)} (note: duplicate links are removed)\n\n")
            for link in combined_links:
                f.write(link + '\n')
        return True, None
    except Exception as e:
        return False, f"Error saving file: {e}"

if __name__ == "__main__":
    script_name = os.path.basename(__file__)
    input_file = input("Enter the path to the text file containing web page URLs: ").strip()

    if not os.path.isfile(input_file):
        print(f"Error: File '{input_file}' not found.")
        print("\nPress any key to exit...")
        msvcrt.getch()
        exit()

    with open(input_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("No valid URLs found in the file.")
        print("\nPress any key to exit...")
        msvcrt.getch()
        exit()

    keyword = input("Enter keyword to filter image links: ").strip()
    if not keyword:
        print("Keyword cannot be empty.")
        print("\nPress any key to exit...")
        msvcrt.getch()
        exit()

    all_results = {}

    for url in urls:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            print(f"\nFetching image links from: {url}")
            print("Invalid URL format.")
            all_results[url] = "Invalid URL format"
            continue

        print(f"\nFetching image links from: {url}")
        links, error = fetch_all_image_links(url, keyword)
        if error:
            print(error)
            all_results[url] = error
        else:
            print(f"Found {len(links)} image links.")
            all_results[url] = links

    # Combine and deduplicate
    combined_links = []
    for result in all_results.values():
        if isinstance(result, list):
            combined_links.extend(result)

    combined_links = sorted(set(combined_links))

    if combined_links:
        for link in combined_links:
            print(link)
    else:
        print("(No matching image links found across all pages)")

    # Ask to save
    while True:
        print(f"\n\n--- Combined Image Links ({len(combined_links)} total) ---")
        print("")
        print(f"note: duplicate links are removed, filtered by keyword: '{keyword}'")
        print("")
        save_choice = input("\nDo you want to save all image links to a text file? (yes/no): ").lower().strip()
        if save_choice in ['yes', 'y']:
            default_filename = f"filtered_image_links_{keyword}_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"
            output_filename = input(f"Enter filename to save as (blank for default '{default_filename}'): ").strip()
            if not output_filename:
                output_filename = default_filename
            print(f"Saving results to '{output_filename}'...")
            success, save_error = save_all_results_to_file(output_filename, combined_links, script_name, len(all_results))
            if success:
                print("Image links saved successfully.")
            else:
                print(save_error)
            break
        elif save_choice in ['no', 'n']:
            print("Okay, results will not be saved.")
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    print("\nProcess completed.")
    print("\nPress any key to close this python script...")
    msvcrt.getch()