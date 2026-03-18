from flask import Flask, request, jsonify
import subprocess, os, tempfile, base64

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    query = data.get('query', '')

    search_term = f"ytsearch1:{query}"
    out_dir = tempfile.mkdtemp()
    out_template = os.path.join(out_dir, '%(id)s.%(ext)s')

    cmd = [
        'yt-dlp',
        '--format', 'best[height<=720][ext=mp4]/best[height<=720]/best',
        '--no-playlist',
        '--no-check-certificate',
        '--extractor-retries', '5',
        '--sleep-interval', '2',
        '--cookies', '/app/cookies.txt',
        '--output', out_template,
        '--print', 'after_move:filepath',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        search_term
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip().endswith('.mp4')]

    if not lines:
        return jsonify({
            'error': 'No clip found',
            'stdout': result.stdout,
            'stderr': result.stderr[-3000:]
        }), 400

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
