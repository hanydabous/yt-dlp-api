from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests, random, json

app = Flask(__name__)

PROXY = "http://hrwmqwzu:aznd3fx6nczr@45.61.118.112:5809"
BOT_TOKEN = "8708552965:AAHnIat8255nA-UqSi5KAha-fcFwOWWsib0"
CHAT_ID = "8388528228"

# Slowed + reverb emotional/cinematic tracks like @mdscae style
MUSIC_TRACKS = [
    "https://cdn.pixabay.com/audio/2023/10/30/audio_0b0c7e1d2d.mp3",
    "https://cdn.pixabay.com/audio/2024/02/15/audio_a80a28ce7f.mp3",
    "https://cdn.pixabay.com/audio/2022/11/22/audio_ea3371b02f.mp3",
    "https://cdn.pixabay.com/audio/2023/05/16/audio_6b3b9572cd.mp3",
    "https://cdn.pixabay.com/audio/2022/10/14/audio_b43c3b5e38.mp3",
    "https://cdn.pixabay.com/audio/2023/09/05/audio_5e5b8be1ba.mp3",
    "https://cdn.pixabay.com/audio/2022/08/25/audio_64d7771af8.mp3",
]

# Hook text to show at top of video
HOOKS = [
    "This scene hits different",
    "POV: you just discovered this",
    "This is pure cinema",
    "Nobody talks about this scene",
    "The acting in this scene tho",
    "This scene lives rent free in my head",
    "Criminally underrated scene",
    "This moment changed everything",
    "The way this was filmed tho",
    "This is what cinema is about",
]

# Viral movie/series search queries — rotates automatically
QUERIES = [
    "Breaking Bad intense scene",
    "Game of Thrones epic moment",
    "Peaky Blinders confrontation scene",
    "The Boys shocking scene",
    "Better Call Saul emotional scene",
    "Succession power moment",
    "Ozark tense scene",
    "Black Mirror twist scene",
    "Avengers emotional moment",
    "Interstellar emotional scene",
    "The Dark Knight joker scene",
    "Oppenheimer dramatic scene",
    "No Country for Old Men scene",
    "There Will Be Blood scene",
    "Inception mind bending scene",
    "Dune epic scene",
    "John Wick fight scene",
    "The Godfather scene",
    "Goodfellas scene",
    "Pulp Fiction scene",
    "Fight Club scene",
    "Se7en ending scene",
    "Prisoners emotional scene",
    "Mindhunter interrogation scene",
    "Chernobyl emotional scene",
    "The Last of Us emotional scene",
    "Squid Game intense scene",
    "Dark Netflix emotional scene",
]

USED_FILE = '/tmp/used_queries.json'

def get_unused_query():
    used = []
    if os.path.exists(USED_FILE):
        with open(USED_FILE) as f:
            used = json.load(f)
    unused = [q for q in QUERIES if q not in used]
    if not unused:
        unused = QUERIES
        used = []
    query = random.choice(unused)
    used.append(query)
    with open(USED_FILE, 'w') as f:
        json.dump(used, f)
    return query

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    force_query = data.get('query', '')
    skip = data.get('skip', False)

    query = force_query if force_query and not skip else get_unused_query()

    search_term = f"ytsearch10:{query}"
    out_dir = tempfile.mkdtemp()
    out_template = os.path.join(out_dir, '%(id)s.%(ext)s')

    cmd = [
        'yt-dlp',
        '--format', 'bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720]',
        '--merge-output-format', 'mp4',
        '--no-playlist',
        '--no-check-certificate',
        '--extractor-retries', '3',
        '--cookies', '/app/cookies.txt',
        '--proxy', PROXY,
        '--remote-components', 'ejs:github',
        '--max-filesize', '80m',
        '--match-filter', 'duration <= 180',
        '--output', out_template,
        '--print', 'after_move:filepath',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        search_term
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip().endswith('.mp4')]

    if not lines:
        return jsonify({'error': 'No clip found', 'stderr': result.stderr[-1000:], 'query': query}), 400

    filepath = lines[0]
    filename = os.path.basename(filepath)

    try:
        # Download music
        music_url = random.choice(MUSIC_TRACKS)
        music_path = os.path.join(out_dir, 'music.mp3')
        music_resp = requests.get(music_url, timeout=30)
        with open(music_path, 'wb') as f:
            f.write(music_resp.content)

        # Pick hook text
        hook = random.choice(HOOKS)

        # Process with ffmpeg: mix music + add text overlay
        output_path = os.path.join(out_dir, 'final.mp4')

        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', filepath,
            '-i', music_path,
            '-filter_complex',
            f"[0:a]volume=0.8[va];[1:a]volume=0.45,afade=t=out:st=170:d=10[music];[va][music]amix=inputs=2:duration=first[aout],"
            f"[0:v]drawtext=text='{hook}':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=60:box=1:boxcolor=black@0.5:boxborderw=10:font=Arial:borderw=3:bordercolor=black[vout]",
            '-map', '[vout]',
            '-map', '[aout]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-b:v', '2M',
            '-shortest',
            output_path
        ]

        ffmpeg_result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=180)
        final_path = output_path if os.path.exists(output_path) else filepath

        with open(final_path, 'rb') as f:
            tg = requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendVideo',
                data={
                    'chat_id': CHAT_ID,
                    'caption': f'🎬 {query}\n\nPress POST or SKIP for another clip',
                    'reply_markup': '{"inline_keyboard":[[{"text":"✅ POST","callback_data":"post"},{"text":"❌ SKIP","callback_data":"skip"}]]}'
                },
                files={'video': ('clip.mp4', f, 'video/mp4')},
                timeout=180
            )

        for p in [filepath, music_path, output_path]:
            if os.path.exists(p):
                os.remove(p)

        if tg.ok:
            tg_data = tg.json()
            file_id = tg_data.get('result', {}).get('video', {}).get('file_id', '')
            return jsonify({
                'success': True,
                'file_id': file_id,
                'query': query,
                'hook': hook
            })
        else:
            return jsonify({'error': 'Telegram send failed', 'details': tg.text}), 500

    except Exception as e:
        for p in [filepath]:
            if os.path.exists(p):
                os.remove(p)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
