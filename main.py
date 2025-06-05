from fastapi import FastAPI, Request, Header, HTTPException
import subprocess
import uuid
import os
import json

app = FastAPI()

RENDER_DIR = "videos"
os.makedirs(RENDER_DIR, exist_ok=True)

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

    video_inputs = ""
    for idx, video in enumerate(data['videos']):
        video_inputs += f"-thread_queue_size 512 -i {video['src']} "

    video_inputs += f"-thread_queue_size 512 -i {data['audio_url']} "

    command = f"ffmpeg -probesize 5000000 -analyzeduration 10000000 {video_inputs} -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac -preset veryfast {output_path}"

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": str(e)}

    public_url = f"https://getaway-geek-render.onrender.com/{output_path}"

    return {
        "status": "success",
        "url": public_url
    }