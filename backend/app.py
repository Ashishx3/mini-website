from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp  # Ensure you're using yt-dlp for better compatibility
import os  # Import os to handle file system operations

app = Flask(__name__, static_folder='static', template_folder='templates')

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

        return jsonify({'success': True, 'file': filename})
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'success': False, 'message': 'Conversion failed'})

@app.route('/downloads/<filename>', methods=['GET'])
def download_file(filename):
    return send_file(f'{DOWNLOAD_FOLDER}/{filename}', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
