from fastapi import FastAPI, Request
import subprocess
import uuid
import os
import json

app = FastAPI()

RENDER_DIR = "videos"
os.makedirs(RENDER_DIR, exist_ok=True)

@app.post("/render")
async def render_video(request: Request):
    data = await request.json()

    video_id = str(uuid.uuid4())
    output_path = f"{RENDER_DIR}/{video_id}.mp4"

    # Write incoming config for debugging/logging (optional)
    with open(f"{RENDER_DIR}/{video_id}_config.json", "w") as f:
        json.dump(data, f, indent=2)

    video_inputs = ""
    for idx, video in enumerate(data['videos']):
        video_inputs += f"-i {video['src']} "

    # Add background music
    video_inputs += f"-i {data['audio_url']} "

    # Simple FFmpeg command — customize as needed
    command = f"ffmpeg {video_inputs} -shortest -c:v libx264 -c:a aac -preset veryfast {output_path}"

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": str(e)}

    public_url = f"https://getaway-geek-render.onrender.com/{output_path}"

    return {
        "status": "success",
        "url": public_url
    }