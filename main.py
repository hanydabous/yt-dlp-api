from flask import Flask, request, jsonify
import subprocess, os, tempfile, base64

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    query = data.get('query', '')
    duration_max = data.get('duration_max', 60)

    search_term = f"ytsearch5:{query}"
    out_dir = tempfile.mkdtemp()
    out_template = os.path.join(out_dir, '%(id)s.%(ext)s')

    cmd = [
        'yt-dlp',
        '--format', 'bestvideo[height<=1080][ext=mp4]+bestaudio/best[height<=1080]',
        '--merge-output-format', 'mp4',
        '--match-filter', f'duration < {duration_max}',
        '--no-playlist',
        '--output', out_template,
        '--print', 'after_move:filepath',
        search_term
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip().endswith('.mp4')]

    if not lines:
        return jsonify({'error': 'No clip found', 'details': result.stderr}), 400

    filepath = lines[0]

    with open(filepath, 'rb') as f:
        video_b64 = base64.b64encode(f.read()).decode()

    os.remove(filepath)

    return jsonify({
        'success': True,
        'video_base64': video_b64,
        'filename': os.path.basename(filepath)
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
