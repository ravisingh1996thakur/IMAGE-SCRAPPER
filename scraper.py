from selenium import webdriver
import time
import os
import requests
from urllib.parse import urlparse
from selenium.webdriver.chrome.service import Service

def search_and_download(search_term:str, driver_path:str, target_path='./images', number_images=5):
    
    s = Service(driver_path)
    s.start()
    options = webdriver.ChromeOptions()
    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=VizDisplayCompositor")
    
    with webdriver.Chrome(service=s, options=options) as wd:
        res = wd.get(f"https://www.google.com/search?q={search_term}&tbm=isch")
        
        # scroll to the end of the page
        last_height = wd.execute_script("return document.body.scrollHeight")
        
        while True:
            wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = wd.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
                
            last_height = new_height
            
        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        print(f"Found {len(thumbnail_results)} thumbnail images.")
        
        for index, thumbnail in enumerate(thumbnail_results[:number_images]):
            try:
                thumbnail.click()
                time.sleep(2)
                actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
                
                for actual_image in actual_images:
                    if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                        parsed_url = urlparse(actual_image.get_attribute('src'))
                        filename = os.path.basename(parsed_url.path)
                        response = requests.get(actual_image.get_attribute('src'))
                        with open(os.path.join(target_path, f"{search_term}_{index+1}_{filename}"), 'wb') as f:
                            f.write(response.content)
                        print(f"Downloaded image {index+1} of {number_images}.")
                        
            except Exception as e:
                print(f"Error occurred while downloading image {index+1}: {e}")
        
        wd.quit()

if __name__ == "__main__":
    search_term = "cats"
    DRIVER_PATH = '/usr/local/bin/chromedriver'
    search_and_download(search_term=search_term, driver_path=DRIVER_PATH, number_images=150)
