from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests, random
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

PROXY = "http://hrwmqwzu:aznd3fx6nczr@45.61.118.112:5809"
BOT_TOKEN = "8708552965:AAHnIat8255nA-UqSi5KAha-fcFwOWWsib0"
CHAT_ID = "8388528228"

MUSIC_TRACKS = [
    "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3",
    "https://cdn.pixabay.com/audio/2022/01/18/audio_d0c6ff1bab.mp3",
    "https://cdn.pixabay.com/audio/2021/11/13/audio_cb4f5da9a6.mp3",
]

CLIPS = [
    {
        "query": "Suits Harvey Specter you dont send a message scene clip",
        "hook": ["He Didn't Negotiate The Price", "He Negotiated The Power! 💼"]
    },
    {
        "query": "Suits Harvey closer best I can do scene",
        "hook": ["The Best Lawyers Don't Win In Court", "They Win Before It Starts! ⚖️"]
    },
    {
        "query": "Suits Mike Ross genius memory scene",
        "hook": ["He Used His Mind As", "His Only Weapon! 🧠"]
    },
    {
        "query": "Mad Men Don Draper Carousel pitch scene",
        "hook": ["He Didn't Sell A Product", "He Sold A Feeling! 🎯"]
    },
    {
        "query": "Mad Men Don Draper this is not the future pitch",
        "hook": ["They Came To Fire Him", "He Left With The Deal! 🤝"]
    },
    {
        "query": "Wolf of Wall Street sell me this pen scene",
        "hook": ["Create The Need First", "Then Offer The Solution! 💰"]
    },
    {
        "query": "Wolf of Wall Street Jordan Belfort motivational speech",
        "hook": ["He Lost Everything Twice", "And Still Built An Empire! 🔥"]
    },
    {
        "query": "Billions Bobby Axelrod I am the best scene",
        "hook": ["He Never Asked For Permission", "He Asked For Forgiveness After! 📈"]
    },
    {
        "query": "Billions Chuck Rhoades courtroom speech",
        "hook": ["The Room Went Silent", "The Moment He Walked In! 🏛️"]
    },
    {
        "query": "Silicon Valley Richard Hendricks compression algorithm pitch",
        "hook": ["They Laughed At The Idea", "Until It Was Worth Billions! 💻"]
    },
    {
        "query": "Succession Logan Roy business meeting scene",
        "hook": ["He Built An Empire", "By Trusting No One! 👑"]
    },
    {
        "query": "Breaking Bad Walter White I am the danger scene",
        "hook": ["The Moment He Stopped Being", "A Victim And Became The Boss! ⚡"]
    },
    {
        "query": "Breaking Bad Walter I am the one who knocks",
        "hook": ["He Didn't Ask For Respect", "He Demanded It! 😤"]
    },
    {
        "query": "Moneyball Peter Brand statistics scene",
        "hook": ["Everyone Saw Players", "He Saw Market Inefficiencies! 📊"]
    },
    {
        "query": "Moneyball Billy Beane we're gonna change the game",
        "hook": ["They Said It Was Impossible", "Until He Made It The Standard! 🏆"]
    },
    {
        "query": "The Social Network Eduardo Saverin diluted shares scene",
        "hook": ["He Signed The Paper Without Reading", "And Lost It All! ✍️"]
    },
    {
        "query": "The Social Network Mark Zuckerberg deposition scene",
        "hook": ["The Smartest Person In The Room", "Never Has To Say It! 🎓"]
    },
    {
        "query": "Glengarry Glen Ross Alec Baldwin coffee is for closers",
        "hook": ["He Came To Motivate Them", "But Only The Strong Survived! ☕"]
    },
    {
        "query": "Wall Street Gordon Gekko greed is good speech",
        "hook": ["He Turned Greed Into", "A Business Philosophy! 💎"]
    },
    {
        "query": "Wall Street Gordon Gekko lunch is for wimps",
        "hook": ["While They Rested", "He Was Already Winning! ⏱️"]
    },
    {
        "query": "Entourage Ari Gold phone call negotiation scene",
        "hook": ["He Closed The Deal", "Before They Hung Up! 📞"]
    },
    {
        "query": "Shark Tank best pitch ever investor deal",
        "hook": ["She Walked In Nervous", "And Left A Partner! 🦈"]
    },
    {
        "query": "Jerry Maguire show me the money scene",
        "hook": ["He Had One Client Left", "And Made Him A Legend! 💵"]
    },
    {
        "query": "Ozark Marty Byrde money laundering explanation scene",
        "hook": ["He Turned A Problem", "Into A Business Model! 🌀"]
    },
    {
        "query": "Peaky Blinders Tommy Shelby business deal scene",
        "hook": ["He Always Made An Offer", "They Couldn't Refuse! 🎩"]
    },
]

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
            clean = word.lower().rstrip('!?.,:🎯💼⚖️🧠💰🔥📈🏛️💻👑⚡😤📊🏆✍️🎓☕💎⏱️📞🦈💵🌀🎩')
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
    clip_data = random.choice(CLIPS)
    query = clip_data['query']
    hook_lines = clip_data['hook']

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
