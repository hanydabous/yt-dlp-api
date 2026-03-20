from flask import Flask, request, jsonify, send_file
import subprocess, os, tempfile, requests, random
from PIL import Image, ImageDraw, ImageFont
import json, base64

app = Flask(__name__)

BOT_TOKEN = "8708552965:AAHnIat8255nA-UqSi5KAha-fcFwOWWsib0"
CHAT_ID = "8388528228"
ANTHROPIC_KEY = os.environ.get("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", "")

MUSIC_TRACKS = [
    '/app/music1.mp3',
    '/app/music2.mp3',
    '/app/music3.mp3',
]

CLIP_IDS = [
    "1ipjyBMTGlam6PgvLtv2Atl8vmnfbG0UK",
    "1Hm9qjf9QBJ05yxe414qTFW_zFxsknadZ",
    "1rjBuyZWF0rT9aCr0Hql1XANwEs-RYzw1",
    "1oSiFUHlQypg-xyZ73lhLbYN89AWdmxEz",
    "1G_YW2d8H5Vd6-AVQti0Vgimrw7Fd0eVx",
    "1Wcryu1ylTZpUOTIA03N2TsfUUM84nHK7",
    "1JwC941HVUTHxMKe3ExBSHgjnNaozTMhk",
    "1C6aWqclsau8keBj1IDHrjAF_ruOQtwhA",
    "1sYGg0zzq50bod2_8y63PuQrtNZk8sDNp",
    "1GwpbLByFsxxbkwcO5A78V5p00pyKklhE",
    "1tN1xoO6C8A0M061qWd_c4TTIyZ3g00uN",
    "1RVZcq1vhWjyHK_MWTAXZ7jXvH6rqyOMc",
    "1BwmwTYP-mDouSd3uM24J79s7rj34IuVw",
    "1bq23T4b-N1irx3fMVw66uJ7z-NE98HHf",
    "1SkWFT3wKNJdW6iSwNMU_R8_IwSAGNEQ4",
    "1VnvB5WdZ6HrSfPi_yfV2V1GYwhZitrOO",
    "1MuDISJYL_r5haDnJ5EQEAmY1Non-s9s9",
    "1A_QcMChcu_SdaqGSJkjQ2W45hb26PL6r",
    "16Gvl5Y7-NrHVIpvtga1GSDE22mEA9GmA",
    "1BxGNfZ2CaG7emB7DGIxC2UrwCsdbYHf9",
    "1-Y_3mpQWSl4cgm_vFQaYswAmI1Rj2QeJ",
    "1eprPIzwGlnjTLs-Hb4kmQqWDJh_R8N4t",
    "15YcWnnAXnDc5Zqca_5dLSjA8XXfXhv__",
    "1lraugxY3Gt_F2F_Y18dUAM7FzfkU0QLx",
    "1F5AaW7PISkHEF78b3GdHn3UEM5C1b5TP",
    "19ie3YQPpL0vI_nsDPdK3uzkFP_EC3IfZ",
    "1CZg9qXSn6lhBu5LfVYpHfUdZaJJnmt6M",
    "1BRHJRtxYxSN4svW_J7zMTFT3EvEtFaye",
    "1yWoLs_P1GdY0Km5TfDVOBY6Ymrs6FXWC",
    "1gfipusj5doO-si6EdkK2fpddKCVQtdM1",
    "15pDSFExEl_UtRwf8jpA77T6-9o7T2Fxb",
    "1QrbTS1BduTX_WWtNKCco5qUIKcjyIQgn",
    "1kYsTEfUOsYHCcn64o0yZxLjnTr5-zkd2",
    "1-gRpq_aJmBUnFWAF1d0OG7AI-IHgny2T",
    "1lr2BeulKVUJn8lVMAWLHnKbkowMZpzCu",
    "1GrItgtaqThwE0jKt1mI9se29-KMAL2Pz",
    "1YPC13xMk3K_w1jWYyj3CMBdT_IjAaWaq",
    "19crntgfV33p_nVbexcw_txyYbdYl9i1L",
    "1Mf7CBE7mkgmlCCq1dvgTTrvD7ChApQjV",
    "1fOYZCnUZ0ZKwWxWSTNv2VpovqSDY6LL0",
    "1l1QSAyy1pByQSo6v-uuVrDEM7AG3UIRG",
    "1kAE6qSesJYFxZnCnmQ04V4UChoUY5XaS",
    "1zJLAmbiLrTKR7gbvtTqpDjxtKWgv7fw5",
    "1-dQya0U-TCTjNs3J8-1Fp2MbB1R1EVFI",
    "1Zs8mQg0YGWdrExdUDTBwW2ur2RTolgWC",
    "1OAVaLU1C0chXTbJEcwomqipH4qJwIyJ9",
]

VIDEO_STORE = {}

