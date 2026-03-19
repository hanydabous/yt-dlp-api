from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests

app = Flask(__name__)

PROXY = "http://hrwmqwzu:aznd3fx6nczr@31.59.20.176:6754"

def install_deno():
    deno = '/root/.deno/bin/deno'
    if not os.path.exists(deno):
        os.system('curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/root/.deno sh 2>/dev/null')
    if os.path.exists(deno):
        os.environ['PATH'] = '/root/.deno/bin:' + os.environ.get('PATH', '')
        os.environ['DENO_INSTALL'] = '/root/.deno'
    return os.path.exists(deno)

install_deno()

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    query = data.get('query', '')

    search_term = f"ytsearch1:{query}"
    out_dir = tempfile.mkdtemp()
    out_template = os.path.join(out_dir, '%(id)s.%(ext)s')

    env = os.environ.copy()
    env['PATH'] = '/root/.deno/bin:' + env.get('PATH', '')

    cmd = [
        'yt-dlp',
        '--format', 'worst[ext=mp4]/worst',
        '--no-playlist',
        '--no-check-certificate',
        '--extractor-retries', '3',
        '--cookies', '/app/cookies.txt',
        '--proxy', PROXY,
        '--output', out_template,
        '--print', 'after_move:filepath',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        search_term
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=240, env=env)
    lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip().endswith('.mp4')]

    if not lines:
        return jsonify({
            'error': 'No clip found',
            'stderr': result.stderr[-2000:]
        }), 400

    filepath = lines[0]

    try:
        with open(filepath, 'rb') as f:
            upload = requests.post(
                'https://file.io/?expires=1d',
                files={'file': (os.path.basename(filepath), f, 'video/mp4')},
                timeout=60
            )
        os.remove(filepath)

        if upload.ok:
            return jsonify({
                'success': True,
                'video_url': upload.json().get('link'),
                'filename': os.path.basename(filepath)
            })
        else:
            return jsonify({'error': 'Upload failed'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
