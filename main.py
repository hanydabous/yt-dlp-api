from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests, random, json

app = Flask(__name__)

PROXY = "http://hrwmqwzu:aznd3fx6nczr@45.61.118.112:5809"
BOT_TOKEN = "8708552965:AAHnIat8255nA-UqSi5KAha-fcFwOWWsib0"
CHAT_ID = "8388528228"

MUSIC_TRACKS = [
    "https://cdn.pixabay.com/audio/2022/10/14/audio_b43c3b5e38.mp3",
    "https://cdn.pixabay.com/audio/2023/03/09/audio_c0d2b85c39.mp3",
    "https://cdn.pixabay.com/audio/2022/08/02/audio_884fe92c21.mp3",
]

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    query = data.get('query', '')

    search_term = f"ytsearch10:{query} site:youtube.com"
    out_dir = tempfile.mkdtemp()
    out_template = os.path.join(out_dir, '%(id)s.%(ext)s')

    cmd = [
        'yt-dlp',
        '--format', 'bestvideo[height<=1080][ext=mp4]+bestaudio/best[height<=1080]',
        '--merge-output-format', 'mp4',
        '--no-playlist',
        '--no-check-certificate',
        '--extractor-retries', '3',
        '--cookies', '/app/cookies.txt',
        '--proxy', PROXY,
        '--remote-components', 'ejs:github',
        '--max-filesize', '100m',
        '--match-filter', 'duration <= 180',
        '--output', out_template,
        '--print', 'after_move:filepath',
        '--write-info-json',
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        search_term
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip().endswith('.mp4')]

    if not lines:
        return jsonify({'error': 'No clip found', 'stderr': result.stderr[-2000:]}), 400

    filepath = lines[0]
    filename = os.path.basename(filepath)

    # Get video title from info json
    info_path = filepath.replace('.mp4', '.info.json')
    video_title = query
    if os.path.exists(info_path):
        try:
            with open(info_path) as f:
                info = json.load(f)
                video_title = info.get('title', query)[:60]
        except:
            pass

    try:
        # Download music
        music_url = random.choice(MUSIC_TRACKS)
        music_path = os.path.join(out_dir, 'music.mp3')
        music_resp = requests.get(music_url, timeout=30)
        with open(music_path, 'wb') as f:
            f.write(music_resp.content)

        # Crop to 9:16, add music, add text overlay at top
        output_path = os.path.join(out_dir, 'final.mp4')

        # Escape title for ffmpeg
        safe_title = video_title.replace("'", "").replace('"', '').replace(':', ' -').replace('\\', '')[:50]

        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', filepath,
            '-i', music_path,
            '-filter_complex',
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v];"
            f"[v]drawtext=text='{safe_title}':fontsize=42:fontcolor=white:x=(w-text_w)/2:y=60:"
            f"box=1:boxcolor=black@0.5:boxborderw=10[vt];"
            f"[0:a]volume=1.0[va];"
            f"[1:a]volume=0.4[music];"
            f"[va][music]amix=inputs=2:duration=first[aout]",
            '-map', '[vt]',
            '-map', '[aout]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            '-preset', 'fast',
            output_path
        ]

        subprocess.run(ffmpeg_cmd, capture_output=True, timeout=180)

        final_path = output_path if os.path.exists(output_path) else filepath

        with open(final_path, 'rb') as f:
            tg = requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendVideo',
                data={
                    'chat_id': CHAT_ID,
                    'caption': f'{video_title}\n\nPress POST or SKIP',
                    'reply_markup': '{"inline_keyboard":[[{"text":"✅ POST","callback_data":"post"},{"text":"❌ SKIP","callback_data":"skip"}]]}'
                },
                files={'video': ('clip.mp4', f, 'video/mp4')},
                timeout=120
            )

        for p in [filepath, music_path, output_path, info_path]:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except:
                    pass

        if tg.ok:
            file_id = tg.json().get('result', {}).get('video', {}).get('file_id', '')
            return jsonify({'success': True, 'file_id': file_id, 'title': video_title})
        else:
            return jsonify({'error': 'Telegram send failed', 'details': tg.text}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
