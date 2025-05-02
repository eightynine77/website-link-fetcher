import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import datetime
import msvcrt
import time 

REQUEST_TIMEOUT = 20 
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' # Example User Agent

def fetch_links_in_web_page(url, text_pattern_to_search):
    links = []
    error_message = None
    print(f"  Fetching: {url}")
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        response.raise_for_status() 

        soup = BeautifulSoup(response.content, 'html.parser')
        base_url = response.url 

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()

            if not href or href.lower().startswith(('javascript:', 'mailto:')):
                continue

            absolute_link = urljoin(base_url, href)

            if text_pattern_to_search in absolute_link:
                links.append(absolute_link)

        links = sorted(list(set(links)))
        print(f"  Found {len(links)} matching links on this page.")
        return links, None

    except requests.exceptions.Timeout:
        error_message = f"Error: The request to {url} timed out after {REQUEST_TIMEOUT} seconds."
        return [], error_message 
    except requests.exceptions.HTTPError as e:
        error_message = f"Error: HTTP Error {e.response.status_code} for URL {url}"
        return [], error_message
    except requests.exceptions.ConnectionError:
        error_message = f"Error: Could not connect to {url}. Check network or URL validity."
        return [], error_message
    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching URL {url}: {e}"
        return [], error_message
    except Exception as e:
        error_message = f"An unexpected error occurred while processing {url}: {e}"
        return [], error_message

def save_links_to_file(filename, links, script_name, input_file_path, text_pattern):
    """Saves the collected links to a text file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Links containing '{text_pattern}' fetched by {script_name}\n")
            f.write(f"# Source URL list file: {input_file_path}\n")
            f.write(f"# Fetched on: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")
            f.write(f"# Total unique matching links found: {len(links)}\n")
            f.write("#" + "-"*40 + "\n\n") 
            if links:
                for link in links:
                    f.write(link + '\n')
            else:
                f.write(f"(No links containing '{text_pattern}' were found across the processed URLs)\n")
        return True, None
    except IOError as e:
        error_message = f"Error writing to file {filename}: {e}"
        return False, error_message
    except Exception as e:
        error_message = f"An unexpected error occurred during file saving: {e}"
        return False, error_message

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except ValueError:
        return False

def add_scheme_if_missing(url):
    parsed = urlparse(url)
    if not parsed.scheme:
        
        if '.' in parsed.path and '/' not in parsed.path.split('.')[0]: 
             print(f"  Warning: Assuming 'http://' for '{url}'")
             return 'http://' + url
    return url


if __name__ == "__main__":
    script_name = os.path.basename(__file__)
    print(f"--- {script_name} ---")
    print(f"")
    print(f"")
    print("Fetches links containing specific text from multiple web pages listed in a file.")

    while True:
        url_file_path = input("Enter the path to the text file containing the list of web page URLs: ").strip()
        if os.path.isfile(url_file_path):
            break
        else:
            print(f"Error: File not found at '{url_file_path}'. Please check the path and try again.")

    text_pattern = input("Enter the text to search for within the links: ").strip()
    if not text_pattern:
        print("Warning: No text provided. The script will fetch ALL valid links.")

    urls_to_process = []
    try:
        with open(url_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                url = line.strip()
                if url and not url.startswith('#'): 
                    urls_to_process.append(url)
    except Exception as e:
        print(f"Error reading URL file '{url_file_path}': {e}")
        exit() 

    if not urls_to_process:
        print(f"No URLs found in '{url_file_path}'. Exiting.")
        exit()

    print(f"\nFound {len(urls_to_process)} URLs in '{os.path.basename(url_file_path)}'.")
    print(f"Searching for links containing: '{text_pattern}'")

    all_found_links = []
    errors_encountered = []
    processed_count = 0
    skipped_count = 0

    print("\nProcessing URLs...")
    total_urls = len(urls_to_process)
    for i, url in enumerate(urls_to_process):
        print(f"\n[{i+1}/{total_urls}] Processing: {url}")

        url_to_fetch = add_scheme_if_missing(url)

        if not is_valid_url(url_to_fetch):
            error_msg = f"Skipped: Invalid URL format '{url}' (missing scheme or domain?)"
            print(f"  {error_msg}")
            errors_encountered.append(f"{url}: {error_msg}")
            skipped_count += 1
            continue

        found_links_for_url, error = fetch_links_in_web_page(url_to_fetch, text_pattern)

        if error:
            print(f"  {error}")
            errors_encountered.append(f"{url_to_fetch}: {error}")
        if found_links_for_url:
            all_found_links.extend(found_links_for_url) 

        processed_count += 1
        # Optional: Add a small delay between requests to be polite to servers
        # time.sleep(0.5) # Sleep for 0.5 seconds

    print("\n--- Processing Complete ---")

    unique_found_links = sorted(list(set(all_found_links)))

    print(f"\nProcessed {processed_count} URLs.")
    if skipped_count > 0:
       print(f"Skipped {skipped_count} URLs due to invalid format.")
    print(f"\n{script_name} has fetched a total of {len(unique_found_links)} unique links containing '{text_pattern}'.")

    if errors_encountered:
        print("\n--- Errors Encountered During Processing ---")
        for err in errors_encountered:
            print(f"- {err}")
        print("------------------------------------------")

    if unique_found_links:
        print("\n--- Found Links ---")
        for link in unique_found_links:
            print(link)
        print("-------------------")

        while True:
            save_choice = input("\nDo you want to save these unique links to a text file? (yes/no): ").lower().strip()
            if save_choice in ['yes', 'y']:
                input_filename_base = os.path.splitext(os.path.basename(url_file_path))[0]
                default_filename = f"{input_filename_base}_links_{text_pattern}_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"
                safe_pattern = "".join(c if c.isalnum() else "_" for c in text_pattern) if text_pattern else "all"
                default_filename = f"{input_filename_base}_links_{safe_pattern}_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"

                filename_prompt = f"Enter filename to save as (leave blank for default: '{default_filename}'): "
                output_filename = input(filename_prompt).strip()
                if not output_filename:
                    output_filename = default_filename

                print(f"Saving links to '{output_filename}'...")
                success, save_error = save_links_to_file(output_filename, unique_found_links, script_name, url_file_path, text_pattern)
                if success:
                    print("Links saved successfully.")
                    print("")
                    print("")
                    print("press any key to close this python script...")
                    msvcrt.getch()
                else:
                    print(save_error)
                break 
            elif save_choice in ['no', 'n']:
                print("Okay, links will not be saved.")
                print("")
                print("")
                print("press any key to close this python script...")
                msvcrt.getch()
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")
    elif not errors_encountered:
        print(f"\nNo links containing '{text_pattern}' were found in any of the processed URLs.")
    else:
        print("\nNo links were successfully extracted, check the error messages above.")

    print("\n--- Script Finished ---")