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

url = 'https://www.ncei.noaa.gov/data/local-climatological-data/access/2021/'
DOWNLOAD_DIR = r'C:\Projects\Docker\Exercises\Exercise-2\Downloads'
os.makedirs(DOWNLOAD_DIR,exist_ok=True)
DEFAULT_WAIT_TIME = 5

def run_web_scrap():
    driver = None           # Driver Initializiation
    try:
        # --- 1. Configuration Chrome Options for Downloads ---
        chrome_options = Options()
        
        # Setting Download Preferences     
        prefs = {
            'download.default_directory': DOWNLOAD_DIR,
            'download.prompt_for_download': False, # Suppresses download prompt
            'download.directory_upgrade': True, # Important for consistent behavior
            'safeBrowse.enabled': True # Improves security
        }
        chrome_options.add_experimental_option('prefs', prefs)
        
        # Maximize the browser window for better visibility (optional)        
        chrome_options.add_argument('--start-maximized')
        
        # Optional: Run in headless mode (no visible browser window) for server environments
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu') # Often needed for headless on Windows/Linux

        # --- 2. Initializiation of the WebDriver ---
        # ChromeDriverManager automatically handles downloading the correct ChromeDriver
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), # Use Service for the executable path
            options=chrome_options                           # Pass options separately
        )
    
        
        # Use Selenium as usual
        driver.get(url)
        print(f'Loading webpage: {url}')
        
         # --- 4. Wait for the main table to be present on the page ---
        # We use WebDriverWait to ensure the HTML table is loaded before we try to find elements within it.
        WebDriverWait(driver, DEFAULT_WAIT_TIME).until(
            EC.presence_of_element_located((By.TAG_NAME, 'table'))
        )
        
         # --- 5. Find the Table Body and Iterate through Rows ---
        # First, find the table element.
        table = driver.find_element(By.TAG_NAME, 'table')

        # Get all rows in the table body, skipping the header rows.
        # We look for <tr> tags that are children of <tbody>
        rows = table.find_elements(By.TAG_NAME, 'tr')
        
        target_file_link = None
        # 2024-01-19 10:27 does exist on the example page.So taking a different one, You can put your desired timestamp
        target_timestamp = "2024-01-19 15:55" 
        
        # Iterate through each row to find the desired file
        # We start from index 2 to skip the header row and the <hr> row
        for i, row in enumerate(rows):
            if i < 2:      # Skip the header and separator rows
                continue
        
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) > 2:       # Ensure there are enough columns (at least Name and Last modified)
                # The 'Name' is in the first <td> (index 0)
                name_cell = cells[0]
                file_link_element = name_cell.find_element(By.TAG_NAME, 'a')
                file_name = file_link_element.text      # Gets the visible text of the file link
                
                # The 'Last modified' is in the second <td> (index 1)
                last_modified_cell = cells[1]
                # .text gets visible text; .strip() removes leading/trailing whitespace
                # The HTML shows a non-breaking space at the end, so strip is important.
                current_timestamp = last_modified_cell.text.strip()
                
                print(f'Checking file: {file_name}, Last modified: {current_timestamp}')

                 # Compares the extracted timestamp with our target          
                if current_timestamp == target_timestamp:    
                    print(f"Found target File: {file_name} with timestamp: {current_timestamp}")
                    target_file_link = file_link_element
                    break
        
        # --- 6. Act on the Found Link ---
        if target_file_link:
            target_file_link.click()         # Click the link to trigger the download
            print(f"Clicked on {target_file_link.text} to initiate download")
            # Give the browser some time to process the download.
            # This time might need adjustment based on file size and network speed.
            print(f"Waiting {DEFAULT_WAIT_TIME + 7} seconds for download to complete...")
            time.sleep(DEFAULT_WAIT_TIME + 7)
            print(f"Download process initiated. Check {DOWNLOAD_DIR} for the file")
        else:
            print(f"File with timstamp: {current_timestamp} not found on the page")
        
        df = pd.read_csv('C:/Projects/Docker/Exercises/Exercise-2/Downloads/01389099999.csv')
        max_temp = df['HourlyDewPointTemperature'].max
        
        rows_with_max_temp = df[df['HourlyDewPointTemperature'] == max_temp]
        print(f'Printing rows with maximum temperature\n: {rows_with_max_temp}')
        
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
        