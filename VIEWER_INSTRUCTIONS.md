# 📱 Telegram Message Viewer

## 🚀 Quick Start

1. **Run the viewer server:**
   ```bash
   python run_viewer.py
   ```
   or
   ```bash
   python3 run_viewer.py
   ```

2. **Browser will open automatically** to `http://localhost:8000/telegram_viewer.html`

3. **Setup user mappings (optional):**
   - Create a `users.json` file in the same directory as the HTML file
   - Map user IDs to usernames for better readability
   - See [User Mapping](#-user-mapping) section below

4. **Enter data:**
   - Group ID: example `10011223344`
   - Thread ID: choose from dropdown:
     - **"No Thread (All Messages)"** - for backup without thread filter
     - **"Thread 6"**, **"Thread 19"**, etc. - for specific thread
   - Click **"Load Messages"**

## ✨ Viewer Features

### 🎨 **Telegram-like Interface**
- Dark theme like Telegram Desktop
- Chat bubbles with different colors for incoming/outgoing messages
- Smooth animations when scrolling
- **Lazy loading**: Loads messages in batches for better performance
- **Bidirectional scrolling**: Load older messages by scrolling up

### 🔍 **Search & Filter**
- **Search bar**: search text in messages or file names
- **Filter by type**: 
  - All Messages (all)
  - All Media (all media)
  - Images Only (images & GIFs)
  - Videos Only (videos only)
  - Audio Only (music/voice)
  - Documents Only (documents/files)
  - Text Only (text only)
- **Real-time filtering** while typing
- **Smart scrolling**: Automatically scrolls to newest messages after filtering
- **Full archive search**: Search works across all messages, not just visible ones

### 🖼️ **Media Support**
- **Images**: Preview images directly in chat, click for fullscreen
- **Animated GIFs**: Full support for animated GIFs 🎞️
- **Videos**: HTML5 video player with controls (play/pause/volume) 🎥
- **Audio**: HTML5 audio player for music/voice notes 🎵
- **Documents**: Preview with icon, click to download 📄
- **Archives**: ZIP/RAR files with special icons 📦
- **Modal popup**: ESC to close, supports all formats

### 📊 **Message Information**
- Timestamp with smart formatting (Today, Yesterday, etc.)
- "Deleted message" info
- Forward info if available
- Reply info if available
- **Smart user display**: Shows usernames if mapped, falls back to user IDs
- **Performance optimized**: Only renders visible messages for large archives

### 📱 **Responsive Design**
- Works on desktop & mobile
- Auto-scroll to latest messages
- Keyboard shortcuts (ESC to close modal)

## 🆔 User Mapping

Transform user IDs like `123456789` into readable usernames like `@username1`.

### Setup users.json

Create a `users.json` file in the same directory as `telegram_viewer.html`:

```json
{
  "123456789": "@username1",
  "987654321": "@username2", 
  "555666777": "@username3",
  "111222333": "@username4"
}
```

### Features
- **Automatic loading**: Loads on page start and when loading messages
- **Graceful fallback**: Shows `User 12345` if mapping not found
- **Error handling**: Works even if `users.json` is missing
- **Real-time**: Updates all sender names and forward info immediately

### Benefits
- Much easier to identify who sent messages
- Better readability in group chats
- Professional appearance for documentation/reports

## 📁 Folder Structure

Make sure the folder structure looks like this:
```
your-project/
├── telegram_viewer.html
├── run_viewer.py
├── users.json                  # Optional: User ID to username mapping
├── backup/
│   └── 10011223344/            # Group ID
│       ├── dump.json           # For backup WITHOUT thread
│       ├── msg_123/            # Media without thread
│       ├── album_456/          # Album without thread
│       ├── thread_6/           # Specific thread
│       │   ├── dump.json
│       │   ├── msg_123/
│       │   │   └── photo.jpg
│       │   └── album_456/
│       │       ├── photo1.jpg
│       │       └── photo2.jpg
│       ├── thread_19/
│       └── thread_6697/
```

## 🛠️ Troubleshooting

### Port already in use?
```bash
python run_viewer.py
# If error port 8000 is used, try:
python -m http.server 8001
# Then open http://localhost:8001/telegram_viewer.html
```

### Can't load JSON file?
- Make sure Python server is running
- Make sure backup folder path is correct
- Check browser console (F12) for error details

### Images not showing?
- Make sure image files exist in the correct folder
- Check path in `local_media_file` in JSON
- Make sure server can access backup folder

### Users showing as IDs instead of usernames?
- Make sure `users.json` is in the same directory as the HTML file
- Check browser console (F12) for user mapping load status
- Verify JSON format is correct (no trailing commas)
- File should be accessible via HTTP server

### Performance issues with large archives?
- Lazy loading automatically handles large archives (10,000+ messages)
- Only 50 messages render at a time
- Scroll up/down to load more messages automatically
- Search still works across all messages, not just visible ones

## 🎯 Usage Tips

1. **Backup Strategy**:
   - **"No Thread"** - for regular groups or backup all messages at once
   - **"Thread X"** - for forum/supergroup with separate topics

2. **Performance with Large Archives**:
   - Viewer handles 10,000+ messages smoothly with lazy loading
   - Initial load shows 50 most recent messages
   - Scroll down for newer messages, scroll up for older messages
   - Search works across entire archive, not just visible messages

3. **User Experience**:
   - Create `users.json` for readable usernames instead of IDs
   - Filters automatically scroll to newest matching messages
   - Use search + filter combination for precise results

4. **Navigation Tips**:
   - **Multiple Threads**: Change thread ID to view different threads
   - **Search**: Search text in messages or file names (searches all messages)
   - **Smart Filtering**: After applying filters, viewer shows newest matches first

5. **Media Handling**: 
   - "Images Only" for photo & GIF gallery
   - "Videos Only" for all videos  
   - "Documents Only" for downloadable files
   - **Fullscreen**: Click image/GIF to view full size
   - **Video/Audio**: Built-in controls (play/pause/volume/scrub)
   - **Download**: Click document file to download directly

6. **Mobile Support**: Works on mobile, touch controls for video/audio

## 🔧 Customization

Edit `telegram_viewer.html` to:
- Change theme colors
- Add new features
- Modify layout
- Add more file types support
- Adjust `messagesPerBatch` variable for different lazy loading batch sizes
- Modify user display format in `getUserDisplayName()` function

Edit `users.json` to:
- Add more user ID to username mappings
- Update usernames as needed
- Remove users no longer in the group

## 📊 Performance Features

- **Lazy Loading**: Only renders 50 messages at a time for instant startup
- **Bidirectional Scrolling**: Load older/newer messages on demand
- **Smart Memory Usage**: Large archives don't overwhelm browser memory
- **Full Search**: Search functionality works across entire archive
- **Optimized Rendering**: Smooth scrolling even with media-heavy messages

## 📞 Notes

- This viewer is for local viewing only
- Data is not sent to any server
- Pure HTML/CSS/JS, no external dependencies
- Compatible with all modern browsers
- Optimized for large message archives (tested with 10,000+ messages)
- User mappings are optional - viewer works without `users.json`