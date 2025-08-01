# [Telegram Backup Tool] TML Documentation

## Overview
This tool allows you to recover deleted messages and media from Telegram channels and groups. It provides features to export all messages, only media files, or only text messages within a specific ID range.

### ✨ Latest Features
- **🗂️ Organized Backup Structure:** Files are now automatically organized in `backup/{channel_id}/` folders
- **👤 User-Based Filtering:** Filter messages by who deleted them (admin, user, or specific person)
- **🧵 Thread/Topic Filtering:** Filter messages by specific thread or forum topic ID
- **📊 Enhanced Logging:** See who deleted each message in the output
- **🎯 Better Organization:** Each channel/group gets its own dedicated backup folder

---

## 📦 Setting Up the Environment

### Installing and Configuring a Virtual Environment (venv)
`venv` is an isolated environment for Python projects. It allows you to install dependencies without affecting the global Python installation on your device.

This is especially important when working with multiple projects that require different library versions.

### 💻 How to Create a Virtual Environment

Open the terminal (bash/zsh), which can be done directly inside VS Code.

#### Creating a virtual environment:
```bash
$ python3 -m venv venv
```
Here, `venv` is the directory name that will contain your virtual environment. You can choose any name for this folder.

#### Activating the virtual environment:
**MacOS/Linux:**
```bash
$ source venv/bin/activate
```
**Windows:**
```bash
$ .\venv\Scripts\activate
```

#### Deactivating the virtual environment:
```bash
$ deactivate
```

### 📂 Installing Project Dependencies
Ensure the virtual environment is activated before installing dependencies:
```bash
$ pip3 install -r requirements.txt
```
Once dependencies are installed, you can run the Python scripts.

---

## 🛠️ Using the Backup Module to Recover Data

### Prerequisites
Before starting the recovery process, you need to obtain the following values:
- `api_id`
- `api_hash`
- `group_chat_id`

