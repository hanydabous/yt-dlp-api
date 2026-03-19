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
        return jsonify({
            'error': 'No clip found',
            'stderr': result.stderr[-2000:]
        }), 400

    filepath = lines[0]
    filename = os.path.basename(filepath)

    try:
        # Step 1: Create upload source and get signed URL
        upload_req = requests.post(
            'https://api.shotstack.io/ingest/stage/upload',
            headers={
                'x-api-key': SHOTSTACK_KEY,
                'Content-Type': 'application/json'
            },
            json={'filename': filename, 'contentType': 'video/mp4'},
            timeout=30
        )

        if not upload_req.ok:
            os.remove(filepath)
            return jsonify({'error': 'Upload init failed', 'details': upload_req.text}), 500

        upload_data = upload_req.json()
        put_url = upload_data.get('data', {}).get('attributes', {}).get('url', '')
        source_url = upload_data.get('data', {}).get('attributes', {}).get('source', '')

        if not put_url:
            os.remove(filepath)
            return jsonify({'error': 'No URL in response', 'response': upload_data}), 500

        # Step 2: PUT file to signed URL
        with open(filepath, 'rb') as f:
            put = requests.put(
                put_url,
                data=f.read(),
                headers={'Content-Type': 'video/mp4'},
                timeout=300
            )

        os.remove(filepath)

        return jsonify({
            'success': True,
            'video_url': source_url,
            'filename': filename,
            'put_status': put.status_code
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
