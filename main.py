from flask import Flask, request, jsonify, send_file
import subprocess, os, tempfile

app = Flask(__name__)

PROXY = "http://hrwmqwzu:aznd3fx6nczr@31.59.20.176:6754"
STORE = '/tmp/videos'
os.makedirs(STORE, exist_ok=True)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    query = data.get('query', '')

    search_term = f"ytsearch1:{query}"
    out_dir = tempfile.mkdtemp()
    out_template = os.path.join(out_dir, '%(id)s.%(ext)s')

    cmd = [
        'yt-dlp',
        '--format', 'worst',
        '--no-playlist',
        '--no-check-certificate',
        '--extractor-retries', '3',
        '--cookies', '/app/cookies.txt',
        '--proxy', PROXY,
        '--remote-components', 'ejs:github',
        '--max-filesize', '20m',
        '--output', out_template,
        '--print', 'after_move:filepath',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        search_term
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip().endswith('.mp4')]

    if not lines:
        return jsonify({'error': 'No clip found', 'stderr': result.stderr[-2000:]}), 400

    filepath = lines[0]
    filename = os.path.basename(filepath)
    dest = os.path.join(STORE, filename)
    os.rename(filepath, dest)

    public_url = f'https://web-production-32cbf.up.railway.app/serve/{filename}'

    return jsonify({
        'success': True,
        'public_url': public_url,
        'filename': filename
    })

@app.route('/serve/<filename>', methods=['GET'])
def serve(filename):
    path = os.path.join(STORE, filename)
    if os.path.exists(path):
        return send_file(path, mimetype='video/mp4')
    return 'Not found', 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
