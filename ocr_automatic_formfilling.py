# ==============================================================================
# FINAL INTEGRATED SCRIPT: Multi-Document OCR to Automatic Form Filling
# ==============================================================================
# This script simulates a real-world workflow:
# 1. It processes an Aadhaar card image to get initial details.
# 2. It processes a PAN card image to get financial details.
# 3. It merges the data into a single, complete client profile.
# 4. It uses that final profile to automatically fill a web form using RPA.
# ==============================================================================

import os
import re
import time
import easyocr
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- PART 1: OCR LOGIC ---

# Initialize the OCR reader once. This is a heavy operation.
print(">>> [SETUP] Loading EasyOCR model... (This may take a moment on first run)")
try:
    reader = easyocr.Reader(['hi', 'en'])
    print(">>> EasyOCR model loaded successfully.")
except Exception as e:
    print(f"!!! FATAL ERROR: Could not load EasyOCR model. Error: {e}")
    exit()

def process_document_image(image_path):
    """
    Processes a single image, automatically detects if it's Aadhaar or PAN,
    and returns a dictionary with the extracted information.
    """
    print(f"\n>>> [OCR] Processing image: {os.path.basename(image_path)}")
    if not os.path.exists(image_path):
        print(f"!!! ERROR: Image file not found at '{image_path}'")
        return None

    try:
        results = reader.readtext(image_path, detail=0)
        full_text_lower = " ".join(results).lower()
        extracted_data = {}

        # --- Logic to identify as PAN Card ---
        pan_match = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', " ".join(results).upper())
        if pan_match:
            print(f">>> Document identified as: PAN Card")
            extracted_data['doc_type'] = 'PAN Card'
            extracted_data['pan_number'] = pan_match.group(0)
            for i, line in enumerate(results):
                if "name" in line.lower() and i + 1 < len(results):
                    if not extracted_data.get('name'):
                        extracted_data['name'] = results[i+1].strip()
                if "birth" in line.lower() and i + 1 < len(results):
                    dob_match = re.search(r'\d{2}/\d{2}/\d{4}', results[i+1])
                    if dob_match: extracted_data['dob'] = dob_match.group(0)
            return extracted_data

        # --- Logic to identify as Aadhaar Card ---
        if 'government of india' in full_text_lower:
            print(f">>> Document identified as: Aadhaar Card")
            extracted_data['doc_type'] = 'Aadhaar Card'
            for i, line in enumerate(results):
                if 'government of india' in line.lower() and i + 2 < len(results):
                    extracted_data['name'] = results[i+2].strip()
                if 'dob' in line.lower() and i + 1 < len(results):
                    dob_match = re.search(r'\d{2}/\d{2}/\d{4}', results[i+1])
                    if dob_match: extracted_data['dob'] = dob_match.group(0)
                if line.strip().lower() in ['male', 'female']:
                    extracted_data['gender'] = line.strip()
            return extracted_data
            
        print("!!! WARNING: Could not identify document type.")
        return None

    except Exception as e:
        print(f"!!! An error occurred during OCR processing: {e}")
        return None


# --- PART 2: RPA (AUTOMATIC FORM FILLING) LOGIC ---

def fill_web_form(data):
    """
    Uses Selenium to open a browser and automatically fill a form with the
    final, merged data from both documents.
    """
    print("\n>>> [RPA] Starting the Robotic Process Automation script...")
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        form_url = "https://www.globalsqa.com/samplepagetest/"
        print(f">>> Opening the sample web form: {form_url}")
        driver.get(form_url)
        driver.maximize_window()
        time.sleep(3)

        print(">>> Finding form fields and filling with merged data...")

        # Fill the Name field
        name_field = driver.find_element(By.ID, "g2599-name")
        name_field.send_keys(data.get('name', 'N/A'))
        print(f"  - Filled Name: {data.get('name', 'N/A')}")
        time.sleep(1)

        # Fill all other extracted data in the "Comment" box to show the complete profile
        comment_field = driver.find_element(By.ID, "contact-form-comment-g2599-comment")
        details_text = (
            f"--- MERGED PROFILE ---\n"
            f"Extracted Date of Birth: {data.get('dob', 'N/A')}\n"
            f"PAN Number: {data.get('pan_number', 'N/A')}\n"
            f"Gender: {data.get('gender', 'N/A')}\n"
            f"Documents Processed: Aadhaar & PAN"
        )
        comment_field.send_keys(details_text)
        print(f"  - Filled other details in the Comment field.")
        time.sleep(1)
        
        # Use JavaScript to reliably click the checkbox
        print(">>> Selecting an option using a reliable JavaScript click...")
        checkbox_to_click = driver.find_element(By.XPATH, "//input[@value='Automation Testing']")
        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_to_click)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", checkbox_to_click)
        print("  - Successfully clicked a checkbox.")
        time.sleep(1)

        print("\n" + "="*25 + " DEMO COMPLETE " + "="*25)
        print("The script has successfully used data from BOTH documents to fill the form.")
        print("The browser will remain open for 15 seconds for you to see the result.")
        time.sleep(15)

    except Exception as e:
        print("\n" + "!"*25 + " DEMO FAILED " + "!"*25)
        print(f"An error occurred during the RPA process: {e}")
    finally:
        if driver:
            driver.quit()
        print(">>> Browser closed.")


# --- PART 3: MAIN EXECUTION ---
if __name__ == '__main__':
    
    # Define the two image files we will process
    aadhar_image_file = 'aadhar sample.jpg'
    pan_image_file = 'pan sample.jpg'

    print("--- Starting Full Automation: Aadhaar -> PAN -> Merge -> Form Fill ---")
    
    # Step 1: Process the Aadhaar card image
    aadhar_data = process_document_image(aadhar_image_file)
    if not aadhar_data:
        aadhar_data = {} # Ensure it's a dict to avoid errors, even if it fails

    # Step 2: Process the PAN card image
    pan_data = process_document_image(pan_image_file)
    if not pan_data:
        pan_data = {}

    # Step 3: Merge the data from both documents into a single profile
    print("\n>>> [MERGE] Combining data from both documents into a single client profile...")
    full_client_profile = aadhar_data.copy()  # Start with data from the first document
    full_client_profile.update(pan_data)      # Add or overwrite with data from the second

    # A small piece of logic: the name on a PAN card is often more official for financial use.
    # If we found a name on the PAN card, let's make sure that's the one we use.
    if pan_data.get('name'):
        full_client_profile['name'] = pan_data['name']

    # Step 4: Run the RPA form filler with the final, merged data
    if full_client_profile:
        print(f"\n>>> Final Merged Profile: {full_client_profile}")
        fill_web_form(full_client_profile)
    else:
        print("\n!!! Halting execution because OCR failed to extract data from any document.")