### 🔑 Steps to Obtain `api_id` and `api_hash`
1. Go to the [Telegram API website](https://my.telegram.org/).
2. Log in with your phone number in the format `+XXXXXXXXXXXX`.
3. Confirm authentication with the 2FA code.
4. Click on **API development tools**.
5. Your `api_id` and `api_hash` will be displayed on the page.

### 🏷️ Obtaining `group_chat_id` or `channel_id` by following the [instructions](https://gist.github.com/nafiesl/4ad622f344cd1dc3bb1ecbe468ff9f8a#get-chat-id-for-a-group-chat).
Follow the provided instructions to obtain these values. Store them securely for the recovery process.

### 👤 Getting User IDs (Optional - for filtering)
To filter by who deleted messages, you'll need user IDs:
- **Your own ID:** Use [@userinfobot](https://t.me/userinfobot) - send any message to get your user ID
- **Other users:** Forward a message from them to [@userinfobot](https://t.me/userinfobot)
- **Admin/Bot IDs:** Check group member lists or use Telegram's developer tools
- **Skip filtering:** Enter `0` to backup all deleted messages regardless of who deleted them

### 🧵 Getting Thread/Topic IDs (Optional - for filtering)
To filter by specific threads or topics, you'll need thread IDs:
- **Forum Topics:** Right-click topic → "Copy Link" → Extract ID from URL (e.g., `https://t.me/c/1234567890/123` → thread ID is `123`)
- **Reply Threads:** Use the message ID of the original message that started the thread
- **Regular Messages:** Any message ID can be used to filter messages in that specific thread
- **Skip filtering:** Enter `0` to backup messages from all threads and topics

---

## 🚀 Starting the Recovery Process

Run the backup module with the following command:
```bash
$ python3 -m src.backup
```

The script will prompt you to enter:

- **api_id:** Enter your previously obtained `api_id`.
- **api_hash:** Enter your previously obtained `api_hash`.
- **export_mode:** Choose from 1 (all), 2 (media only), or 3 (text only).
- **min_message_id:** Minimum message ID to start from (0 for first message).
- **max_message_id:** Maximum message ID to retrieve (0 for all messages).
- **group_id:** The channel or group ID to backup from.
- **filter_user_id:** User ID to filter by who deleted messages (0 for no filter).
- **message_thread_id:** Thread/topic ID to filter by (0 for no filter).

### 🔐 Authorization Step

You will be prompted with the following message:
```bash
$ Please enter your phone (or bot token):
```

#### Authentication Methods:
1. **Logging in via personal account (Recommended):**
   - Enter your phone number.
   - Enter your password.
   - Input the 2FA code received from Telegram Service Notifications (TSN).

2. **Using a bot token (Not recommended due to restrictions):**
   - Create a bot via [@BotFather](https://t.me/BotFather).
   - Obtain the API Token.
   - Enter it in the terminal.

⚠️ **Important:** Bot authentication may result in the following error:
```bash
telethon.errors.rpcerrorlist.BotMethodInvalidError: The API access for bot users is restricted.
```
Thus, user account authorization is required.

---

## 📊 Export Modes
You can choose from the following export modes:
- **Mode 1:** Export **all messages and media**.
- **Mode 2:** Export **only media files**.
- **Mode 3:** Export **only text messages**.

### 🔢 Setting Message ID Ranges
- **Minimum message ID:** `0` (start from the very first message).
- **Maximum message ID:** `0` (retrieve all messages).

**Example:**
```bash
min_message_id = 23456
max_message_id = 25673
```
This will recover messages within the specified range.

### 📌 Group or Channel ID
Enter the `group_chat_id` obtained earlier. The ID typically starts with a minus sign (e.g., `-1001234567890`).

### 👤 User Filtering
You can now filter messages by who deleted them:
- **Enter a specific user ID:** Only backup messages deleted by that user.
- **Enter `0`:** No filter - backup messages deleted by anyone (default behavior).

This is useful for:
- Tracking admin deletions vs user self-deletions
- Focusing on messages deleted by specific moderators
- Analyzing deletion patterns by user

### 🧵 Thread/Topic Filtering (New Feature)
You can now filter messages by specific threads or forum topics:
- **Enter a specific thread/topic ID:** Only backup messages from that thread/topic.
- **Enter `0`:** No filter - backup messages from all threads/topics (default behavior).

This works with:
- **Forum Topics:** Filter by forum topic ID in Telegram groups with topics enabled
- **Reply Threads:** Filter by the original message ID that started a reply thread
- **Regular Messages:** Use the message ID itself for messages that aren't part of threads

**How to find thread/topic IDs:**
- **Forum topics:** Right-click on topic title → Copy message link → Extract the topic ID from URL
- **Reply threads:** Use the message ID of the first message in the thread
- **Message inspection:** Use developer tools or Telegram clients that show message details

---

## 📥 Output and Recovery Management

### 📁 Folder Structure
The recovered media files and `dump.json` will be automatically organized in the following structure:

**Without thread filtering:**
```
backup/
└── {channel_id}/
    ├── dump.json
    ├── {message_id}.jpg
    ├── {message_id}.mp4
    └── ...
```

**With thread filtering:**
```
backup/
└── {channel_id}/
    └── thread_{thread_id}/
        ├── dump.json
        ├── {message_id}.jpg
        ├── {message_id}.mp4
        └── ...
```

**Examples:** 
- Channel ID `-1001234567890` (no thread filter): `backup/1001234567890/`
- Channel ID `-1001234567890` with thread ID `123`: `backup/1001234567890/thread_123/`

### 📄 Output Details
- **Media files:** Named after their corresponding message ID (e.g., `12345.jpg`)
- **Text messages:** Stored in `dump.json` with full message metadata
- **Deletion info:** Each output line now shows who deleted the message

**Sample output:**
```
Saved message 1 (ID: 12345, Date: 2024-01-15, Deleted by: 987654321)
Saved media file 1 (ID: 12346, Date: 2024-01-15, Deleted by: 123456789)
```

### 🔄 Resuming Interrupted Recovery
If the script is interrupted, use the ID of the last exported message to resume:
1. Restart the script
2. Enter the same channel ID and settings
3. Set `min_message_id` to the last processed message ID
4. The script will continue from that point, saving to the same organized folder

---

## 📺 Monitoring the Process
Once the script is running, monitor the console output to track progress.

