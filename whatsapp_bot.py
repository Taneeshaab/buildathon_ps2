import os
import json
from flask import Flask, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
from twilio.rest import Client

# This line loads your secret keys from the .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'this_is_for_testing_whatsapp'

def send_whatsapp_reminder(summary_data, client_phone_number):
    """Takes the JSON data and sends a WhatsApp message via Twilio."""
    print(">>> [WHATSAPP] Checking if a reminder is needed based on the JSON...")

    if "requiredDocuments" in summary_data and summary_data["requiredDocuments"]:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not all([account_sid, auth_token, twilio_number]):
            flash("Twilio credentials are missing or incomplete in your .env file.", "error")
            return

        client_name = summary_data.get("clientName", "there")
        documents_list = ", ".join(summary_data["requiredDocuments"])
        
        message_body = (
            f"Hi {client_name}, thank you for your call. "
            f"To proceed with your insurance quote, please reply here with a clear picture of your: {documents_list}."
        )

        try:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                from_=twilio_number,
                body=message_body,
                to=f'whatsapp:{client_phone_number}'
            )
            print(f">>> [WHATSAPP] Success! Message SID: {message.sid}")
            flash(f"Successfully sent WhatsApp message to {client_phone_number}!", "success")
        except Exception as e:
            print(f"!!! [WHATSAPP] ERROR: {e}")
            flash(f"Twilio API Error: {e}", "error")
    else:
        print(">>> [WHATSAPP] No required documents found. No message sent.")
        flash("No required documents found in the JSON. No message was sent.", "info")

@app.route('/', methods=['GET'])
def index():
    """Displays the webpage."""
    return render_template('index_whatsapp.html')

@app.route('/send_reminder', methods=['POST'])
def send_reminder():
    """Handles the button click to send the message."""
    summary_json_string = request.form.get('summary_json')
    your_phone_number = request.form.get('phone_number')

    try:
        summary_data = json.loads(summary_json_string)
    except json.JSONDecodeError:
        flash("Invalid JSON format. Please check for typos.", "error")
        return redirect(url_for('index'))

    send_whatsapp_reminder(summary_data, your_phone_number)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Using port 5002 to avoid conflicts
    app.run(host='0.0.0.0', port=5002, debug=True)

