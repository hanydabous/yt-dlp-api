from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests, random
from PIL import Image, ImageDraw, ImageFont
import json

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

FALLBACK_CLIPS = [
    {"query": "Suits Harvey Specter you dont send a message scene", "hook": ["He Didn't Negotiate The Price...", "He Negotiated The Power! 💼"]},
    {"query": "Mad Men Don Draper Carousel pitch scene", "hook": ["He Didn't Sell A Product...", "He Sold A Feeling! 🎯"]},
    {"query": "Wolf of Wall Street sell me this pen scene", "hook": ["Create The Need First...", "Then Offer The Solution! 💰"]},
    {"query": "Billions Bobby Axelrod I am the best scene", "hook": ["He Never Asked For Permission...", "He Asked For Forgiveness After! 📈"]},
    {"query": "Breaking Bad Walter White I am the danger scene", "hook": ["The Moment He Stopped Being A Victim...", "He Became The Boss! ⚡"]},
    {"query": "Glengarry Glen Ross coffee is for closers speech", "hook": ["He Came To Motivate Them...", "But Only The Strong Survived! ☕"]},
    {"query": "Wall Street Gordon Gekko greed is good speech", "hook": ["He Turned Greed Into...", "A Business Philosophy! 💎"]},
    {"query": "Peaky Blinders Tommy Shelby business deal scene", "hook": ["He Always Made An Offer...", "They Couldn't Refuse! 🎩"]},
    {"query": "Succession Logan Roy boardroom scene", "hook": ["He Built An Empire...", "By Trusting No One! 👑"]},
    {"query": "Moneyball we're gonna change the game scene", "hook": ["They Said It Was Impossible...", "Until He Made It The Standard! 🏆"]},
]


def generate_clip_idea():
    try:
        prompt = """You are a viral YouTube Shorts creator in the style of @mdscae and @biz.surgeon.

Generate ONE fresh idea for a business/money/success lesson clip from a famous TV show or movie.

The hook must have PROGRESSION and CLIMAX:
- Line 1 = the SETUP/TENSION (ends with "..." to create suspense)
- Line 2 = the CLIMAX/PUNCHLINE (the lesson that hits hard, ends with emoji)

Examples of perfect hooks:
- "He Didn't Negotiate The Price..." / "He Negotiated The Power! 💼"
- "They Laughed At The Idea..." / "Until It Was Worth Billions! 💻"
- "She Walked In With Nothing..." / "And Left A Millionaire! 🦈"
- "He Lost Everything Twice..." / "And Still Built An Empire! 🔥"
- "They Came To Fire Him..." / "He Left With The Deal! 🤝"
- "While Everyone Panicked..." / "He Was Already Positioning! 📈"

Use specific iconic scenes from: Suits, Mad Men, Breaking Bad, Billions, Succession, 
Peaky Blinders, Silicon Valley, The Social Network, Wolf of Wall Street, 
Glengarry Glen Ross, Wall Street, Moneyball, Entourage, Ozark, Shark Tank,
Jerry Maguire, The Godfather, American Psycho, Boiler Room, Margin Call,
The Big Short, Two and a Half Men, Modern Family, Scrubs, House MD,
Yellowstone, Ozark, Narcos, Boardwalk Empire, Billions, Industry

Respond ONLY with valid JSON:
{
  "query": "specific scene search query for YouTube",
  "hook": ["Line one setup with ...at end", "Line two climax with emoji! 🔥"]
}"""

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 200,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=15
        )

        if response.ok:
            text = response.json()['content'][0]['text'].strip()
            text = text.replace('```json', '').replace('```', '').strip()
            idea = json.loads(text)
            if 'query' in idea and 'hook' in idea:
                return idea

    except Exception as e:
        print(f"Claude API error: {e}")

    return random.choice(FALLBACK_CLIPS)


def create_line_image(text, width=1080, height=110):
    """Create a single line of colored text as PNG"""
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
              'still','while','after','before','first','then','him','her','them'}

    words = text.split()
    total_w = sum(draw.textlength(w + ' ', font=font) for w in words)
    x = max(10, (width - total_w) / 2)
    color_idx = 0
    y = 25

    for word in words:
        clean = word.lower().rstrip('!?.,:...💼🎯💰📈⚡☕💎🏆🎩👑💻🦈💵🌀⚖️🧠😤📊✍️🎓📞🔥')
        if clean in filler:
            color = 'white'
        else:
            color = word_colors[color_idx % len(word_colors)]
            color_idx += 1
        # Shadow
        draw.text((x + 2, y + 2), word + ' ', font=font, fill=(0, 0, 0, 220))
        draw.text((x, y), word + ' ', font=font, fill=color)
        x += draw.textlength(word + ' ', font=font)

    return img


@app.route('/download', methods=['POST'])
def download():
    clip_data = generate_clip_idea()
    query = clip_data['query']
    hook_lines = clip_data['hook']

    print(f"Query: {query}")
    print(f"Hook: {hook_lines}")

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
        # Line 1 = hook (shows immediately)
        line1_img = create_line_image(hook_lines[0])
        line1_path = os.path.join(out_dir, 'line1.png')
        line1_img.save(line1_path)

        # Line 2 = climax (fades in at 40% through the video)
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

        # ffmpeg: crop to 9:16, line1 shows from 0s, line2 fades in at 40% duration
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', filepath,
            '-i', music_path,
            '-i', line1_path,
            '-i', line2_path,
            '-filter_complex',
            # Crop to vertical
            '[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v];'
            # Line 1: visible from start
            '[v][2:v]overlay=0:30:enable=\'gte(t,0)\'[v1];'
            # Line 2: fades in at 40% of video with alpha fade
            '[3:v]fade=in:st=0:d=0.8:alpha=1[line2fade];'
            '[v1][line2fade]overlay=0:140:enable=\'gte(t,between(t,0,999)*0+lt(t,999))\':shortest=1[vt];'
            # Audio: lower original, boost music
            '[0:a]volume=0.12[va];'
            '[1:a]volume=0.65[music];'
            '[va][music]amix=inputs=2:duration=first[aout]',
            '-map', '[vt]',
            '-map', '[aout]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            '-preset', 'fast',
            output_path
        ]

        proc = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=180)
        
        # If complex filter failed, use simple fallback
        if not os.path.exists(output_path) or os.path.getsize(output_path) < 1000:
            ffmpeg_simple = [
                'ffmpeg', '-y',
                '-i', filepath,
                '-i', music_path,
                '-i', line1_path,
                '-i', line2_path,
                '-filter_complex',
                '[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v];'
                '[v][2:v]overlay=0:30[v1];'
                '[v1][3:v]overlay=0:145[vt];'
                '[0:a]volume=0.12[va];'
                '[1:a]volume=0.65[music];'
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
            return jsonify({'success': True, 'file_id': file_id, 'hook': hook_lines, 'query': query})
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
