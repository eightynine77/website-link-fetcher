import subprocess
import os
import urllib.parse
import sys

def main():
    """
    Main function to run the bulk downloader script.
    """
    
    # 1. Ask the user for the path to the file containing links
    links_file_path = input("Enter the full path to your links file (e.g., C:\\Users\\YourUser\\Desktop\\links.txt): ")

    # 2. Check if the file exists
    if not os.path.isfile(links_file_path):
        print(f"\nError: File not found at '{links_file_path}'")
        print("Please check the path and try again.")
        return

    # 3. Create a directory to store the downloads
    # This folder will be created in the same directory where you run the script.
    download_dir = "bulk_downloads"
    os.makedirs(download_dir, exist_ok=True)
    
    print(f"\nFiles will be saved to the '{os.path.abspath(download_dir)}' folder.")
    print("Starting downloads...\n")

    # 4. Read all links from the file
    try:
        with open(links_file_path, 'r') as f:
            urls = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Initialize the counter for file naming
    file_counter = 1

    # 5. Loop through each URL in the file
    for url in urls:
        url = url.strip()  # Remove whitespace and newline characters

        # Skip any empty lines
        if not url:
            continue

        try:
            # --- Determine the output filename ---
            
            # Parse the URL to get its path component (e.g., "/images/photo.jpg")
            parsed_path = urllib.parse.urlparse(url).path
            
            # Extract the file extension (e.g., ".jpg") from the path
            # The first part (filename) is ignored, we only need the extension
            _, extension = os.path.splitext(parsed_path)

            # Create the new filename based on the counter and the original extension
            # Examples: "1.jpg", "2.pdf", "3" (if no extension was found)
            output_filename = f"{file_counter}{extension}"
            
            # Create the full path for the output file
            # e.g., "bulk_downloads/1.jpg"
            output_path = os.path.join(download_dir, output_filename)

            # --- Construct and run the curl command ---
            
            print(f"--- Processing link #{file_counter} ---")
            print(f"Downloading: {url}")
            print(f"Saving as:   {output_path}")

            # Command list for subprocess
            # 'curl.exe' : The program to run
            # '-L'       : Follow redirects (important for many download links)
            # '-o'       : Specify the output file path
            # output_path: Where to save the file
            # url        : The URL to download
            command = ["curl.exe", "-L", "-o", output_path, url]

            # Execute the command
            # check=True will raise an error if curl fails (e.g., 404 Not Found)
            subprocess.run(command, check=True)

            print(f"Successfully downloaded {output_filename}\n")

            # Increment the counter for the next file
            file_counter += 1

        except FileNotFoundError:
            # This error happens if 'curl.exe' isn't in the system's PATH
            print("\nFATAL ERROR: 'curl.exe' not found.")
            print("curl.exe is included in modern Windows 10/11.")
            print("Please ensure it's installed and your system's PATH variable is set correctly.")
            print("or make sure you have curl.exe in the same directory as this python script")
            return  # Stop the script
            
        except subprocess.CalledProcessError as e:
            # This error happens if curl runs but returns an error code
            print(f"Failed to download {url}. 'curl.exe' returned an error: {e}\n")
            # We continue to the next URL even if one fails
        
        except Exception as e:
            # Catch any other unexpected errors
            print(f"An unexpected error occurred for {url}: {e}\n")

    print(f"--- Download process finished ---")
    print(f"Processed {len(urls)} links. Saved {file_counter - 1} files.")

# Standard Python entry point
if __name__ == "__main__":
    main()