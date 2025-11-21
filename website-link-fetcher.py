import msvcrt
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import datetime
import sys

# --- NEW IMPORTS ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
# --- END NEW IMPORTS ---


def fetch_links_in_web_page(url, text_pattern=None, use_regex=False, timeout=20):
    """
    Fetch and return a deduplicated, sorted list of absolute http(s) links from the
    given URL whose absolute URL contains `text_pattern` (substring) or matches the
    regex `text_pattern` if use_regex=True. If text_pattern is None or empty, all
    http(s) links will be returned.

    This version uses Selenium to load the page, allowing JavaScript to render.

    Returns (links_list, error_message)
    """
    links = set()
    driver = None  # Initialize driver for the 'finally' block

    try:
        # --- Selenium Setup ---
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run without a visible browser window
        chrome_options.add_argument("--disable-gpu") # Recommended for headless mode
        chrome_options.add_argument("--log-level=3")  # Suppress console logs
        
        # Use a modern user agent
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Suppress webdriver-manager logs
        os.environ['WDM_LOG_LEVEL'] = '0' 
        
        # Use webdriver-manager to automatically get the correct driver
        driver_service = Service(ChromeDriverManager().install())
        
        driver = webdriver.Chrome(service=driver_service, options=chrome_options)
        
        # Set the timeout for the page *load*
        driver.set_page_load_timeout(timeout)
        
        # Fetch the page (this will wait for JS to run)
        driver.get(url)
        
        # response.url equivalent (gets URL after redirects)
        base_url = driver.current_url
        
        # response.content equivalent (gets final, rendered HTML)
        page_content = driver.page_source
        
        # --- End of Selenium-specific code ---

        soup = BeautifulSoup(page_content, 'html.parser')

        # --- YOUR ORIGINAL PARSING LOGIC (UNCHANGED) ---
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()

            # skip anchors, javascript: and non-http schemes (mailto:, tel:, etc.)
            if not href or href.startswith('#') or href.lower().startswith('javascript:'):
                continue

            # Build absolute URL using the response's final URL as base
            absolute_link = urljoin(base_url, href)

            # Normalize and ensure scheme is http or https
            parsed = urlparse(absolute_link)
            if parsed.scheme not in ('http', 'https'):
                continue

            normalized = parsed.geturl()

            # Pattern matching
            if text_pattern:
                if use_regex:
                    try:
                        if not re.search(text_pattern, normalized, flags=re.IGNORECASE):
                            continue
                    except re.error:
                        # invalid regex -> skip matching and treat as no match
                        continue
                else:
                    if text_pattern.lower() not in normalized.lower():
                        continue

            links.add(normalized)
        # --- END OF YOUR ORIGINAL LOGIC ---

        links_list = sorted(links)
        return links_list, None

    except TimeoutException:
        return None, f"Error: The request to {url} timed out (Selenium page load)."
    except WebDriverException as e:
        # Simplify the complex WebDriver error message
        error_lines = str(e).split('\n')
        simple_error = error_lines[0] if error_lines else "WebDriver error"
        return None, f"Error fetching URL {url} (WebDriver Error): {simple_error}"
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"
    finally:
        # CRITICAL: Always close the browser, even if an error occurs
        if driver:
            driver.quit()


def save_links_to_file(filename, links, script_name, source_url):
    """
    (This function is 100% identical to your original script)
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# links fetched by {script_name} from: {source_url}\n")
            f.write(f"# Retrieved at: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n")
            f.write(f"# Total links: {len(links)}\n")
            f.write("#" + "-"*40 + "\n")
            if links:
                for link in links:
                    f.write(link + '\n')
            else:
                f.write("(No links matched the given pattern)\n")
        return True, None
    except IOError as e:
        return False, f"Error writing to file {filename}: {e}"
    except Exception as e:
        return False, f"An unexpected error occurred during file saving: {e}"


if __name__ == '__main__':
    """
    (This main block is 100% identical to your original script)
    """
    script_name = os.path.basename(__file__)

    try:
        target_url = input("Enter the link of the web page: ").strip()

        if not target_url:
            print("No URL provided. Exiting.")
            sys.exit(1)

        parsed_input_url = urlparse(target_url)
        # If user omitted scheme, assume https
        if not parsed_input_url.scheme:
            target_url = 'https://' + target_url
            parsed_input_url = urlparse(target_url)

        if not parsed_input_url.scheme or not parsed_input_url.netloc:
            print("Error: Invalid URL format. Please include a valid domain (e.g., example.com) or http(s) scheme.")
            sys.exit(1)

        # Ask for search pattern (optional)
        text_pattern = input("Enter the text you want to search (leave blank to collect all http(s) links): ").strip()

        use_regex = False
        if text_pattern:
            regex_choice = input("Treat the text as a regular expression? (yes/no) [no]: ").strip().lower()
            use_regex = regex_choice in ('yes', 'y')

        print(f"\nFetching links from {target_url}...\n(This may take a moment as a browser is loading)")
        found_links, error = fetch_links_in_web_page(target_url, text_pattern=text_pattern if text_pattern else None, use_regex=use_regex)

        if error:
            print(error)
            sys.exit(1)

        print(f"{script_name} has fetched a total of {len(found_links)} links:")
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
                    print("\nPress any key to close this python script... (Windows only)")
                    try:
                        msvcrt.getch()
                    except Exception:
                        pass
                    break
                else:
                    print(save_error)
            elif save_choice in ['no', 'n']:
                print("Okay, links will not be saved.")
                print("\nPress any key to close this python script... (Windows only)")
                try:
                    msvcrt.getch()
                except Exception:
                    pass
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

    except KeyboardInterrupt:
        print('\nInterrupted by user. Exiting.')
        sys.exit(1)
