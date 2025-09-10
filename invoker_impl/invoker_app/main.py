
import requests

from invoker_app.config import get_settings

settings = get_settings()


def load_token(file_path: str) -> str:
    with open(file_path, "r", encoding='utf-8') as f:
        return f.read().strip()

def main():
    url = "http://127.0.0.1:8000/provider-app/v1/hello"

    token = load_token(settings.TOKEN_PATH) if settings.TOKEN_PATH else ""

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url,timeout=10, headers=headers)

    if response.status_code == 200:
        print("Server says:", response.json()["message"])
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    main()