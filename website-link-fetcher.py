import msvcrt
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import datetime 

def fetch_links_in_web_page(url):
    links = []
    error_message = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=20)
        response.raise_for_status() 

        soup = BeautifulSoup(response.content, 'html.parser')

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']

            if not href or href.lower().startswith('javascript:'):
                continue

            absolute_link = urljoin(url, href)

            if text_pattern in absolute_link:
                links.append(absolute_link)

        links = sorted(list(set(links)))

        return links, None

    except requests.exceptions.Timeout:
        error_message = f"Error: The request to {url} timed out."
        return None, error_message
    except requests.exceptions.RequestException as e:
        error_message = f"Error fetching URL {url}: {e}"
        return None, error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        return None, error_message

def save_links_to_file(filename, links, script_name, url):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# links fetched by {script_name} from: {url}\n")
            f.write(f"# Total attachment links: {len(links)}\n")
            f.write("#" + "-"*30 + "\n") # Separator
            if links:
                for link in links:
                    f.write(link + '\n')
            else:
                f.write(f"(No links containing {text_pattern} were found)\n")
        return True, None
    except IOError as e:
        error_message = f"Error writing to file {filename}: {e}"
        return False, error_message
    except Exception as e:
        error_message = f"An unexpected error occurred during file saving: {e}"
        return False, error_message


if __name__ == "__main__":
    script_name = os.path.basename(__file__)

    target_url = input("Enter the link of the web page: ")

    text_pattern = input("Enter the text you want to search: ")

    parsed_input_url = urlparse(target_url)
    if not parsed_input_url.scheme or not parsed_input_url.netloc:
          print("Error: Invalid URL format. Please include scheme (e.g., http or https) and domain.")

    if target_url.startswith(('http://', 'https://')):
        print(f"\nFetching links from {target_url}...")
        found_links, error = fetch_links_in_web_page(target_url)

        if error:
            print(error)
        elif found_links is not None:
            print(f"\n{script_name} has fetched a total of {len(found_links)} links:")
            if found_links:
                for link in found_links:
                    print(link)
            else:
                print("(No valid links found on the page)")

            while True:
                save_choice = input("\nDo you want to save these links to a text file? (yes/no): ").lower().strip()
                if save_choice in ['yes', 'y']:
                    default_filename = f"{urlparse(target_url).netloc}_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"
                    filename_prompt = f"Enter filename to save as (leave blank for default: '{default_filename}'): "
                    output_filename = input(filename_prompt).strip()
                    if not output_filename:
                        output_filename = default_filename

                    print(f"Saving links to '{output_filename}'...")
                    success, save_error = save_links_to_file(output_filename, found_links, script_name, target_url)
                    if success:
                        print("Links saved successfully.")
                        print("")
                        print("")
                        print("press any key to close this python script...")
                        msvcrt.getch()
                    else:
                        print(save_error)
                elif save_choice in ['no', 'n']:
                    print("Okay, links will not be saved.")
                    print("")
                    print("")
                    print("press any key to close this python script...")
                    msvcrt.getch()
                    break 
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")
        else:
             print("An unknown issue occurred after fetching.")