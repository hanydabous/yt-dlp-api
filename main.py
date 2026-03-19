from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests, random
from PIL import Image, ImageDraw, ImageFont
import textwrap

app = Flask(__name__)

PROXY = "http://hrwmqwzu:aznd3fx6nczr@45.61.118.112:5809"
BOT_TOKEN = "8708552965:AAHnIat8255nA-UqSi5KAha-fcFwOWWsib0"
CHAT_ID = "8388528228"

MUSIC_TRACKS = [
    "https://cdn.pixabay.com/audio/2022/10/14/audio_b43c3b5e38.mp3",
    "https://cdn.pixabay.com/audio/2023/03/09/audio_c0d2b85c39.mp3",
    "https://cdn.pixabay.com/audio/2022/08/02/audio_884fe92c21.mp3",
]

CLIPS = [
    {"query": "Suits Harvey Specter negotiation scene", "hook": ["He Closed The Deal", "Without Saying A Word! 🤝"]},
    {"query": "Silicon Valley pitch scene funding", "hook": ["They Needed To Fail First", "To Succeed! 😤"]},
    {"query": "Modern Family real estate sales scene", "hook": ["He Manipulated His Clients Into The Sale", "Without Even Realizing It! 😏"]},
    {"query": "The Office Michael Scott sales pitch", "hook": ["Sometimes The Worst Salesman", "Makes The Best Deal! 😂"]},
    {"query": "Wolf of Wall Street sales call scene", "hook": ["He Sold The Pen", "Before They Even Wanted It! 💰"]},
    {"query": "Mad Men Don Draper pitch client", "hook": ["They Didn't Buy The Product", "They Bought The Feeling! 🧠"]},
    {"query": "Shark Tank best deal pitch scene", "hook": ["She Walked In With Nothing", "And Left A Millionaire! 🦈"]},
    {"query": "Breaking Bad Walter White business deal", "hook": ["He Turned Nothing Into An Empire", "The Hard Way! 💎"]},
    {"query": "Billions Bobby Axelrod trading scene", "hook": ["While Everyone Panicked", "He Was Already Positioning! 📈"]},
    {"query": "Succession boardroom power scene", "hook": ["The Boardroom Is Just", "A Battlefield In Suits! ⚔️"]},
    {"query": "The Internship Google pitch scene", "hook": ["The Best Ideas Sound Crazy", "Until They Work! 💡"]},
    {"query": "Entourage Ari Gold negotiation", "hook": ["He Knew His Worth", "And Never Settled For Less! 🔥"]},
    {"query": "American Psycho business card scene", "hook": ["In Business The Packaging", "Is Part Of The Product! 🃏"]},
    {"query": "The Social Network Facebook pitch", "hook": ["They Laughed At The Idea", "Until It Was Worth Billions! 💻"]},
    {"query": "Jerry Maguire show me the money scene", "hook": ["Sometimes You Have To Ask", "For What You Deserve! 💵"]},
    {"query": "Moneyball negotiation baseball trade scene", "hook": ["The Real Edge Is Seeing", "What Others Ignore! 📊"]},
    {"query": "Glengarry Glen Ross sales motivation speech", "hook": ["Always Be Closing —", "The Rule That Never Changes! 🏆"]},
    {"query": "Scrubs Dr Cox lesson speech", "hook": ["They Gave Everything They Had", "And Still Got Nothing Back! 😤"]},
    {"query": "Parks Recreation Leslie Knope pitch", "hook": ["She Was Told No", "Until They Couldn't Say Anything Else! 💪"]},
    {"query": "Two and a Half Men Charlie Harper money", "hook": ["Easy Money Always Looks Easy", "Until The Work Actually Begins! 🌀"]},
]

def create_text_overlay(text_lines, width=1080, height=200):
    """Create a transparent PNG with styled colored text"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 44)
        font_small = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
    except:
        font_large = ImageFont.load_default()
        font_small = font_large

    colors = ['#FF4444', '#44FF44', '#FFD700', '#FF8C00', '#00BFFF']
    
    y_pos = 20
    for i, line in enumerate(text_lines):
        font = font_large if i == 0 else font_small
        words = line.split()
        
        # Calculate total line width to center it
        total_w = sum(draw.textlength(w + ' ', font=font) for w in words)
        x = (width - total_w) / 2
        
        for j, word in enumerate(words):
            # Alternate colors for key words, white for filler words
            filler = {'the', 'a', 'an', 'in', 'of', 'to', 'and', 'but', 'or', 'for', 'with', 'at', 'by', 'from', 'is', 'it', 'he', 'she', 'they'}
            if word.lower().rstrip('!?.,:') in filler:
                color = 'white'
            else:
                color = colors[j % len(colors)]
            
            # Draw shadow
            draw.text((x+2, y_pos+2), word + ' ', font=font, fill=(0, 0, 0, 180))
            # Draw text
            draw.text((x, y_pos), word + ' ', font=font, fill=color)
            x += draw.textlength(word + ' ', font=font)
        
        y_pos += 60
    
    return img

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    clip_data = random.choice(CLIPS)
    query = data.get('query', clip_data['query'])
    hook_lines = data.get('hook', clip_data['hook'])
    
    if isinstance(hook_lines, str):
        hook_lines = [hook_lines]

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
    lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip().endswith('.mp4')]

    if not lines:
        return jsonify({'error': 'No clip found', 'stderr': result.stderr[-2000:]}), 400

    filepath = lines[0]

    try:
        # Create text overlay image
        overlay_img = create_text_overlay(hook_lines)
        overlay_path = os.path.join(out_dir, 'overlay.png')
        overlay_img.save(overlay_path)

        # Download music
        music_url = random.choice(MUSIC_TRACKS)
        music_path = os.path.join(out_dir, 'music.mp3')
        music_resp = requests.get(music_url, timeout=30)
        with open(music_path, 'wb') as f:
            f.write(music_resp.content)

        # Crop to 9:16, overlay text image at top, mix music
        output_path = os.path.join(out_dir, 'final.mp4')
        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', filepath,
            '-i', music_path,
            '-i', overlay_path,
            '-filter_complex',
            '[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[v];'
            '[v][2:v]overlay=0:30[vt];'
            '[0:a]volume=1.0[va];'
            '[1:a]volume=0.35[music];'
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
            return jsonify({'error': 'Telegram send failed', 'details': tg.text}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
