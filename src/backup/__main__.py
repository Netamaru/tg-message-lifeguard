"""
This module handles the export of deleted Telegram messages and media using Telethon.
It supports various export models based on user inputs,
including exporting all deleted messages, media only, or text-only messages.
"""

import os
import json
import asyncio
from telethon import TelegramClient
from telethon.tl.types import PeerChannel
from telethon.errors import RPCError

# Requesting user credentials
api_id: int = int(input("Enter your api_id: "))
api_hash: str = input("Enter your api_hash: ")

session_name: str = "session_name"
session_file: str = f"{session_name}.session"

# Output folder will be set after getting the group ID

# Remove session file if it exists
if os.path.exists(session_file):
    os.remove(session_file)
    print(f"Existing session file removed: {session_file}")

# Initialize Telegram client
client: TelegramClient = TelegramClient(session_name, api_id, api_hash)


async def export_messages(
    target_group_id: int,
    mode: int,
    min_id: int = 0,
    max_id: int = 0,
    filter_user_id: int = 0,
) -> None:
    """
    Exports messages from a Telegram group or channel.

    :param target_group_id: ID of the Telegram group or channel.
    :param mode: Export mode (1 - all, 2 - media only, 3 - text only).
    :param min_id: Minimum message ID to export.
    :param max_id: Maximum message ID to export.
    :param filter_user_id: User ID to filter by (who deleted the message). 0 = no filter.
    """
    group: PeerChannel = await client.get_entity(PeerChannel(target_group_id))
    # Define the dump file path
    dump_file = os.path.join(output_folder, "dump.json")
    # Check if the file exists to append data instead of overwriting
    file_mode: str = "a" if os.path.exists(dump_file) else "w"

    # Initialize JSON structure
    messages = []
    if file_mode == "a" and os.path.exists(dump_file):
        # Load existing messages if appending
        try:
            with open(dump_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    # Handle the old malformed format
                    if content.startswith('['):
                        messages = json.loads(content)
                    else:
                        # Convert old comma-separated format
                        if content.endswith(','):
                            content = content[:-1]
                        messages = json.loads(f"[{content}]")
        except (json.JSONDecodeError, FileNotFoundError):
            messages = []
    
    c: int = 0  # Counter for text messages
    m: int = 0  # Counter for media messages

    limit_per_request: int = 100  # Number of events per request

    try:
        while True:
            events = [
                event
                async for event in client.iter_admin_log(
                    group,
                    min_id=min_id or 0,
                    max_id=max_id or 0,
                    limit=limit_per_request,
                    delete=True,  # Interested only in deleted messages
                )
            ]

            if not events:
                print("Loading complete, no new messages.")
                break

            # Filter and process messages
            for event in events:
                # Check if message was deleted and meets ID criteria
                if event.deleted_message and event.old.id >= min_id:
                    # Apply user filter if specified (0 means no filter)
                    if filter_user_id != 0 and event.user_id != filter_user_id:
                        continue
                    if mode == 1:  # Export all text and media
                        message_json = json.loads(event.old.to_json())
                        messages.append(message_json)
                        c += 1
                        print(
                            f"Saved message {c} (ID: {event.old.id}, Date: {event.old.date}, Deleted by: {event.user_id})"
                        )

                        if event.old.media:
                            m += 1
                            await client.download_media(
                                event.old.media,
                                os.path.join(output_folder, str(event.old.id)),
                            )
                            print(
                                f"Saved media file {m} (ID: {event.old.id}, Date: {event.old.date}, Deleted by: {event.user_id})"
                            )

                    elif mode == 2 and event.old.media:  # Export media only
                        m += 1
                        await client.download_media(
                            event.old.media,
                            os.path.join(output_folder, str(event.old.id)),
                        )
                        print(
                            f"Saved media file {m} (ID: {event.old.id}, Date: {event.old.date}, Deleted by: {event.user_id})"
                        )

                    elif mode == 3 and not event.old.media:  # Export text only
                        message_json = json.loads(event.old.to_json())
                        messages.append(message_json)
                        c += 1
                        print(
                            f"Saved text message {c} (ID: {event.old.id}, Date: {event.old.date}, Deleted by: {event.user_id})"
                        )

                    await asyncio.sleep(0.1)  # Short pause to avoid flooding API

            max_id = (
                events[-1].id - 1
            )  # Exclude the last received event from the next request

            if max_id < min_id:
                print("Reached the lower message ID limit.")
                break

    except RPCError as e:
        print(f"An error occurred: {e}")
    
    # Save messages as proper JSON array
    with open(dump_file, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(messages)} messages to {dump_file}")


# Request additional details from the user
export_mode: int = int(
    input("Enter export mode (1 - all, 2 - media only, 3 - text only): ")
)
min_message_id: int = int(
    input("Enter the minimum message ID (0 to start from the first): ")
)
max_message_id: int = int(input("Enter the maximum message ID (0 to retrieve all): "))
group_id: int = int(input("Enter the group or channel ID: "))
filter_user_id: int = int(input("Enter user ID to filter by who deleted messages (0 for no filter): "))

# Create output folder based on group ID (remove leading minus if present)
folder_name = str(abs(group_id))  # abs() removes the minus sign
output_folder: str = os.path.join("backup", folder_name)
os.makedirs(output_folder, exist_ok=True)  # Create the folder if it doesn't exist
print(f"Backup will be saved to folder: {output_folder}")
if filter_user_id != 0:
    print(f"Filtering messages deleted by user ID: {filter_user_id}")
else:
    print("No user filter applied - showing messages deleted by anyone")


async def main() -> None:
    """
    Main function to start the export process.
    """
    await client.start()
    await export_messages(
        group_id, export_mode, min_id=min_message_id, max_id=max_message_id, filter_user_id=filter_user_id
    )


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
