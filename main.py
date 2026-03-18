from flask import Flask, request, jsonify
import subprocess, os, uuid, tempfile

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    query = data.get('query', '')
    duration_max = data.get('duration_max', 60)
    
    search_term = f"ytsearch5:{query} scene clip official"
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
    
    import base64
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
```

4. Click **"Commit new file"**

**1.4 — Add requirements file**
1. Click "Add file" → "Create new file" again
2. Name it `requirements.txt`
3. Paste:
```
flask
yt-dlp
```
4. Commit it

**1.5 — Add Procfile**
1. "Add file" → "Create new file"
2. Name it `Procfile` (capital P, no extension)
3. Paste:
```
web: python main.py
```
4. Commit it

**1.6 — Deploy on Railway**
1. Go back to Railway, click "New Project" → "Deploy from GitHub repo"
2. Select your `yt-dlp-api` repo
3. Railway detects Python automatically and starts deploying
4. Wait about 2 minutes — you'll see a green "Active" status
5. Click your project → Settings → Domains → click **"Generate Domain"**
6. Copy the domain — it looks like `yt-dlp-api-production-xxxx.up.railway.app`
7. Keep this — this is your **DOWNLOADER URL**

---

## STEP 2 — Set up your Google Sheet for search terms

Instead of clip URLs, your sheet now holds **search queries** — what to search on YouTube.

**2.1 — Create the sheet**
1. Go to `sheets.google.com` → new sheet → name it "Viral Clips"
2. Row 1 headers exactly:
   - A1: `search_query`
   - B1: `category`
   - C1: `used`

**2.2 — Fill in search queries**

Add these rows (A2 onwards) — copy and paste all of these:
```
Breaking Bad intense scene,TV Series,false
Game of Thrones epic moment,TV Series,false
Avengers battle scene,Marvel,false
The Dark Knight Joker scene,Movie,false
Peaky Blinders confrontation,TV Series,false
Interstellar emotional scene,Movie,false
John Wick fight scene,Movie,false
Oppenheimer dramatic moment,Movie,false
Better Call Saul courtroom,TV Series,false
Inception mind bending scene,Movie,false
Thor ragnarok funny moment,Marvel,false
Breaking Bad chemistry scene,TV Series,false
GOT dragons scene,TV Series,false
Iron Man suit up scene,Marvel,false
The Boys shocking scene,TV Series,false
Dune epic scene,Movie,false
No Country for Old Men,Movie,false
Succession power scene,TV Series,false
Black Mirror twist ending,TV Series,false
Ozark tense scene,TV Series,false
