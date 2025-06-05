from fastapi import FastAPI, Request, Header, HTTPException
import subprocess
import uuid
import os
import json
import requests

app = FastAPI()

RENDER_DIR = "videos"
os.makedirs(RENDER_DIR, exist_ok=True)

def download_file(url, suffix):
    local_filename = os.path.join(RENDER_DIR, f"{uuid.uuid4()}.{suffix}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

@app.post("/render")
async def render_video(
    request: Request,
    x_api_key: str = Header(None)
):
    if x_api_key != os.getenv("RENDER_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid or missing API key")

    data = await request.json()

    video_id = str(uuid.uuid4())
    output_path = f"{RENDER_DIR}/{video_id}.mp4"

    with open(f"{RENDER_DIR}/{video_id}_config.json", "w") as f:
        json.dump(data, f, indent=2)

    temp_files = []
    video_inputs = ""
    for idx, video in enumerate(data['videos']):
        local_video = download_file(video['src'], "mp4")
        video_inputs += f"-i {local_video} "
        temp_files.append(local_video)

    local_audio = download_file(data['audio_url'], "mp3")
    video_inputs += f"-i {local_audio} "
    temp_files.append(local_audio)

    command = f"ffmpeg -probesize 100M -analyzeduration 100M {video_inputs} -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac -preset veryfast {output_path}"

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": str(e)}
    finally:
        for temp in temp_files:
            if os.path.exists(temp):
                os.remove(temp)

    public_url = f"https://getaway-geek-render.onrender.com/{output_path}"

    return {
        "status": "success",
        "url": public_url
    }