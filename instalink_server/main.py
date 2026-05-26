from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
async def root():
    out = subprocess.run(["bash", "-c", "instantlink"], capture_output=True)
    return {"message": out.stderr.decode("utf-8")}
