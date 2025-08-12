import os
import sys
import subprocess

COLOR_MAP = {
    "31": "Red",
    "32": "Green",
    "33": "Yellow",
    "34": "Blue",
    "35": "Magenta",
    "36": "Cyan",
    "37": "White",
    
}

def ps_print(text, color=None, end="\n", no_newline=False):
    if color is None:
        print(text, end=end)
        return

    if color in COLOR_MAP:
        ps_color = COLOR_MAP[color]
    else:
        ps_color = color  

    safe_text = text.replace("'", "''")

    no_newline_flag = "-NoNewline" if no_newline else ""

    ps_command = f"Write-Host '{safe_text}' -ForegroundColor {ps_color} {no_newline_flag}"
    if end == "\n" and not no_newline:
        full_command = ps_command
    else:
        full_command = ps_command

    subprocess.run(["powershell", "-NoProfile", "-Command", full_command])

    if end != "\n" and not no_newline:
        print(end, end="")


try:
    import requests  
except ImportError:
    ps_print("Error:", "31")
    ps_print("'requests'", "33")
    ps_print("pip install requests", "36")
    sys.stderr.write("\nThe 'requests' python package is not installed.\n\n\n\nPlease install it by running:\n")
    sys.stderr.flush()
    sys.exit(1)

ps_print("\nwelcome to Stemmy, the bulk file downloader\n\n", None)
ps_print("open ", "32", no_newline=True)
ps_print('"HOW TO USE.txt"', "33", no_newline=True)
ps_print(" text file to see how to use this python script\n\n", "32")


def download_file(url, destination_folder):
    local_filename = url.split('/')[-1]
    output_path = os.path.join(destination_folder, local_filename)
    
    try:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()  
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=131072):
                    if chunk:  
                        f.write(chunk)
        ps_print("Downloaded:", "36", no_newline=True)
        ps_print(f' "{local_filename}" to ', None, no_newline=True)
        ps_print(os.getcwd() + f'\\downloads\\', "31", no_newline=True)
        ps_print(local_filename, "31")
    except Exception as e:
        ps_print("Error downloading", "31", no_newline=True)
        print(f" {url}: {e}")

def download_links_from_file(file_path, destination_folder="downloads"):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    try:
        with open(file_path, 'r') as file:
            links = file.readlines()
    except FileNotFoundError:
        ps_print("Error:", "31")  
        print(f"The file '{file_path}' was not found.")
        return
    
    for line in links:
        url = line.strip()
        if url:  
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'http://' + url
            ps_print("Downloading from:", "33")
            print(url)
            download_file(url, destination_folder)
            print("")

if __name__ == "__main__":
    links_file = "links.txt"  
    output_folder = "downloads"
    download_links_from_file(links_file, output_folder)