import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask , request , Response
from slackeventsapi import SlackEventAdapter

#Accessing our environment variables
env_path = Path('.')/'.env'
load_dotenv(dotenv_path=env_path)

#Initiating the Flask webserver should be runnig on http://127.0.0.1:5000
app = Flask(__name__)

#Configuring the event adapter
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events',app)

#Configuring the Slack client that we will use to post message
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

#Extracting the Bot Id using client.api_call
BOT_ID = client.api_call("auth.test")['user_id']
#print(client.api_call("auth.test"))

#Since we are not using a database yet to store the count, we are then using a dictionary. 
message_counts = {}

#example on how to post a message
#client.chat_postMessage(channel="C061QN2V6UA",text="Hello from python app")

@slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event',{})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    if BOT_ID != user_id:
        if user_id in message_counts:
            message_counts[user_id] += 1
        else:
            message_counts[user_id] = 1


@app.route('/message-count', methods=['POST'])
def message_count():
    data = request.form
    print(data)
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    message_count = message_counts.get(user_id,0)
    client.chat_postMessage(channel=channel_id, text=f"Message: {message_count}")
    return Response(), 200


if __name__== "__main__":
    app.run(debug=True)