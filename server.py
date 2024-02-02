import os
import secrets
from datetime import datetime

import google.cloud.dialogflow_v2 as dialogflow
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


random_string = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10))


@app.route('/')
def index():
    return render_template('index.html')


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)
        return response.query_result.fulfillment_text

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    fulfillment_text = detect_intent_texts(project_id, random_string, message, 'en')
    response_text = { "message":  fulfillment_text }
    return jsonify(response_text)


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True)

    return jsonify(format_data(data)) 


def format_data(data):
    current_intent = data.get('queryResult').get('intent').get('displayName')
    outputContext=data.get('queryResult').get('outputContexts')
    intent_to_match = 'conversation.question3'
    intent_finish ='conversation.question3 - yes'
    outputContextVariableHolder = 'session_variable'
    users_info=''

    for i in range(len(outputContext)-1, -1, -1):
        if outputContext[i]['name'].split('/')[-1]==outputContextVariableHolder:
            session_context_params=outputContext[i].get('parameters')
            pet_name = session_context_params.get('DogName')
            date = datetime.strptime(session_context_params.get('date-time').get('date_time'),'%Y-%m-%dT%H:%M:%S%z') 
            formatted_datetime = date.strftime("%B %d, %Y %I:%M%p")
            age = session_context_params.get('age').get('amount')
            breed = session_context_params.get('DogsBreed')
            users_info = f'Appointment Date: {formatted_datetime}<br>Dog\'s Name: {pet_name}<br>Dog\'s Age: {age}<br>Dog\'s Breed: {breed}'

        
    if intent_to_match == current_intent:
        reply = {
            "fulfillmentText": f"Okay, just to review, here's your data. Is this correct?<br><br>{users_info}"
        }
        return reply

    elif current_intent == intent_finish:
        # Perform saving data from user to database
        reply = {
            "fulfillmentText": "Booked appointment, thank you!",
        }
        return reply


if __name__ == "__main__":
    app.run(debug=True)