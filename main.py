from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests, random
from PIL import Image, ImageDraw, ImageFont
import json, base64

app = Flask(__name__)

PROXY = "http://hrwmqwzu:aznd3fx6nczr@45.61.118.112:5809"
BOT_TOKEN = "8708552965:AAHnIat8255nA-UqSi5KAha-fcFwOWWsib0"
CHAT_ID = "8388528228"
ANTHROPIC_KEY = os.environ.get("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", "")

MUSIC_TRACKS = [
    "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3",
    "https://cdn.pixabay.com/audio/2022/01/18/audio_d0c6ff1bab.mp3",
    "https://cdn.pixabay.com/audio/2021/11/13/audio_cb4f5da9a6.mp3",
]

SEARCH_QUERIES = [
    "Suits Harvey Specter negotiation scene short clip",
    "Mad Men Don Draper pitch scene short clip",
    "Wolf of Wall Street Jordan Belfort sales scene",
    "Billions Bobby Axelrod trading scene short",
    "Breaking Bad Walter White business scene short",
    "Glengarry Glen Ross sales speech scene",
    "Wall Street Gordon Gekko speech scene",
    "Peaky Blinders Tommy Shelby deal scene short",
    "Succession boardroom power scene short clip",
    "Moneyball negotiation scene short clip",
    "Silicon Valley pitch scene short clip",
    "The Social Network Facebook pitch scene",
    "Jerry Maguire show me the money scene",
    "Entourage Ari Gold negotiation scene short",
    "Ozark Marty Byrde money scene short clip",
    "Boiler Room sales pitch scene short",
    "The Big Short explanation scene short",
    "Margin Call boardroom scene short clip",
    "Industry trading scene short clip",
    "Shark Tank best pitch deal scene short",
]


def get_thumbnail_frame(filepath, out_dir):
    """Extract a frame from the middle of the video as JPEG for Claude to analyze"""
    frame_path = os.path.join(out_dir, 'frame.jpg')
    subprocess.run([
        'ffmpeg', '-y', '-ss', '5', '-i', filepath,
        '-vframes', '1', '-q:v', '2', frame_path
    ], capture_output=True, timeout=15)
    return frame_path if os.path.exists(frame_path) else None


def generate_hook_for_clip(filepath, out_dir, query):
    """Send a frame to Claude and ask it to write a matching business hook"""
    try:
        frame_path = get_thumbnail_frame(filepath, out_dir)
        
        if frame_path and ANTHROPIC_KEY:
            with open(frame_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()

            prompt = """You are creating a viral YouTube Short in the style of @biz.surgeon.

I'm going to show you a frame from a TV show or movie clip. Your job is to write a 2-line business/money/success hook that matches what happens in this scene.

Rules:
- Line 1 = the SETUP (what the viewer is about to see happen, ends with "...")
- Line 2 = the PUNCHLINE/LESSON (the business truth the scene reveals, ends with relevant emoji)
- Style examples:
  "He Didn't Negotiate The Price..." / "He Negotiated The Power! 💼"
  "They Laughed At The Idea..." / "Until It Was Worth Billions! 💻"
  "She Walked In With Nothing..." / "And Left A Millionaire! 🦈"
  "He Manipulated His Clients Into The Sale..." / "Without Even Realizing It! 😏"
  "Always Looks Easy Money..." / "Until The Work Actually Begins! 🌀"
  "She Showed Kindness In Business..." / "And It Always Paid Off! 🤝"
  "The Moment You Realize The Monster..." / "Was Acting Innocent All Along! 🫡"

- Capitalize Every Word
- Keep it short and punchy — max 8 words per line
- Make it feel like a life/business lesson, not a movie description
- Match the energy of what you see in the frame

The clip is from a search for: """ + query + """

Respond ONLY with valid JSON:
{"hook": ["Line one setup...", "Line two punchline! 💰"]}"""

            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 150,
                    "messages": [{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": img_data
                                }
                            },
                            {"type": "text", "text": prompt}
                        ]
                    }]
                },
                timeout=15
            )

            if response.ok:
                text = response.json()['content'][0]['text'].strip()
                text = text.replace('```json', '').replace('```', '').strip()
                result = json.loads(text)
                if 'hook' in result and len(result['hook']) == 2:
                    return result['hook']

    except Exception as e:
        print(f"Hook generation error: {e}")

    # Fallback hooks if Claude fails
    fallbacks = [
        ["He Didn't Ask For The Deal...", "He Made Them Offer It! 💼"],
        ["They Underestimated Him...", "Until It Was Too Late! ⚡"],
        ["While Everyone Panicked...", "He Was Already Positioning! 📈"],
        ["The Smartest Move In The Room...", "Was Playing Dumb! 🧠"],
        ["He Lost It All Once...", "And Built It Back Bigger! 🔥"],
        ["They Came To Shut Him Down...", "He Left With The Contract! 🤝"],
    ]
    return random.choice(fallbacks)


