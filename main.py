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
    filesize = os.path.getsize(filepath)

    try:
        # Step 1: Get a signed upload URL from Shotstack
        signed = requests.post(
            'https://api.shotstack.io/ingest/stage/upload',
            headers={
                'x-api-key': SHOTSTACK_KEY,
                'Content-Type': 'application/json'
            },
            json={'filename': filename},
            timeout=30
        )

        if not signed.ok:
            os.remove(filepath)
            return jsonify({'error': 'Could not get upload URL', 'details': signed.text}), 500

        signed_data = signed.json()
        upload_url = signed_data.get('data', {}).get('attributes', {}).get('url', '')
        source_url = signed_data.get('data', {}).get('attributes', {}).get('source', '')

        if not upload_url:
            os.remove(filepath)
            return jsonify({'error': 'No upload URL returned', 'response': signed_data}), 500

        # Step 2: Upload file directly to signed URL
        with open(filepath, 'rb') as f:
            put = requests.put(
                upload_url,
                data=f,
                headers={'Content-Type': 'video/mp4'},
                timeout=300
            )

        os.remove(filepath)

        if put.ok or put.status_code == 200:
            return jsonify({
                'success': True,
                'video_url': source_url,
                'filename': filename,
                'size': filesize
            })
        else:
            return jsonify({'error': 'PUT upload failed', 'status': put.status_code}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
