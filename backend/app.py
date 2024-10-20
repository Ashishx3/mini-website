from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp  # Ensure you're using yt-dlp for better compatibility
import os  # Import os to handle file system operations
import logging  # Import logging for logging configuration

# Initialize Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format for log messages
)

# Path to save MP3 files
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')  # Serve the HTML from the templates folder

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    video_url = data['url']
    bitrate = data.get('bitrate', '128kbps')  # Default to 128kbps if not specified

    # Set the audio quality based on the selected bitrate
    bitrate_mapping = {
        '128kbps': '128',
        '192kbps': '192',
        '320kbps': '320',
    }
    selected_quality = bitrate_mapping.get(bitrate, '128')

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': selected_quality,
            }],
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        logging.info(f'Successfully converted video: {video_url} to {filename}')
        return jsonify({'success': True, 'file': filename})
    except Exception as e:
        logging.error(f'Error during conversion: {e}', exc_info=True)  # Log the error with stack trace
        return jsonify({'success': False, 'message': 'Conversion failed', 'error': str(e)})

@app.route('/downloads/<path:filename>', methods=['GET'])
def download_file(filename):
    # Sanitize the filename to prevent directory traversal attacks
    safe_filename = os.path.basename(filename)
    try:
        return send_file(os.path.join(DOWNLOAD_FOLDER, safe_filename), as_attachment=True)
    except FileNotFoundError:
        logging.error(f'File not found for download: {safe_filename}')
        return jsonify({'success': False, 'message': 'File not found'}), 404

if __name__ == '__main__':
    # Only run the app directly if this script is executed
    app.run(debug=True)
