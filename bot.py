import os
import subprocess
from telegram.ext import Updater, MessageHandler, Filters

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set in hosting environment

def handle_file(update, context):
    file = update.message.video or update.message.document
    file_name = file.file_name if file and hasattr(file, 'file_name') else 'video_input'
    os.makedirs("downloads", exist_ok=True)
    download_path = f"downloads/{file_name}"
    output_path = f"downloads/streamable.mp4"

    # Download the file
    file.get_file().download(download_path)

    try:
        # Convert to streamable MP4 using ffmpeg
        subprocess.run([
            'ffmpeg', '-i', download_path,
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-movflags', '+faststart',
            output_path
        ], check=True)

        # Send the streamable video
        with open(output_path, 'rb') as video_file:
            update.message.reply_video(video=video_file, supports_streaming=True)

    except Exception as e:
        update.message.reply_text(f"❌ Failed to convert: {e}")

    # Cleanup
    if os.path.exists(download_path): os.remove(download_path)
    if os.path.exists(output_path): os.remove(output_path)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.video | Filters.document, handle_file))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
