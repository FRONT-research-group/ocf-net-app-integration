import threading
import httpx
import uvicorn
from fastapi import FastAPI, Request
import time

HOST, PORT = "127.0.0.1", 8004   # Localhost only
ENDPOINT = "/receive"

app = FastAPI()

@app.post(ENDPOINT)
async def receive(request: Request):
    payload = await request.json()
    print(f"[Server] Received: {payload}")
    return {"echo": payload, "server_time": time.strftime("%H:%M:%S")}


def start_server():
    uvicorn.run(
        app,
        host=HOST,   # Only accessible from local machine
        port=PORT,
        log_level="info",
    )


def send_manual(payload):
    payload = {"notificationDestination": "http://{HOST}:{PORT}{ENDPOINT}".format(HOST=HOST,PORT=PORT), **payload}
    url = "http://127.0.0.1:8001/location"
    resp = httpx.post(url, json=payload)
    print("[Client] Response:", resp.json())


if __name__ == "__main__":
    # Run FastAPI server in background thread
    threading.Thread(target=start_server, daemon=True).start()
    time.sleep(1)

    print("Local server running (127.0.0.1 only).")
    print("Type a message and press Enter to send it. Ctrl+C to exit.")
    try:
        while True:
            msg = input("Message> ")
            payload = {"msisdn": msg}
            send_manual(payload)
    except KeyboardInterrupt:
        print("\n[Main] Exiting.")
