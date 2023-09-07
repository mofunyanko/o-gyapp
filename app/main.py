import os
import random
from flask import Flask, request, make_response
from slack import WebClient
from slack_sdk.errors import SlackApiError

app = Flask(__name__)
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

# メッセージと対応するチャンネルIDの辞書
channels = {
  ":tag_ai:": "C05GMNGJ61H",
  ":tag_iot:": "C05GMLDHJTD",
  ":tag_os:": "C05GF6K8BCN",
  ":tag_アルゴリズム:": "C05GMLG8MJP",
  ":tag_データサイエンス:": "C05GMQ16U02",
  ":tag_ネットワークセキュリティ:": "C05GQ7U1FRA",
  ":tag_暗号:": "C05GQ801XJQ"
}

def send_dm_to_user(user_id, message):
  try:
    client.chat_postMessage(
      channel=user_id,
      text=message
    )
  except SlackApiError as e:
    print(f"Error: {e}")
    print(f"Response: {e.response}")

def get_random_member(channel_id):
  try:
    response = client.conversations_members(channel=channel_id)
    members = response["members"]
    return members
  except SlackApiError as e:
    print(f"Error: {e}")
    print(f"Response: {e.response}")
    return []

@app.route('/slack/events', methods=['POST'])
def slack_event():
  data = request.get_json()
  if "challenge" in data:
    return make_response(data["challenge"], 200, {"content_type": "application/json"})

  if "event" in data:
    event = data["event"]
    if event["type"] == "message":
      if 'subtype' in event and event['subtype'] == 'message_changed':
        event = event['message']

      if event["channel"].startswith('D') and 'bot_id' not in event:
        sender_id = event["user"]
        message = event["text"]
        selected_members = []

        for tag, channel_id in channels.items():
          if tag in message:
            members = get_random_member(channel_id)
            selected_members.append(set(members))

        common_members = set.intersection(*selected_members)
        if common_members:
          selected_member = random.choice(list(common_members))
          send_dm_to_user(selected_member, f"<@{sender_id}>さんとマッチングしました！以下が、<@{selected_member}>さんからの相談文です。\n{message}")
          send_dm_to_user(sender_id, f"<@{selected_member}>さんとマッチングしました！\n<@{selected_member}>さんには、あなたの相談文をお伝えいたします。")

  return make_response("Event received", 200,)

if __name__ == "__main__":
  app.run()
