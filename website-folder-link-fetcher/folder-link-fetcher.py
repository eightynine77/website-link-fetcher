import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import datetime # Added for default filename timestamp

def fetch_index_links(url):
    links = []
    error_message = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=15) 
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')

        title_tag = soup.find('title')
        if not title_tag or not any(term in title_tag.get_text().lower() for term in ['index of', 'directory listing for']):
            error_message = f"Error: The page at {url} does not appear to be an 'Index of' page (title mismatch)."
            return None, error_message

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            link_text = a_tag.get_text(strip=True) # Get link text for filtering

            if '?' in href:
                continue
            if link_text in ['Name', 'Last modified', 'Size', 'Description', 'Parent Directory']:
                continue
            if href.endswith('/') and len(href) > 1 and href != '../':
                 pass 
            elif href == '/' or href == '../':
                 continue
            # Ignore empty hrefs or javascript links
            if not href or href.lower().startswith('javascript:'):
                continue

            absolute_link = urljoin(url, href)

            parsed_base = urlparse(url)
            parsed_link = urlparse(absolute_link)
            base_path = parsed_base.path.rstrip('/')
            link_path = parsed_link.path.rstrip('/')
            if parsed_link.scheme == parsed_base.scheme and \
               parsed_link.netloc == parsed_base.netloc and \
               link_path == base_path and \
               parsed_link.query == parsed_base.query: # Also compare query params
                 continue

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
        error_message = f"An unexpected error occurred during fetching/parsing: {e}"
        return None, error_message

def save_links_to_file(filename, links, script_name, url):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Links fetched by {script_name} from: {url}\n")
            f.write(f"# Total links: {len(links)}\n")
            f.write("#" + "-"*30 + "\n") # Separator
            if links:
                for link in links:
                    f.write(link + '\n')
            else:
                f.write("(No links were found)\n")
        return True, None
    except IOError as e:
        error_message = f"Error writing to file {filename}: {e}"
        return False, error_message
    except Exception as e:
        error_message = f"An unexpected error occurred during file saving: {e}"
        return False, error_message


if __name__ == "__main__":
    script_name = os.path.basename(__file__)

    target_url = input("Enter the URL of the 'Index of' page: ")

    parsed_input_url = urlparse(target_url)
    if not parsed_input_url.scheme or not parsed_input_url.netloc:
         print("Error: Invalid URL format. Please include scheme (http/https) and domain.")
    elif not parsed_input_url.path or not parsed_input_url.path.endswith('/'):
         if '.' not in os.path.basename(parsed_input_url.path): 
              target_url += '/'
              print(f"Info: Added trailing slash. Using URL: {target_url}")


    if target_url.startswith(('http://', 'https://')):
        print(f"\nFetching links from {target_url}...")
        found_links, error = fetch_index_links(target_url)

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
                    default_filename = f"links_{urlparse(target_url).netloc}_{datetime.datetime.now():%Y%m%d_%H%M%S}.txt"
                    filename_prompt = f"Enter filename to save as (leave blank for default: '{default_filename}'): "
                    output_filename = input(filename_prompt).strip()
                    if not output_filename:
                        output_filename = default_filename

                    print(f"Saving links to '{output_filename}'...")
                    success, save_error = save_links_to_file(output_filename, found_links, script_name, target_url)
                    if success:
                        print("Links saved successfully.")
                    else:
                        print(save_error) 
                    break 
                elif save_choice in ['no', 'n']:
                    print("Okay, links will not be saved.")
                    break 
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")
        else:
             print("An unknown issue occurred after fetching.")
