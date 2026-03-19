from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests, random
from PIL import Image, ImageDraw, ImageFont
import json

app = Flask(__name__)

PROXY = "http://hrwmqwzu:aznd3fx6nczr@45.61.118.112:5809"
BOT_TOKEN = "8708552965:AAHnIat8255nA-UqSi5KAha-fcFwOWWsib0"
CHAT_ID = "8388528228"
ANTHROPIC_KEY = "YOUR_ANTHROPIC_API_KEY"

MUSIC_TRACKS = [
    "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3",
    "https://cdn.pixabay.com/audio/2022/01/18/audio_d0c6ff1bab.mp3",
    "https://cdn.pixabay.com/audio/2021/11/13/audio_cb4f5da9a6.mp3",
]

FALLBACK_CLIPS = [
    {"query": "Suits Harvey Specter you dont send a message scene", "hook": ["He Didn't Negotiate The Price", "He Negotiated The Power! 💼"]},
    {"query": "Mad Men Don Draper Carousel pitch scene", "hook": ["He Didn't Sell A Product", "He Sold A Feeling! 🎯"]},
    {"query": "Wolf of Wall Street sell me this pen scene", "hook": ["Create The Need First", "Then Offer The Solution! 💰"]},
    {"query": "Billions Bobby Axelrod I am the best scene", "hook": ["He Never Asked For Permission", "He Asked For Forgiveness After! 📈"]},
    {"query": "Breaking Bad Walter White I am the danger scene", "hook": ["The Moment He Stopped Being", "A Victim And Became The Boss! ⚡"]},
    {"query": "Glengarry Glen Ross coffee is for closers speech", "hook": ["He Came To Motivate Them", "But Only The Strong Survived! ☕"]},
    {"query": "Wall Street Gordon Gekko greed is good speech", "hook": ["He Turned Greed Into", "A Business Philosophy! 💎"]},
    {"query": "Moneyball we're gonna change the game scene", "hook": ["They Said It Was Impossible", "Until He Made It The Standard! 🏆"]},
    {"query": "Peaky Blinders Tommy Shelby business deal scene", "hook": ["He Always Made An Offer", "They Couldn't Refuse! 🎩"]},
    {"query": "Succession Logan Roy boardroom scene", "hook": ["He Built An Empire", "By Trusting No One! 👑"]},
]

def generate_clip_idea():
    """Use Claude AI to generate a fresh business lesson clip idea"""
    try:
        prompt = """You are a viral YouTube Shorts creator. Generate ONE fresh idea for a business/money lesson clip.

The format must be:
- A specific famous TV show or movie SCENE to search for on YouTube (from shows like Suits, Mad Men, Breaking Bad, Billions, Succession, Peaky Blinders, Silicon Valley, The Social Network, Wolf of Wall Street, Glengarry Glen Ross, Wall Street, Moneyball, Entourage, Ozark, Shark Tank, Jerry Maguire, etc.)
- A 2-line business lesson hook text that connects the scene to a money/business/success lesson

The hook text style must match these examples exactly:
- "He Didn't Negotiate The Price / He Negotiated The Power! 💼"
- "They Laughed At The Idea / Until It Was Worth Billions! 💻"  
- "She Walked In With Nothing / And Left A Millionaire! 🦈"
- "He Turned Greed Into / A Business Philosophy! 💎"

Rules:
- Hook line 1: setup (what happened)
- Hook line 2: punchline/lesson with emoji
- Scene must be a SPECIFIC iconic moment, not generic
- Business/money/success/sales/negotiation angle always
- Never repeat obvious scenes — be creative and varied

Respond ONLY with valid JSON, no other text:
{
  "query": "specific scene search query for YouTube",
  "hook": ["Line one of hook", "Line two with emoji! 🔥"]
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
            # Strip markdown code fences if present
            text = text.replace('```json', '').replace('```', '').strip()
            idea = json.loads(text)
            if 'query' in idea and 'hook' in idea:
                return idea

    except Exception as e:
        print(f"Claude API error: {e}")

    # Fallback to hardcoded list
    return random.choice(FALLBACK_CLIPS)


def create_text_overlay(text_lines, width=1080, height=220):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 46)
    except:
        font = ImageFont.load_default()

    word_colors = ['#FF4444', '#FFD700', '#44DDFF', '#FF8C00', '#44FF88']
    filler = {'the','a','an','in','of','to','and','but','or','for','with','at','by',
              'from','is','it','he','she','they','his','her','their','was','were',
              'be','been','as','on','up','had','has','not','no','its','into'}

    y_pos = 20
    for line in text_lines:
        words = line.split()
        total_w = sum(draw.textlength(w + ' ', font=font) for w in words)
        x = max(0, (width - total_w) / 2)
        color_idx = 0
        for word in words:
            clean = word.lower().rstrip('!?.,:💼🎯💰📈⚡☕💎🏆🎩👑💻🦈💵🌀⚖️🧠😤📊✍️🎓📞🔥')
            if clean in filler:
                color = 'white'
            else:
                color = word_colors[color_idx % len(word_colors)]
                color_idx += 1
            draw.text((x + 2, y_pos + 2), word + ' ', font=font, fill=(0, 0, 0, 200))
            draw.text((x, y_pos), word + ' ', font=font, fill=color)
            x += draw.textlength(word + ' ', font=font)
        y_pos += 65

    return img


@app.route('/download', methods=['POST'])
def download():
    # Generate fresh idea using Claude AI
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
        overlay_img = create_text_overlay(hook_lines)
        overlay_path = os.path.join(out_dir, 'overlay.png')
        overlay_img.save(overlay_path)

        music_url = random.choice(MUSIC_TRACKS)
        music_path = os.path.join(out_dir, 'music.mp3')
        r = requests.get(music_url, timeout=30)
        with open(music_path, 'wb') as f:
            f.write(r.content)

        output_path = os.path.join(out_dir, 'final.mp4')
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', filepath,
            '-i', music_path,
            '-i', overlay_path,
            '-filter_complex',
            '[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v];'
            '[v][2:v]overlay=0:30[vt];'
            '[0:a]volume=0.15[va];'
            '[1:a]volume=0.6[music];'
            '[va][music]amix=inputs=2:duration=first[aout]',
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

        for p in [filepath, music_path, output_path, overlay_path]:
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
