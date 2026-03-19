from flask import Flask, request, jsonify
import subprocess, os, tempfile, requests, random
from PIL import Image, ImageDraw, ImageFont
import json, base64

app = Flask(__name__)

BOT_TOKEN = "8708552965:AAHnIat8255nA-UqSi5KAha-fcFwOWWsib0"
CHAT_ID = "8388528228"
ANTHROPIC_KEY = os.environ.get("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", "")

MUSIC_TRACKS = [
    "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3",
    "https://cdn.pixabay.com/audio/2022/01/18/audio_d0c6ff1bab.mp3",
    "https://cdn.pixabay.com/audio/2021/11/13/audio_cb4f5da9a6.mp3",
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


def download_gdrive_file(file_id, out_dir):
    output_path = os.path.join(out_dir, f'{file_id}.mp4')
    try:
        result = subprocess.run([
            'gdown', f'https://drive.google.com/uc?id={file_id}&confirm=t',
            '-O', output_path, '--quiet'
        ], capture_output=True, timeout=180)
        print(f"gdown returncode: {result.returncode}")
        print(f"gdown stderr: {result.stderr[-300:]}")
        if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            print(f"Downloaded: {os.path.getsize(output_path)} bytes")
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

            prompt = """You are creating a viral YouTube Short in the style of @biz.surgeon.

Look at this frame from a business/money/success video clip. Write a 2-line hook.

- Line 1 = SETUP (ends with "...")
- Line 2 = PUNCHLINE with business lesson (ends with emoji)
- Capitalize Every Word, max 8 words per line
- Examples:
  "He Didn't Negotiate The Price..." / "He Negotiated The Power! 💼"
  "They Laughed At The Idea..." / "Until It Was Worth Billions! 💻"
  "While Everyone Panicked..." / "He Was Already Positioning! 📈"
  "Always Looks Easy Money..." / "Until The Work Actually Begins! 🌀"
  "She Showed Kindness In Business..." / "And It Always Paid Off! 🤝"

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
        ["She Walked In With Nothing...", "And Left A Partner! 🦈"],
        ["He Never Asked For Permission...", "He Asked For Forgiveness After! 👑"],
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
              'never','ever','just','all','this','that','too'}

    words = text.split()
    total_w = sum(draw.textlength(w + ' ', font=font) for w in words)
    x = max(10, (width - total_w) / 2)
    color_idx = 0
    y = 28

    for word in words:
        clean = word.lower().rstrip('!?.,...💼🎯💰📈⚡☕💎🏆🎩👑💻🦈💵🌀⚖️🧠😤📊🔥🤝🫡😏')
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
    out_dir = tempfile.mkdtemp()
    file_id = random.choice(CLIP_IDS)
    print(f"Downloading file ID: {file_id}")

    filepath = download_gdrive_file(file_id, out_dir)
    if not filepath:
        return jsonify({'error': 'Failed to download from Google Drive'}), 400

    try:
        hook_lines = generate_hook(filepath, out_dir, file_id)
        print(f"Hook: {hook_lines}")

        line1_img = create_line_image(hook_lines[0])
        line1_path = os.path.join(out_dir, 'line1.png')
        line1_img.save(line1_path)

        line2_img = create_line_image(hook_lines[1])
        line2_path = os.path.join(out_dir, 'line2.png')
        line2_img.save(line2_path)

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
            '-preset', 'ultrafast',
            output_path
        ]

        proc = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=180)
        print(f"FFmpeg code: {proc.returncode}")
        if proc.returncode != 0:
            print(f"FFmpeg error: {proc.stderr[-500:]}")

        final_path = output_path if os.path.exists(output_path) and os.path.getsize(output_path) > 10000 else filepath
        print(f"Sending: {final_path}, size: {os.path.getsize(final_path)}")

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
        print(f"Exception: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
