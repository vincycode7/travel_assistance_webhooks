# /index.py

from flask import Flask, request, jsonify, render_template
import os

from werkzeug.wrappers import response
import dialogflow
import requests
import json
import pusher
import google.protobuf  as pf

app = Flask(__name__)

# First page to display to user of the site
@app.route('/')
def index():
    return render_template('index.html')

# Used for the webhook to connect to dialogflow
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)
    # print(data)
    #Sure, I will book a flight ticket to #book_a_flight.geo-city, #book_a_flight.geo-country for $date-time.
    #OK, I will book a flight ticket to #book_a_flight.geo-city, #book_a_flight.geo-country for #book_a_flight.date-time.
    
    if data['queryResult']['intent']['displayName'] == 'book_a_flight_ticket - yes':
        geo_city = data['queryResult']['outputContexts'][0]['parameters']['geo-city']
        geo_country = data['queryResult']['outputContexts'][0]['parameters']['geo-country']
        date_time = data['queryResult']['outputContexts'][0]['parameters']['date-time']['date_time']
        
        reply = {
            "fulfillmentText": "OK, I will book a flight ticket to {}, {} for {}.".format(geo_city, geo_country, date_time),
        }
        reply2 = {
            "fulfillmentMessages": [
                    {
                        "text": {
                        "text": [
                            "OK."
                        ]
                        }
                    },
                    {
                        "text": {
                        "text": [
                            "I will book a flight ticket to {}, {} for {}.".format(geo_city, geo_country, date_time)
                        ]
                        }
                    }
                            ]
        }
        return jsonify(reply2)

    #OK, flight ticket to #book_a_flight.geo-city, #book_a_flight.geo-country for #book_a_flight.date-time. has not been booked but added to cart, you can type "book current flight ticket" to book the most recent flight ticket in cart.
    elif data['queryResult']['intent']['displayName'] == 'book_a_flight_ticket - no':
        geo_city = data['queryResult']['outputContexts'][0]['parameters']['geo-city']
        geo_country = data['queryResult']['outputContexts'][0]['parameters']['geo-country']
        date_time = data['queryResult']['outputContexts'][0]['parameters']['date-time']['date_time']
        reply = {
            "fulfillmentText": "OK, flight ticket to {}, {} for {}. has not been booked but added to cart, you can type 'book current flight ticket' to book the most recent flight ticket in cart.".format(geo_city, geo_country, date_time),
        }
        reply2 = {
            "fulfillmentMessages": [
                    {
                        "text": {
                        "text": [
                            "OK."
                        ]
                        }
                    },
                    {
                        "text": {
                        "text": [
                            "Flight ticket to {}, {} for {}. has not been booked but added to cart, you can type 'book current flight ticket' to book the most recent flight ticket in cart.".format(geo_city, geo_country, date_time)
                        ]
                        }
                    }
                            ]
        }
        return jsonify(reply2)

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)
        return json.loads(pf.json_format.MessageToJson(response, including_default_value_fields=False))

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    response = detect_intent_texts(project_id, "unique", message, 'en')
    return jsonify(response)

# run Flask
if __name__ == "__main__":
    app.run(debug=True, port=5000)