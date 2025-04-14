import json
import time
import glob
from telethon import TelegramClient
from telethon.tl.types import PeerChannel
from datetime import datetime
import asyncio
import html
import os

input_folder: str = "backup_will_be_inside_me"


async def main():
    with open(os.path.join(input_folder, "dump.json"), "r") as file:
        raw = file.read()
        if raw.endswith(","):
            raw = raw[:-1]
        fixed = "[" + raw + "]"
        content = json.loads(fixed)
        content = sorted(content, key=lambda x: x["date"])

        api_id = "API_ID"
        api_hash = "API_HASH"
        chat_id = "GROUP_CHAT_ID"

        client = TelegramClient("session_name", api_id, api_hash)
        await client.start()

        group = await client.get_entity(PeerChannel(int(chat_id)))

        for msg in content:
            if msg["_"] != "Message":
                continue
            peer_id = msg["peer_id"].get("channel_id", None)
            reply_to_msg_id = msg["reply_to"].get("reply_to_msg_id", None)
            reply_to_top_id = msg["reply_to"].get("reply_to_top_id", None)
            reply_to = "/".join(
                str(s).strip()
                for s in [peer_id, reply_to_top_id, reply_to_msg_id]
                if s and str(s).strip())
            message_id = msg["id"]
            from_id = msg["from_id"].get("user_id", None)
            message = msg.get("message", "")
            has_media = msg.get("media", None) is not None
            has_message = message != ""
            date = datetime.fromisoformat(msg["date"]).strftime("%Y %b %d, %H:%M")

            print(
                f"{message_id} {message}, {date}, has_media: {has_media}, from_id: {from_id}, reply_to: {reply_to}"
            )

            if msg["reply_to"]["quote"]:
                quote_text = msg["reply_to"].get("quote_text", None)
                if quote_text is not None:
                    quote_text = html.escape(quote_text)
                    if has_message:
                        message = f"<pre>❝ {quote_text} ❞</pre>\n\n{message}"
                    else:
                        message = f"<pre>❝ {quote_text} ❞</pre>"
                    has_message = True

            if has_message:
                message = str(date) + "\n\n" + str(message)
            else:
                message = str(date)

            if from_id is not None:
                try:
                    user = await client.get_entity(from_id)
                    full_name = " ".join(
                        filter(None, [user.first_name, user.last_name]))
                    message = f"{full_name} (@{user.username}) - http://t.me/c/{reply_to} - {message}"
                except Exception as e:
                    print(f"Error fetching user: {str(e)}")
                    message = f"Unknown User - http://t.me/c/{reply_to} - {message}"
            else:
                message = f"Unknown User - http://t.me/c/{reply_to} - {message}"

            did_send_media_msg = False

            if has_media:
                file_names = glob.glob(f"{input_folder}/{message_id}.*")
                for file_name in file_names:
                    print(f"Sending Media: {file_name}")
                    try:
                        await client.send_file(entity=group,
                                               file=file_name,
                                               caption=message,
                                               silent=True)
                        did_send_media_msg = True
                    except Exception as e:
                        print(f"Error sending media {file_name}: {str(e)}")

            if has_message and not did_send_media_msg:
                print(f"Sending Message: {message}")
                try:
                    await client.send_message(entity=group,
                                              message=message,
                                              silent=True,
                                              parse_mode="html")
                except Exception as e:
                    print(f"Error sending message: {str(e)}")

            time.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
