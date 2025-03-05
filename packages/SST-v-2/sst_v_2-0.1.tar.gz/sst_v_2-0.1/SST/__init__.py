from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from os import getcwd
import time

# Use preinstalled Edge WebDriver (if installed via pip)
edge_options = webdriver.EdgeOptions()
edge_options.add_argument("--use-fake-ui-for-media-stream")  # Allow microphone
edge_options.add_argument("--headless")  # Run in headless mode (no UI)
edge_options.add_argument("--disable-gpu")  # Prevents GPU-related issues
edge_options.add_argument("--log-level=3")  # Suppress unnecessary logs

# Initialize WebDriver with optimized options
driver = webdriver.Edge(service=Service(), options=edge_options)

# Open the local HTML file
website = f"file:///{getcwd()}/package/index.html"
driver.get(website)

# Define output file
rec_file = f"{getcwd()}/package/input.txt"

def listen():
    try:
        start_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "startButton")))
        start_button.click()
        print("Listening...")

        output_text = ""
        while True:
            output_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "output")))
            current_text = output_element.text.strip()

            if current_text and current_text != output_text:
                output_text = current_text
                with open(rec_file, "w") as file:
                    file.write(output_text.lower())
                print("USER: " + output_text)
                
            time.sleep(1)  # Reduce CPU usage
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()  # Close browser after execution

listen()
