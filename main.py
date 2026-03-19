from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests

app = Flask(__name__)

PROXY = "http://hrwmqwzu:aznd3fx6nczr@31.59.20.176:6754"
SHOTSTACK_KEY = "Ymna74p8i5tavuS2aO7LPEAPGjBAZBf1KhHiK0TC"

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
        '--max-filesize', '50m',
        '--output', out_template,
        '--print', 'after_move:filepath',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        search_term
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=480)
    lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip().endswith('.mp4')]

    if not lines:
        return jsonify({'error': 'No clip found', 'stderr': result.stderr[-2000:]}), 400

    filepath = lines[0]
    filename = os.path.basename(filepath)

    try:
        with open(filepath, 'rb') as f:
            file_data = f.read()

        public_url = ''
        try:
            tmp = requests.post(
                'https://tmpfiles.org/api/v1/upload',
                files={'file': (filename, file_data, 'video/mp4')},
                timeout=60
            )
            if tmp.ok:
                raw = tmp.json().get('data', {}).get('url', '')
                public_url = raw.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
        except:
            pass

        upload_req = requests.post(
            'https://api.shotstack.io/ingest/stage/upload',
            headers={'x-api-key': SHOTSTACK_KEY, 'Content-Type': 'application/json'},
            json={'filename': filename},
            timeout=30
        )

        shotstack_url = ''
        source_id = ''
        if upload_req.ok:
            upload_data = upload_req.json()
            put_url = upload_data.get('data', {}).get('attributes', {}).get('url', '')
            source_id = upload_data.get('data', {}).get('id', '')
            if put_url:
                requests.put(put_url, data=file_data, timeout=300)
                shotstack_url = f"shotstack:{source_id}"

        os.remove(filepath)

        return jsonify({
            'success': True,
            'public_url': public_url,
            'shotstack_url': shotstack_url,
            'source_id': source_id,
            'filename': filename
        })

    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
