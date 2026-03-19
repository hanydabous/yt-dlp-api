from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests, threading, uuid

app = Flask(__name__)
jobs = {}

def run_download(job_id, query):
    jobs[job_id] = {'status': 'running'}
    
    search_term = f"ytsearch1:{query}"
    out_dir = tempfile.mkdtemp()
    out_template = os.path.join(out_dir, '%(id)s.%(ext)s')

    cmd = [
        'yt-dlp',
        '--format', 'best[height<=480][ext=mp4]/best[height<=480]/worst',
        '--no-playlist',
        '--no-check-certificate',
        '--extractor-retries', '3',
        '--cookies', '/app/cookies.txt',
        '--output', out_template,
        '--print', 'after_move:filepath',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        search_term
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip().endswith('.mp4')]

    if not lines:
        jobs[job_id] = {
            'status': 'error',
            'error': 'No clip found',
            'stderr': result.stderr[-2000:]
        }
        return

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
            jobs[job_id] = {
                'status': 'done',
                'video_url': upload.json().get('link'),
                'filename': os.path.basename(filepath)
            }
        else:
            jobs[job_id] = {'status': 'error', 'error': 'Upload failed'}
    except Exception as e:
        jobs[job_id] = {'status': 'error', 'error': str(e)}

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    query = data.get('query', '')
    job_id = str(uuid.uuid4())
    thread = threading.Thread(target=run_download, args=(job_id, query))
    thread.start()
    return jsonify({'job_id': job_id, 'status': 'started'})

@app.route('/status/<job_id>', methods=['GET'])
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({'status': 'not_found'}), 404
    return jsonify(job)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
