# Intelligent Insurance Assistant Suite

This project is a suite of automation tools designed to streamline the workflow for an insurance agent. It leverages AI for audio transcription and summarization, OCR for document data extraction, RPA for automatic form filling, and a WhatsApp bot for client communication.

## Key Features

* **Audio Call Analysis (`audio_textsummary.py`):**
    * Upload a `.wav` audio recording of a client call.
    * The tool uses the Gemini API to transcribe the conversation.
    * It then analyzes the transcript to generate a structured JSON summary containing key details like client name, action items, and required documents.

* **Automated WhatsApp Reminders (`whatsapp_bot.py`):**
    * Takes the JSON output from the call analysis.
    * Uses the Twilio API to automatically send a WhatsApp message to the client, requesting the specific documents needed to proceed.

* **OCR & RPA for Form Filling (`ocr_automatic_formfilling.py`):**
    * Uses EasyOCR to read and extract data from images of client documents (e.g., Aadhaar and PAN cards).
    * Merges the extracted data into a single client profile.
    * Uses Selenium (RPA) to automatically fill out a web-based insurance application form with the merged client data, saving significant manual effort.

## Project Structure

The project is composed of three distinct but interconnected Python scripts:

1.  `audio_textsummary.py`: A Flask web application that transcribes and summarizes audio files. It runs on port `5001`.
2.  `whatsapp_bot.py`: A Flask web application that sends WhatsApp reminders based on JSON data. It runs on port `5002`.
3.  `ocr_automatic_formfilling.py`: A command-line script that performs OCR on document images and uses RPA to fill a web form.

## Technologies Used

* **Backend:** Python, Flask
* **AI & Machine Learning:**
    * Google Gemini API (for transcription and summarization)
    * EasyOCR (for Optical Character Recognition)
* **Automation:**
    * Selenium (for Robotic Process Automation / Web Form Filling)
    * `webdriver-manager`
* **Communication:** Twilio API for WhatsApp
* **Environment Management:** `python-dotenv`

## Setup and Installation

Follow these steps to get the project running on your local machine.

### 1. Clone the Repository

```bash
git clone [https://github.com/Taneeshaab/buildathon_ps2.git](https://github.com/Taneeshaab/buildathon_ps2.git)
cd buildathon_ps2
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage dependencies.

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

This project requires several Python packages. You can install them all using the command below.

```bash
pip install flask python-dotenv twilio requests werkzeug easyocr selenium webdriver-manager torch torchvision
```

*Note: `easyocr` requires PyTorch (`torch` and `torchvision`). The command above includes them.*

### 4. Set Up Environment Variables

This project uses API keys and credentials stored in a `.env` file.

Create a file named `.env` in the root of the project directory and add the following content. **Replace the placeholder values with your actual credentials.**

```env
# For audio_textsummary.py
GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"

# For whatsapp_bot.py
TWILIO_ACCOUNT_SID="YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN="YOUR_TWILIO_AUTH_TOKEN"
TWILIO_PHONE_NUMBER="whatsapp:+14155238886" # Your Twilio Sandbox Number
```

## Running the Applications

Each script runs independently. You will need to open three separate terminal windows (with the virtual environment activated in each) to run all components.

### 1. Run the Audio Summarizer

This will start a web server on `http://localhost:5001`.

```bash
python audio_textsummary.py
```

### 2. Run the WhatsApp Bot

This will start a web server on `http://localhost:5002`.

```bash
python whatsapp_bot.py
```

### 3. Run the OCR & RPA Script

This script runs directly from the command line. Make sure you have sample images named `aadhar sample.jpg` and `pan sample.jpg` in the same directory before running.

```bash
python ocr_automatic_formfilling.py
```

## Usage Flow

Here is a typical workflow using these tools:

1.  **Process a Client Call:**
    * Navigate to `http://localhost:5001` in your browser.
    * Upload the `.wav` recording of the client call.
    * The application will display the full transcript and a structured JSON summary. Copy the JSON summary.

2.  **Send a Document Reminder:**
    * Navigate to `http://localhost:5002`.
    * Paste the JSON summary into the "Summary JSON" text area.
    * Enter the client's WhatsApp-enabled phone number (e.g., `+919876543210`).
    * Click "Send Reminder". A WhatsApp message will be sent to the client requesting the necessary documents.

3.  **Automate Data Entry:**
    * Once you receive the document images from the client, save them as `aadhar sample.jpg` and `pan sample.jpg`.
    * Run the OCR script from your terminal: `python ocr_automatic_formfilling.py`.
    * Watch as the script automatically opens a Chrome browser, extracts data from the images, and fills out the sample web form.

---