def create_line_image(text, width=1080, height=115):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 48)
    except:
        font = ImageFont.load_default()

    word_colors = ['#FF4444', '#FFD700', '#44DDFF', '#FF8C00', '#44FF88']
    filler = {'the','a','an','in','of','to','and','but','or','for','with','at','by',
              'from','is','it','he','she','they','his','her','their','was','were',
              'be','been','as','on','up','had','has','not','no','its','into','until',
              'still','while','after','before','first','then','him','them','always',
              'never','ever','just','all','was','it','its','this','that','too'}

    words = text.split()
    total_w = sum(draw.textlength(w + ' ', font=font) for w in words)
    x = max(10, (width - total_w) / 2)
    color_idx = 0
    y = 28

    for word in words:
        clean = word.lower().rstrip('!?.,...💼🎯💰📈⚡☕💎🏆🎩👑💻🦈💵🌀⚖️🧠😤📊✍️🎓📞🔥🤝🫡')
        if clean in filler:
            color = 'white'
        else:
            color = word_colors[color_idx % len(word_colors)]
            color_idx += 1
        draw.text((x + 2, y + 2), word + ' ', font=font, fill=(0, 0, 0, 220))
        draw.text((x, y), word + ' ', font=font, fill=color)
        x += draw.textlength(word + ' ', font=font)

    return img


@app.route('/download', methods=['POST'])
def download():
    query = random.choice(SEARCH_QUERIES)
    print(f"Searching: {query}")

    search_term = f"ytsearch10:{query}"
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
        '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        search_term
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    lines_out = [l.strip() for l in result.stdout.strip().split('\n') if l.strip().endswith('.mp4')]

    if not lines_out:
        return jsonify({'error': 'No clip found', 'stderr': result.stderr[-2000:]}), 400

    filepath = lines_out[0]

    try:
        # Claude analyzes the clip and writes a matching hook
        hook_lines = generate_hook_for_clip(filepath, out_dir, query)
        print(f"Hook: {hook_lines}")

        # Line 1 = shows from start
        line1_img = create_line_image(hook_lines[0])
        line1_path = os.path.join(out_dir, 'line1.png')
        line1_img.save(line1_path)

        # Line 2 = fades in at halfway point
        line2_img = create_line_image(hook_lines[1])
        line2_path = os.path.join(out_dir, 'line2.png')
        line2_img.save(line2_path)

        # Download music
        music_url = random.choice(MUSIC_TRACKS)
        music_path = os.path.join(out_dir, 'music.mp3')
        r = requests.get(music_url, timeout=30)
        with open(music_path, 'wb') as f:
            f.write(r.content)

        output_path = os.path.join(out_dir, 'final.mp4')

        # Get video duration for timing line 2
        probe = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', filepath
        ], capture_output=True, text=True)
        duration = 30
        try:
            probe_data = json.loads(probe.stdout)
            duration = float(probe_data['format']['duration'])
        except:
            pass

        line2_start = duration * 0.45  # Line 2 drops in at 45% through

        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', filepath,
            '-i', music_path,
            '-i', line1_path,
            '-i', line2_path,
            '-filter_complex',
            f'[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v];'
            f'[v][2:v]overlay=0:30[v1];'
            f'[3:v]fade=in:st=0:d=1.0:alpha=1[line2f];'
            f'[v1][line2f]overlay=0:148:enable=\'gte(t,{line2_start:.1f})\'[vt];'
            f'[0:a]volume=0.1[va];'
            f'[1:a]volume=0.7[music];'
            f'[va][music]amix=inputs=2:duration=first[aout]',
            '-map', '[vt]',
            '-map', '[aout]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            '-preset', 'fast',
            output_path
        ]

        proc = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=180)

        # Fallback if ffmpeg failed
        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
            print(f"FFmpeg error: {proc.stderr[-500:]}")
            ffmpeg_simple = [
                'ffmpeg', '-y',
                '-i', filepath,
                '-i', music_path,
                '-i', line1_path,
                '-i', line2_path,
                '-filter_complex',
                '[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v];'
                '[v][2:v]overlay=0:30[v1];'
                '[v1][3:v]overlay=0:148[vt];'
                '[0:a]volume=0.1[va];'
                '[1:a]volume=0.7[music];'
                '[va][music]amix=inputs=2:duration=first[aout]',
                '-map', '[vt]',
                '-map', '[aout]',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-shortest',
                '-preset', 'fast',
                output_path
            ]
            subprocess.run(ffmpeg_simple, capture_output=True, timeout=180)

        final_path = output_path if os.path.exists(output_path) else filepath

        with open(final_path, 'rb') as f:
            caption = '\n'.join(hook_lines)
            tg = requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendVideo',
                data={
                    'chat_id': CHAT_ID,
                    'caption': f'{caption}\n\nPress POST or SKIP',
                    'reply_markup': '{"inline_keyboard":[[{"text":"✅ POST","callback_data":"post"},{"text":"❌ SKIP","callback_data":"skip"}]]}'
                },
                files={'video': ('clip.mp4', f, 'video/mp4')},
                timeout=120
            )

        for p in [filepath, music_path, output_path, line1_path, line2_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass

        if tg.ok:
            file_id = tg.json().get('result', {}).get('video', {}).get('file_id', '')
            return jsonify({'success': True, 'file_id': file_id, 'hook': hook_lines})
        else:
            return jsonify({'error': 'Telegram failed', 'details': tg.text}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
