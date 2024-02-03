# Conversational Creations: Building Chatbots with Dialogflow and Python Flask

## Requirements

- Google account
- Python installed on the system. (At least >= 3.11.x) [Download here](https://www.python.org/downloads/release/python-3115/)
- Ngrok [Download here](https://ngrok.com)

## Implement and design chatbot

- Create dialogflow agent [here](https://dialogflow.cloud.google.com/#/login).
- Create an agent, provide agent name. (Eg. Haku Agent). After creating an agent, it will also create a google cloud console project (takes much time).
- Create design using intent and entities

## Integrate front-end UI and back-end UI (Credit to [Engineering@ZenOfAI](https://medium.com/zenofai/creating-chatbot-using-python-flask-d6947d8ef805))

- Create a directory for the python flask. \

    ```command-line
   mkdir conversational-creations-dialogflow-flask && cd conversational-creations-dialogflow-flask && mkdir templates static && touch server.py static/{custom.js,style.css} templates/index.html requirements.txt .flaskenv .env

    ```

- Create virutal environment:

    ```command-line

    > python3 -m venv env
    > source env/bin/activate (macos or ubuntu)
    > env/Scripts/activate (windows)

    ```

- Install all necessary library

    ```command-line
    pip3 install Flask python-dotenv google-cloud-dialogflow  
    ```

- Configure flask environment

    ```command-line
    python3 server.py
    ```

- Provide this code in `server.py`:

    ```python
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
                print(session_context_params)
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


    ```

- Create a UI for our chatbot:

    **templates/index.html**

    ```html
    <!doctype html>
    <html lang="en">
    <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css">
        <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
        <title>PawCare Connect: Hassle-Free Vet Booking for Dogs</title>
    </head>
    <body>
        <div class="container h-100">
            <div class="row align-items-center h-100">
                <div class="col-md-8 col-sm-12 mx-auto">
                    <div class="h-100 justify-content-center">
                        <div class="chat-container" style="overflow: auto; max-height: 80vh">
                            <!-- chat messages -->
                            <div class="chat-message col-md-5 offset-md-7 bot-message">
                            Welcome to PawCare Connect. How can I help you?
                            </div>
                        </div>
                        <form id="target">
                        <input class="input" type="text" value="" placeholder="Enter message..." id="input_message"/>
                        <input type="submit" hidden>
                        </form>
                    </div>
                </div>
            </div>
        </div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.0/js/bootstrap.min.js"></script>
        <script src="{{ url_for('static', filename='custom.js')}}"></script>
    </body>
    </html>
    ```

    **static/style.css**

    ```css
    body,html {
    height: 100%;
    }

    .chat-container {
    /*margin: 0px;*/
    padding: 0px;
    width: 500px;
    /*margin: 35px 0px;*/
    margin-left: 15%;
    margin-right: 15%;
    }

    .chat-message {
    padding: 6px;
    border-radius: 6px;
    margin-bottom: 3px;
    }

    .bot-message {
    background: #22b538;
    max-width: 300px;
    color: white;
    margin-left: auto;
    }

    .human-message {
    background: dodgerblue;
    max-width: 300px;
    color: white;
    margin: 13px 1px;
    }

    .input {
    width: 500px;
    /*margin: 35px 0px;*/
    margin-left: 15%;
    margin-right: 15%;
    }
    ```

    **static/custom.js**

    ```js
    function submit_message(message) {
        $.post( "/send_message", {message: message}, handle_response);

        function handle_response(data) {
          // append the bot repsonse to the div
          $('.chat-container').append(`
                <div class="chat-message col-md-5 offset-md-7 bot-message">
                    ${data.message}
                </div>
          `)
          // remove the loading indicator
          $( "#loading" ).remove();
        }
    }

    $('#target').on('submit', function(e){
        e.preventDefault();
        const input_message = $('#input_message').val()
        // return if the user does not enter any text
        if (!input_message) {
          return
        }

        $('.chat-container').append(`
            <div class="chat-message col-md-5 human-message">
                ${input_message}
            </div>
        `)

        // loading 
        $('.chat-container').append(`
            <div class="chat-message text-center col-md-2 offset-md-10 bot-message" id="loading">
                <b>...</b>
            </div>
        `)

        // clear the text input 
        $('#input_message').val('')

        // send the message
        submit_message(input_message)
    });
    ```

- `flask run`

- Setup [google cloud console](https://console.cloud.google.com/home/dashboard)
  - Copy project Id to env.

    ```env
    DIALOGFLOW_PROJECT_ID= <your project-id>
    ```

  - Go to APIs & Services > Credentials
  - Create credentials > service account
  - Provide necessary details. And done
  - Open that service account > keys > Add keys > Create new Key > JSON Type
  - After downloading json file. Put it in the base folder of the project and provide to env file.

    ```env
    GOOGLE_APPLICATION_CREDENTIALS=<your JSON file>
    ```

  - final `.env` file:

    ```env
    DIALOGFLOW_PROJECT_ID=haku-gfha
    GOOGLE_APPLICATION_CREDENTIALS=<your JSON file>
    ```

  - Re run the app

## Integrate Server webhook

- Setup [ngork](https://gist.github.com/wosephjeber/aa174fb851dfe87e644e):

    ```command-line
    ngrok http 5000
    ```

- Extract url generated by ngrok

- Go to dialogflow > fulfillment > enable webhook > paste the url

- Enable intents that needs to triggers webhook
