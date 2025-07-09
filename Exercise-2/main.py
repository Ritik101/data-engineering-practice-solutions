import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration ---
url = 'https://www.ncei.noaa.gov/data/local-climatological-data/access/2021/'
# Use a raw string (r'') for Windows paths to avoid issues with backslashes acting as escape characters.
DOWNLOAD_DIR = r'C:\Projects\Docker\Exercises\Exercise-2\Downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
DEFAULT_WAIT_TIME = 10 

def run_web_scrap():
    driver = None # Initialize driver to None, good practice for the finally block
    downloaded_file_name = None # Variable to store the name of the file actually clicked/downloaded

    try:
        # --- 1. Configure Chrome Options for Downloads ---
        chrome_options = Options()

        # Setting Download Preferences
        prefs = {
            'download.default_directory': DOWNLOAD_DIR,
            'download.prompt_for_download': False, # Suppresses download prompt
            'download.directory_upgrade': True,    # Important for consistent behavior
            'safeBrowse.enabled': True           # Improves security (typo was 'safeBrowse.enabled')
        }
        chrome_options.add_experimental_option('prefs', prefs)

        # Maximize the browser window for better visibility (optional)
        chrome_options.add_argument('--start-maximized')

        # Optional: Run in headless mode (no visible browser window) for server environments
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu') # Often needed for headless on Windows/Linux

        # --- 2. Initialization of the WebDriver ---
        # ChromeDriverManager automatically handles downloading the correct ChromeDriver
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), # Use Service for the executable path
            options=chrome_options                            # Pass options separately
        )

        print(f'Loading webpage: {url}')
        driver.get(url)

        # --- 3. Wait for the main table to be present on the page ---
        # We use WebDriverWait to ensure the HTML table is loaded before we try to find elements within it.
        WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located((By.TAG_NAME, 'table'))
        )
        print("Webpage loaded and table found.")
        time.sleep(1) # Small pause for page rendering, optional

        # --- 4. Find the Table Body and Iterate through Rows ---
        # First, find the table element.
        table = driver.find_element(By.TAG_NAME, 'table')

        # Get all rows in the table body.
        rows = table.find_elements(By.TAG_NAME, 'tr')

        target_file_link = None
        # 2024-01-19 10:27 does exist on the example page.So taking a different one, You can put your desired timestamp
        target_timestamp = "2024-01-19 14:55"     

        # Iterate through each row to find the desired file
        # We start from index 2 to skip the header row and the <hr> row as seen on NOAA page structure.
        for i, row in enumerate(rows):
            if i < 2:  # Skip header and separator rows
                continue

            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) >= 2:  # Ensure there are enough columns (at least Name and Last modified)
                # The 'Name' is in the first <td> (index 0)
                name_cell = cells[0]
                file_link_element = name_cell.find_element(By.TAG_NAME, 'a')
                current_file_name = file_link_element.text # Gets the visible text of the file link

                # The 'Last modified' is in the second <td> (index 1)
                last_modified_cell = cells[1]
                # .text gets visible text; .strip() removes leading/trailing whitespace
                current_timestamp = last_modified_cell.text.strip()

                print(f'Checking file: {current_file_name}, Last modified: {current_timestamp}')

                # Compares the extracted timestamp with our target
                if current_timestamp == target_timestamp:
                    print(f"Found target File: {current_file_name} with timestamp: {current_timestamp}")
                    target_file_link = file_link_element
                    downloaded_file_name = current_file_name
                    break

        # --- 5. Act on the Found Link ---
        if target_file_link:
            target_file_link.click()  # Click the link to trigger the download
            print(f"Clicked on {downloaded_file_name} to initiate download.")
 
            # Give the browser some time to process the download.
            # This is a critical time.sleep for download completion.
            # You might need to increase this if files are large or internet is slow.
            # A more advanced approach would be to wait until the file appears in the directory.
            print(f"Waiting {DEFAULT_WAIT_TIME + 7} seconds for download to complete...")
            time.sleep(DEFAULT_WAIT_TIME + 7)
            print(f"Download process initiated. Check {DOWNLOAD_DIR} for the file.")

            # --- 6. Data Analysis with Pandas ---
            # Ensure we're reading the file that was actually downloaded.
            # Use os.path.join for robust path construction.
            csv_file_path = os.path.join(DOWNLOAD_DIR, downloaded_file_name)

            print(f"\nAttempting to read CSV file: {csv_file_path}")
            if os.path.exists(csv_file_path):
                try:
                    df = pd.read_csv(csv_file_path)

                    # Convert temperature columns to numeric, coercing errors to NaN
                    # This is CRUCIAL as these columns often contain non-numeric data like 'T' or blanks.
                    df['HourlyDryBulbTemperature'] = pd.to_numeric(df['HourlyDryBulbTemperature'], errors='coerce')
                    df['HourlyDewPointTemperature'] = pd.to_numeric(df['HourlyDewPointTemperature'], errors='coerce')
                    # Convert DailyAverageDryBulbTemperature too for consistency if needed for other ops
                    df['DailyAverageDryBulbTemperature'] = pd.to_numeric(df['DailyAverageDryBulbTemperature'], errors='coerce')

                    # Find the highest 'HourlyDryBulbTemperature' value
                    # .max() requires parentheses to call the method.
                    max_dry_bulb_temp = df['HourlyDryBulbTemperature'].max()

                    # Filter the DataFrame to show all rows with this maximum temperature
                    rows_with_max_temp = df[df['HourlyDryBulbTemperature'] == max_dry_bulb_temp]

                    print(f"\nSuccessfully read CSV. Highest 'HourlyDryBulbTemperature' found: {max_dry_bulb_temp}")
                    print(f'Rows with the highest HourlyDryBulbTemperature:\n{rows_with_max_temp}')

                except FileNotFoundError:
                    print(f"Error: The file {csv_file_path} was not found. Download might have failed or name is incorrect.")
                except pd.errors.EmptyDataError:
                    print(f"Error: The file {csv_file_path} is empty.")
                except Exception as pandas_error:
                    print(f"An error occurred during Pandas processing: {pandas_error}")
                    import traceback
                    traceback.print_exc() # Print full traceback for debugging Pandas issues
            else:
                print(f"Error: Downloaded file '{downloaded_file_name}' not found at '{DOWNLOAD_DIR}'.")

        else:
            print(f"File with timestamp '{target_timestamp}' not found on the page. No download initiated.")

    except Exception as e:
        print(f"An unexpected error occurred during web scraping: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging Selenium issues
    finally:
        # Ensure the browser is closed even if an error occurs
        if driver: # Check if driver was successfully initialized
            driver.quit()
            print("Browser closed.")

# --- Executes the Web Scraping Function ---
if __name__ == "__main__":
    run_web_scrap()