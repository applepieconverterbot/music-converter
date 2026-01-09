from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os
import time
import subprocess

app = Flask(__name__)

# --- 🎨 MODERN DARK UI (HTML/CSS) ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SonicStream | TV Mode</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --bg: #0f0f0f; --card: #1c1c1c; --accent: #ff0033; --text: #ffffff; --input: #252525; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Outfit', sans-serif; background-color: var(--bg); color: var(--text); height: 100vh; display: flex; justify-content: center; align-items: center; overflow: hidden; background-image: radial-gradient(circle at 10% 20%, rgba(255, 0, 51, 0.1) 0%, transparent 20%); }
        .container { background: rgba(28, 28, 28, 0.8); backdrop-filter: blur(20px); width: 100%; max-width: 500px; padding: 40px; border-radius: 24px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); text-align: center; }
        .header h1 { font-size: 28px; font-weight: 700; } .header span { color: var(--accent); }
        .input-group { margin-bottom: 20px; text-align: left; }
        label { display: block; margin-bottom: 8px; font-size: 12px; font-weight: 700; color: #aaa; text-transform: uppercase; }
        input, select { width: 100%; padding: 16px; background: var(--input); border: 1px solid #333; border-radius: 12px; color: white; font-size: 15px; outline: none; }
        button { width: 100%; padding: 18px; background: var(--accent); color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 700; cursor: pointer; margin-top: 10px; }
        #loader { display: none; position: absolute; inset: 0; background: rgba(15, 15, 15, 0.95); z-index: 100; flex-direction: column; justify-content: center; align-items: center; border-radius: 24px; }
        .spinner { width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1); border-top: 3px solid var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 15px; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div id="loader"><div class="spinner"></div><h3>Converting...</h3><p style="font-size: 13px; color: #666;">Using TV Protocol...</p></div>
        <div class="header"><h1>Sonic<span>Stream</span></h1><p style="color:#888; font-size:14px; margin-bottom: 30px;">TV Client Mode</p></div>
        <form action="/convert" method="post" onsubmit="document.getElementById('loader').style.display='flex'">
            <div class="input-group">
                <label>YouTube Link</label>
                <input type="text" name="url" placeholder="https://music.youtube.com/..." required autocomplete="off">
            </div>
            <div class="input-group">
                <label>Format</label>
                <select name="format">
                    <optgroup label="Best Quality"><option value="m4a">M4A (AAC)</option><option value="mp3">MP3</option><option value="flac">FLAC</option></optgroup>
                    <optgroup label="Retro"><option value="amr">AMR</option><option value="gsm">GSM</option><option value="8svx">8SVX</option></optgroup>
                </select>
            </div>
            <button type="submit">DOWNLOAD</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('url')
    fmt = request.form.get('format')
    
    timestamp = int(time.time())
    temp_wav = f"/tmp/{timestamp}_temp.wav"
    final_output = f"/tmp/{timestamp}.{fmt}"

    # 🚀 CONFIGURATION: TV MODE 🚀
    # We DO NOT use cookies.txt here because it triggers the "IP Mismatch" flag.
    # Instead, we force yt-dlp to pretend it is a Smart TV (tv_embedded).
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'/tmp/{timestamp}_temp.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        
        # 👇 THE SECRET SAUCE 👇
        # This tells YouTube: "I am a TV, I can't sign in, just give me the video."
        'extractor_args': {
            'youtube': {
                'player_client': ['tv_embedded', 'android_creator'],
                'player_skip': ['web', 'ios', 'android']
            }
        },
        
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}],
    }

    try:
        # 1. Download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio_converted')
            clean_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c in ' -_']).strip()

        # 2. Convert (FFmpeg)
        ffmpeg_cmd = ['ffmpeg', '-y', '-i', temp_wav]

        if fmt == 'mp3': ffmpeg_cmd.extend(['-b:a', '320k'])
        elif fmt in ['aac', 'm4a']: ffmpeg_cmd.extend(['-c:a', 'aac', '-b:a', '256k'])
        elif fmt == 'amr': ffmpeg_cmd.extend(['-ar', '8000', '-ac', '1', '-c:a', 'libopencore_amrnb'])
        elif fmt == 'gsm': ffmpeg_cmd.extend(['-ar', '8000', '-ac', '1', '-c:a', 'gsm'])
        elif fmt == '8svx': ffmpeg_cmd.extend(['-c:a', 'pcm_s8', '-f', 'iff'])
        
        ffmpeg_cmd.append(final_output)
        subprocess.run(ffmpeg_cmd, check=True)

        return send_file(final_output, as_attachment=True, download_name=f"{clean_title}.{fmt}")

    except Exception as e:
        error_msg = str(e)
        return f"""
        <body style="background:#0f0f0f; color:#fff; font-family:sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; text-align:center;">
            <div style="background:#1c1c1c; padding:40px; border-radius:20px; border:1px solid #333; max-width:500px;">
                <h2 style="color:#ff0033; margin-bottom:15px;">⚠️ Conversion Failed</h2>
                <p style="color:#ccc; margin-bottom:20px;">{error_msg}</p>
                <div style="background:#222; padding:10px; border-radius:5px; font-size:12px; color:#888; text-align:left;">
                    <strong>Tip:</strong> If this persists, the Render IP address is hard-banned by YouTube. 
                    The only free fix is to run this code on <b>Google Colab</b> or locally on your PC.
                </div>
                <br>
                <button onclick="history.back()" style="background:#333; color:white; border:none; padding:12px 24px; border-radius:8px; cursor:pointer;">Go Back</button>
            </div>
        </body>
        """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
