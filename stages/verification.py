import base64
import re
import time
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from constant import client_id, client_secret, gmail_query

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = Path(__file__).resolve().parent.parent / "token.json"
OAUTH_PORT = 8080


def _get_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [f"http://localhost:{OAUTH_PORT}/"],
                }
            }
            flow = InstalledAppFlow.from_client_config(config, SCOPES)
            creds = flow.run_local_server(port=OAUTH_PORT)
        TOKEN_FILE.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _body_text(payload):
    """Extrai o texto de um payload do Gmail (recursivo)."""
    text = ""
    data = payload.get("body", {}).get("data")
    if data:
        text += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    for part in payload.get("parts", []):
        text += _body_text(part)
    return text


def get_security_code(timeout=90, interval=3, since_ms=None):
    """Espera o e-mail com o código chegar e devolve os 6 dígitos.

    since_ms: timestamp (ms) a partir do qual considerar e-mails; evita pegar
    um código antigo. Por padrão usa o momento da chamada.
    """
    service = _get_service()
    since_ms = since_ms or int(time.time() * 1000) - 5000
    deadline = time.time() + timeout

    while time.time() < deadline:
        res = service.users().messages().list(
            userId="me", q=gmail_query, maxResults=5
        ).execute()
        for ref in res.get("messages", []):
            msg = service.users().messages().get(
                userId="me", id=ref["id"], format="full"
            ).execute()
            if int(msg["internalDate"]) < since_ms:
                continue
            body = _body_text(msg["payload"]) or msg.get("snippet", "")
            match = re.search(r"\b(\d{6})\b", body)
            if match:
                return match.group(1)
        time.sleep(interval)

    raise TimeoutError("Código de verificação não chegou no e-mail a tempo.")
