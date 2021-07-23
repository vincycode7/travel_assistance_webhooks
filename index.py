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
    if data['queryResult']['queryText'] == 'yes':
        reply = {
            "fulfillmentText": "Ok. Tickets booked successfully.",
        }
        return jsonify(reply)

    elif data['queryResult']['queryText'] == 'no':
        reply = {
            "fulfillmentText": "Ok. Booking cancelled.",
        }
        return jsonify(reply)

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)
                # for i in range(0,len(response.query_result.fulfillment_messages)):
                # print(response.query_result.fulfillment_messages[i].text)
        # print({"response_id":response.response_id, "query_result.":response.query_result})
        # return {"response_id":response.response_id, "query_result.":response.query_result}
        return json.loads(pf.json_format.MessageToJson(response, including_default_value_fields=False))

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    response = detect_intent_texts(project_id, "unique", message, 'en')
    # print(response, type(response))
    # print(dict(fulfillment_message))
    # text_msgs = []
    # for i in range(0,len(fulfillment_message)):
    #     text_msgs.append(fulfillment_message[i].text["text"])
    #     print(fulfillment_message[i].text)
    # response_msg = { "message":  fulfillment_message }
    # return fulfillment_message
    return jsonify(response)
    # return {"message":"Welcome to Travel portal. How can I help you?"}

# run Flask
if __name__ == "__main__":
    app.run(debug=True)