OVERLAY_HEIGHT = 170
VIDEO_HEIGHT = 1110


def download_gdrive_file(file_id, out_dir):
    output_path = os.path.join(out_dir, f'{file_id}.mp4')
    try:
        result = subprocess.run([
            'gdown', f'https://drive.google.com/uc?id={file_id}&confirm=t',
            '-O', output_path, '--quiet'
        ], capture_output=True, timeout=180)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            return output_path
    except Exception as e:
        print(f"gdown error: {e}")
    return None


def get_thumbnail_frame(filepath, out_dir):
    frame_path = os.path.join(out_dir, 'frame.jpg')
    subprocess.run([
        'ffmpeg', '-y', '-ss', '3', '-i', filepath,
        '-vframes', '1', '-q:v', '2', frame_path
    ], capture_output=True, timeout=15)
    return frame_path if os.path.exists(frame_path) else None


def generate_hook(filepath, out_dir, file_id):
    try:
        frame_path = get_thumbnail_frame(filepath, out_dir)
        if frame_path and ANTHROPIC_KEY:
            with open(frame_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode()

            prompt = """You are creating a viral YouTube Short exactly like @biz.surgeon.

STEP 1 - Look at this frame and identify EXACTLY:
- Setting (car dealership, office, street, restaurant, gym, casino, courtroom, hotel, warehouse, etc)
- Characters (man in suit, athlete, couple, boss, salesman, woman, etc)
- What is literally happening (negotiating, arguing, celebrating, being rejected, making a deal, driving, counting money, etc)
- Emotion (confident, shocked, determined, nervous, powerful, angry, calm, etc)

STEP 2 - Write a 2-line hook that DIRECTLY matches what you see:
- Line 1 = describes EXACTLY what is happening in the scene (ends with "...")
- Line 2 = the business/money/life lesson from that exact scene (ends with emoji)

RULES:
- Hook MUST match the visual scene
- Car dealership → cars/wealth/deals
- Boardroom/office → business/power/negotiation
- Warehouse/storage → building wealth quietly
- Street/outdoor → hustle/grind/success
- Luxury setting → wealth/status/achievement
- Capitalize Every Word, max 8 words per line

EXAMPLES:
Car dealership, man in sports car: "He Walked In And Chose The Best..." / "Money Was Never The Issue! 💰"
Two suits negotiating outside: "He Made The Offer They Couldn't Refuse..." / "That's How Real Deals Are Made! 🤝"
Woman entering boardroom: "She Walked In Like She Owned It..." / "Because She Actually Did! 👑"
Man alone counting cash: "While They Were Sleeping..." / "He Was Already Counting! 💵"
Tech startup pitch meeting: "He Pitched The Idea No One Believed..." / "Until It Made Him A Billionaire! 💻"

Respond ONLY with valid JSON:
{"hook": ["Line one setup...", "Line two lesson! 💰"]}"""

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
                    "messages": [{
                        "role": "user",
                        "content": [
                            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_data}},
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
        print(f"Hook error: {e}")

    fallbacks = [
        ["He Didn't Ask For The Deal...", "He Made Them Offer It! 💼"],
        ["They Underestimated Him...", "Until It Was Too Late! ⚡"],
        ["While Everyone Panicked...", "He Was Already Positioning! 📈"],
        ["The Smartest Move In The Room...", "Was Playing Dumb! 🧠"],
        ["He Lost It All Once...", "And Built It Back Bigger! 🔥"],
        ["They Came To Shut Him Down...", "He Left With The Contract! 🤝"],
    ]
    return random.choice(fallbacks)


def create_overlay_image(hook_lines, width=720, height=OVERLAY_HEIGHT):
    img = Image.new('RGB', (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font_name = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 28)
        font_handle = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 22)
        font_hook = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
    except:
        font_name = ImageFont.load_default()
        font_handle = font_name
        font_hook = font_name

    logo_size = 58
    logo_x, logo_y = 12, 8
    try:
        logo = Image.open('/app/logo.png').convert('RGBA')
        logo = logo.resize((logo_size, logo_size))
        mask = Image.new('L', (logo_size, logo_size), 0)
        from PIL import ImageDraw as ID
        md = ID.Draw(mask)
        md.ellipse((0, 0, logo_size, logo_size), fill=255)
        logo.putalpha(mask)
        draw.ellipse((logo_x-2, logo_y-2, logo_x+logo_size+2, logo_y+logo_size+2), outline='#E1306C', width=2)
        img.paste(logo, (logo_x, logo_y), logo)
    except Exception as e:
        print(f"Logo error: {e}")

    name_x = logo_x + logo_size + 12
    draw.text((name_x, logo_y + 5), "MillionDollarScenes™", font=font_name, fill='white')
    cw = draw.textlength("MillionDollarScenes™", font=font_name)
    draw.text((name_x + cw + 6, logo_y + 5), "✓", font=font_name, fill='#1DA1F2')
    draw.text((name_x, logo_y + 35), "@MillionDollarScenes", font=font_handle, fill=(170, 170, 170))

    word_colors = ['#FF4444', '#FFD700', '#44DDFF', '#FF8C00', '#44FF88']
    filler = {'the','a','an','in','of','to','and','but','or','for','with','at','by',
              'from','is','it','he','she','they','his','her','their','was','were',
              'be','been','as','on','up','had','has','not','no','its','into','until',
              'still','while','after','before','first','then','him','them','always',
              'never','ever','just','all','this','that','too'}

    y_pos = 82
    for line in hook_lines:
        words = line.split()
        total_w = sum(draw.textlength(w + ' ', font=font_hook) for w in words)
        x = max(8, (width - total_w) / 2)
        color_idx = 0
        for word in words:
            clean = word.lower().rstrip('!?.,...💼🎯💰📈⚡☕💎🏆🎩👑💻🦈💵🌀⚖️🧠😤📊🔥🤝🫡😏🃏🚗')
            color = 'white' if clean in filler else word_colors[color_idx % len(word_colors)]
            if clean not in filler:
                color_idx += 1
            draw.text((x+2, y_pos+2), word+' ', font=font_hook, fill=(0, 0, 0))
            draw.text((x, y_pos), word+' ', font=font_hook, fill=color)
            x += draw.textlength(word+' ', font=font_hook)
        y_pos += 44

    return img


def send_telegram_notification(video_path, hook_lines, youtube_url=''):
    """Send video to Telegram as notification only - no buttons"""
    try:
        caption = '\n'.join(hook_lines)
        msg = f"✅ Posted to YouTube!\n\n{caption}"
        if youtube_url:
            msg += f"\n\n🔗 {youtube_url}"

        with open(video_path, 'rb') as f:
            requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendVideo',
                data={
                    'chat_id': CHAT_ID,
                    'caption': msg,
                },
                files={'video': ('clip.mp4', f, 'video/mp4')},
                timeout=120
            )
    except Exception as e:
        print(f"Telegram notification error: {e}")


@app.route('/download', methods=['POST'])
def download():
    out_dir = tempfile.mkdtemp()
    file_id = random.choice(CLIP_IDS)
    print(f"Downloading: {file_id}")

    filepath = download_gdrive_file(file_id, out_dir)
    if not filepath:
        return jsonify({'error': 'Failed to download'}), 400

    try:
        hook_lines = generate_hook(filepath, out_dir, file_id)
        print(f"Hook: {hook_lines}")

        overlay_img = create_overlay_image(hook_lines)
        overlay_path = os.path.join(out_dir, 'overlay.png')
        overlay_img.save(overlay_path)

        music_path = random.choice(MUSIC_TRACKS)
        output_path = os.path.join(out_dir, 'final.mp4')

        ffmpeg_cmd = [
            'ffmpeg', '-y',
            '-i', filepath,
            '-i', music_path,
            '-i', overlay_path,
            '-filter_complex',
            f'[0:v]scale=720:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,'
            f'pad=720:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:black[vid];'
            f'[2:v]scale=720:{OVERLAY_HEIGHT}[top];'
            f'[top][vid]vstack=inputs=2[vt];'
            '[0:a]volume=0.75[va];'
            '[1:a]volume=0.25[music];'
            '[va][music]amix=inputs=2:duration=first[aout]',
            '-map', '[vt]',
            '-map', '[aout]',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            '-preset', 'ultrafast',
            '-crf', '28',
            '-fs', '45M',
            output_path
        ]

        proc = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=180)
        print(f"FFmpeg: {proc.returncode}")
        if proc.returncode != 0:
            print(f"FFmpeg stderr: {proc.stderr[-500:]}")

        final_path = output_path if os.path.exists(output_path) and os.path.getsize(output_path) > 10000 else filepath
        print(f"Final size: {os.path.getsize(final_path)}")

        for p in [filepath, overlay_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except: pass

        return jsonify({
            'success': True,
            'hook': hook_lines,
            'video_path': final_path
        })

    except Exception as e:
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/notify', methods=['POST'])
def notify():
    """Called by n8n after YouTube upload to send Telegram notification"""
    data = request.json or {}
    video_path = data.get('video_path', '')
    hook = data.get('hook', [])
    youtube_url = data.get('youtube_url', '')

    if video_path and os.path.exists(video_path):
        send_telegram_notification(video_path, hook, youtube_url)
        try: os.remove(video_path)
        except: pass

    return jsonify({'success': True})


@app.route('/get_video', methods=['GET'])
def get_video():
    path = request.args.get('path', '')
    if path and os.path.exists(path):
        return send_file(path, mimetype='video/mp4')
    return 'Not found', 404


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
