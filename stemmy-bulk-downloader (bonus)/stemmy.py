import os
import sys


def colored(text, color_code, bright=False):
    brightness = "1;" if bright else ""
    return f"\033[{brightness}{color_code}m{text}\033[0m"

try:
    import requests  
except ImportError:
    error_message = colored("Error:", "31", bright=True)  
    package_name = colored("'requests'", "33", bright=True) 
    install_command = colored("pip install requests", "36", bright=True) 

    sys.stderr.write(
        f"{error_message} The {package_name} python package is not installed.\n\n\n\n"
        f"Please install it by running:\n"
        f"{install_command}\n"
    )
    sys.exit(1)

print("\nwelcome to Stemmy, the bulk file downloader\n\n")
mainMsg1 = colored('open', "32", bright=True) 
mainMsg2 = colored('text file to see how to use this python script\n\n', "32", bright=True) 
mainMsg3 = colored('"HOW TO USE.txt"', "33", bright=True) 
print(f'{mainMsg1} {mainMsg3} {mainMsg2}')

def download_file(url, destination_folder):
    local_filename = url.split('/')[-1]
    output_path = os.path.join(destination_folder, local_filename)
    
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  
                        f.write(chunk)
        downloader_msg = colored("Downloaded:", "36", bright=True) 
        download_dir_msg = colored(os.getcwd() + f'\\downloads\\', "31", bright=True)
        local_filename_with_color = colored(f"{local_filename}", "31", bright=True) 
        print(f'{downloader_msg} "{local_filename}" to {download_dir_msg}{local_filename_with_color}')
    except Exception as e:
        error_message2 = colored("Error downloading", "31", bright=True)
        print(f"{error_message2} {url}: {e}")

def download_links_from_file(file_path, destination_folder="downloads"):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    try:
        with open(file_path, 'r') as file:
            links = file.readlines()
    except FileNotFoundError:
        error_message1 = colored("Error:", "31", bright=True)  
        print(f"{error_message1} The file '{file_path}' was not found.")
        return
    
    for line in links:
        url = line.strip()
        if url:  
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'http://' + url
            msg = colored("Downloading from:", "33", bright=True) 
            print(f"{msg} {url}")
            download_file(url, destination_folder)

if __name__ == "__main__":
    links_file = "links.txt"  
    output_folder = "downloads"
    download_links_from_file(links_file, output_folder)
