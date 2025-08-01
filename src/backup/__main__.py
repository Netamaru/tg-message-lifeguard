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

# Output folder will be set dynamically for each thread
output_folder: str = ""

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
    message_thread_id: int = 0,
) -> None:
    """
    Exports messages from a Telegram group or channel.

    :param target_group_id: ID of the Telegram group or channel.
    :param mode: Export mode (1 - all, 2 - media only, 3 - text only).
    :param min_id: Minimum message ID to export.
    :param max_id: Maximum message ID to export.
    :param filter_user_id: User ID to filter by (who deleted the message). 0 = no filter.
    :param message_thread_id: Thread ID to filter by (topic/thread). 0 = no filter.
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
                    
                    # Apply thread filter if specified (0 means no filter)
                    if message_thread_id != 0:
                        # Check for forum-style topics first
                        message_reply_to = getattr(event.old, 'reply_to', None)
                        
                        if message_reply_to:
                            # Check for forum topic ID (reply_to_top_id is the actual topic ID)
                            forum_topic_id = getattr(message_reply_to, 'reply_to_top_id', None)
                            reply_msg_id = getattr(message_reply_to, 'reply_to_msg_id', None)
                            is_forum_topic = getattr(message_reply_to, 'forum_topic', False)
                            
                            if is_forum_topic and forum_topic_id is not None:
                                # This is a forum topic message
                                if forum_topic_id != message_thread_id:
                                    continue
                            elif reply_msg_id is not None:
                                # This is a regular reply thread
                                if reply_msg_id != message_thread_id:
                                    continue
                            else:
                                continue
                        else:
                            # If no reply_to, check if the message itself is the thread starter
                            if event.old.id != message_thread_id:
                                continue
                    if mode == 1:  # Export all text and media
                        message_json = json.loads(event.old.to_json())
                        
                        # Initialize media file info
                        media_file_info = None
                        
                        if event.old.media:
                            # Check if message is part of a media group (album)
                            grouped_id = getattr(event.old, 'grouped_id', None)
                            if grouped_id:
                                # Use grouped_id for media group folder
                                message_media_folder = os.path.join(output_folder, f"album_{grouped_id}")
                                folder_info = f"album {grouped_id}"
                            else:
                                # Individual message folder
                                message_media_folder = os.path.join(output_folder, f"msg_{event.old.id}")
                                folder_info = f"message {event.old.id}"
                            
                            os.makedirs(message_media_folder, exist_ok=True)
                            
                            try:
                                # Download media with automatic filename generation
                                downloaded_path = await client.download_media(
                                    event.old.media,
                                    message_media_folder
                                )
                                if downloaded_path:
                                    m += 1
                                    # Convert absolute path to relative path for portability
                                    relative_path = os.path.relpath(downloaded_path, output_folder)
                                    media_file_info = {
                                        "local_path": relative_path,
                                        "absolute_path": downloaded_path,
                                        "filename": os.path.basename(downloaded_path),
                                        "folder_type": "album" if grouped_id else "message",
                                        "folder_id": grouped_id if grouped_id else event.old.id
                                    }
                                    print(
                                        f"Saved media file {m} from {folder_info} (ID: {event.old.id}, Path: {downloaded_path}, Date: {event.old.date}, Deleted by: {event.user_id})"
                                    )
                                else:
                                    print(f"Failed to download media for message {event.old.id}")
                            except Exception as e:
                                print(f"Error downloading media for message {event.old.id}: {e}")
                        
                        # Add media file info to message JSON
                        if media_file_info:
                            message_json["local_media_file"] = media_file_info
                        
                        messages.append(message_json)
                        c += 1
                        print(
                            f"Saved message {c} (ID: {event.old.id}, Date: {event.old.date}, Deleted by: {event.user_id})"
                        )

                    elif mode == 2 and event.old.media:  # Export media only
                        # Check if message is part of a media group (album)
                        grouped_id = getattr(event.old, 'grouped_id', None)
                        if grouped_id:
                            # Use grouped_id for media group folder
                            message_media_folder = os.path.join(output_folder, f"album_{grouped_id}")
                            folder_info = f"album {grouped_id}"
                        else:
                            # Individual message folder
                            message_media_folder = os.path.join(output_folder, f"msg_{event.old.id}")
                            folder_info = f"message {event.old.id}"
                        
                        os.makedirs(message_media_folder, exist_ok=True)
                        
                        try:
                            # Download media with automatic filename generation
                            downloaded_path = await client.download_media(
                                event.old.media,
                                message_media_folder
                            )
                            if downloaded_path:
                                m += 1
                                print(
                                    f"Saved media file {m} from {folder_info} (ID: {event.old.id}, Path: {downloaded_path}, Date: {event.old.date}, Deleted by: {event.user_id})"
                                )
                            else:
                                print(f"Failed to download media for message {event.old.id}")
                        except Exception as e:
                            print(f"Error downloading media for message {event.old.id}: {e}")

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

# Support for multiple thread IDs
print("\nThread Options:")
print("  0 = Backup ALL messages (no thread filter)")
print("  19 = Single thread ID")
print("  [19,20,23] = Multiple threads")
thread_input = input("Enter thread/topic ID(s): ").strip()
if thread_input == "0":
    message_thread_ids = [0]
elif thread_input.startswith("[") and thread_input.endswith("]"):
    # Parse array format like [19, 20, 23]
    thread_str = thread_input[1:-1]  # Remove brackets
    message_thread_ids = [int(x.strip()) for x in thread_str.split(",") if x.strip()]
    print(f"Processing {len(message_thread_ids)} threads: {message_thread_ids}")
else:
    # Single thread ID
    message_thread_ids = [int(thread_input)]

# Create base output folder based on group ID (remove leading minus if present)
folder_name = str(abs(group_id))  # abs() removes the minus sign
base_output_folder: str = os.path.join("backup", folder_name)

# Create base folder
os.makedirs(base_output_folder, exist_ok=True)

if filter_user_id != 0:
    print(f"Filtering messages deleted by user ID: {filter_user_id}")
else:
    print("No user filter applied - showing messages deleted by anyone")

if message_thread_ids == [0]:
    print("No thread filter applied - showing messages from all threads/topics")
else:
    print(f"Will process {len(message_thread_ids)} thread(s): {message_thread_ids}")


async def main() -> None:
    """
    Main function to start the export process.
    """
    await client.start()
    
    # Process each thread ID
    for i, thread_id in enumerate(message_thread_ids, 1):
        if len(message_thread_ids) > 1:
            print(f"\n{'='*50}")
            print(f"Processing thread {i}/{len(message_thread_ids)}: {thread_id}")
            print(f"{'='*50}")
        
        # Set output folder for this thread
        if thread_id != 0:
            current_output_folder = os.path.join(base_output_folder, f"thread_{thread_id}")
        else:
            current_output_folder = base_output_folder
        
        # Create thread-specific folder
        os.makedirs(current_output_folder, exist_ok=True)
        print(f"Backup will be saved to folder: {current_output_folder}")
        
        # Temporarily set global output_folder for export_messages function
        global output_folder
        output_folder = current_output_folder
        
        await export_messages(
            group_id, export_mode, min_id=min_message_id, max_id=max_message_id, 
            filter_user_id=filter_user_id, message_thread_id=thread_id
        )
        
        if len(message_thread_ids) > 1:
            print(f"Completed thread {thread_id}")
    
    if len(message_thread_ids) > 1:
        print(f"\n{'='*50}")
        print(f"All {len(message_thread_ids)} threads processed successfully!")
        print(f"{'='*50}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
