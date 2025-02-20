from flask import Flask, request
import requests
import json
import os

app = Flask(__name__)

# Facebook Credentials (Replace with your actual credentials)
VERIFY_TOKEN = "mango"  # A secret string you create
PAGE_ACCESS_TOKEN = "EAATxo65yWRsBO0ZCRQcXEocF99OEPlSf0Ehvrg5ahhCLZCRI7frcSxoaxgHoskkEoRTXak72pd499hJWgdF5BWZAqtc6j2G5T2bh3jGtJZBjovF7mF37c8nCU8jaqfbEviRLaVhdzaZCp57JfZBbKhp5oT3MkKGC2BDgiCPtZAgiMC40v0jWVu2tBr2SNsFDMltXAZDZD"  # Generated from Facebook Developer Console

# Route to handle Facebook's Webhook Verification
@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if token == VERIFY_TOKEN:
            return str(challenge)
        return "Invalid verification token", 403

    elif request.method == 'POST':
        data = request.get_json()
        if data.get('object') == 'page':
            for entry in data.get('entry', []):
                for message_event in entry.get('messaging', []):
                    sender_psid = message_event['sender']['id']
                    if 'message' in message_event:
                        received_message = message_event['message'].get('text', '')
                        if received_message:
                            response = get_chatgpt_response(received_message)
                            send_message(sender_psid, response)
        return "EVENT_RECEIVED", 200


# Route to handle incoming messages from Facebook
@app.route('/webhook', methods=['POST'])
def receive_message():
    """Handle messages sent to the bot."""
    data = request.get_json()
    
    if data['object'] == 'page':  # Ensuring it's from a Facebook Page
        for entry in data['entry']:
            for message_event in entry['messaging']:
                sender_psid = message_event['sender']['id']  # Get sender's ID
                
                if 'message' in message_event:  # Check if it's a message
                    received_message = message_event['message']['text']
                    print(f"Received Message: {received_message}")
                    
                    # Send response using ChatGPT
                    response = get_chatgpt_response(received_message)
                    send_message(sender_psid, response)

    return "EVENT_RECEIVED", 200

# Function to send a message back to the user
def send_message(psid, response):
    """Send response message to Facebook Messenger."""
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = json.dumps({
        "recipient": {"id": psid},
        "message": {"text": response}
    })
    requests.post(url, headers=headers, data=data)

# Function to get ChatGPT response
def get_chatgpt_response(message):
    """Query OpenAI's API for a response."""
    openai_api_key = "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"  # Replace with your OpenAI API key
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response_json = response.json()
    return response_json["choices"][0]["message"]["content"]

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

