from flask import Flask, request, jsonify, send_file
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

VIDEO_STORE = {}


def download_gdrive_file(file_id, out_dir):
    output_path = os.path.join(out_dir, f'{file_id}.mp4')
    try:
        result = subprocess.run([
            'gdown', f'https://drive.google.com/uc?id={file_id}&confirm=t',
            '-O', output_path, '--quiet'
        ], capture_output=True, timeout=180)
