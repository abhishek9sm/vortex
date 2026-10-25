"""Loopback-only HTTP bridge between the React frontend and local SLM."""

import csv
import json
import os
import tempfile
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import RLock
from urllib.parse import urlsplit

from feedback_manager import FEEDBACK_FILE, save_feedback
from notification_agent import PREFERENCES_PATH, process_notification

HOST = "127.0.0.1"
PORT = 8765
MAX_BODY_BYTES = 64 * 1024
VALID_CATEGORIES = {
    "Education",
    "Security",
    "Personal",
    "Shopping",
    "Promotion",
    "UNKNOWN",
}
VALID_IMPORTANCES = {"HIGH", "MEDIUM", "LOW", "UNKNOWN"}
PREFERENCES_LOCK = RLock()


def read_preferences():
    with PREFERENCES_PATH.open("r", encoding="utf-8") as file:
        preferences = json.load(file)
    if not isinstance(preferences, dict) or not isinstance(
        preferences.get("priorities"), dict
    ):
        raise ValueError("User preferences must contain a priorities object.")
    return preferences


def save_preferences(preferences):
    preference_path = Path(PREFERENCES_PATH)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=preference_path.parent,
            prefix=f".{preference_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            json.dump(preferences, file, indent=2)
            file.write("\n")
        os.replace(temporary_path, preference_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def normalized_category(value):
    if value == "Unknown":
        return "UNKNOWN"
    return value


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "BuzzKillLocal/1.0"

    def do_GET(self):
        path = urlsplit(self.path).path
        try:
            if path == "/api/health":
                self._send_json(200, {"status": "ok"})
            elif path == "/api/keywords":
                with PREFERENCES_LOCK:
                    priorities = read_preferences()["priorities"]
                self._send_json(
                    200,
                    {"keywords": priorities.get("HIGH", [])},
                )
            elif path == "/api/feedback":
                self._send_json(200, {"feedback": self._read_feedback()})
            else:
                self._send_json(404, {"error": "Endpoint not found."})
        except (OSError, ValueError, json.JSONDecodeError) as error:
            self._send_json(500, {"error": f"Local data error: {error}"})

    def do_POST(self):
        path = urlsplit(self.path).path
        body = self._read_json_body()
        if body is None:
            return
        if path == "/api/classify":
            self._classify(body)
        elif path == "/api/feedback":
            self._save_feedback(body)
        else:
            self._send_json(404, {"error": "Endpoint not found."})

    def do_PUT(self):
        if urlsplit(self.path).path != "/api/keywords":
            self._send_json(404, {"error": "Endpoint not found."})
            return
        body = self._read_json_body()
        if body is None:
            return
        keywords = body.get("keywords")
        if (
            not isinstance(keywords, list)
            or len(keywords) > 200
            or not all(
                isinstance(keyword, str)
                and 0 < len(keyword.strip()) <= 100
                for keyword in keywords
            )
        ):
            self._send_json(400, {"error": "Keywords must be non-empty strings."})
            return

        unique_keywords = []
        seen = set()
        for keyword in keywords:
            clean_keyword = keyword.strip()
            folded = clean_keyword.casefold()
            if folded not in seen:
                seen.add(folded)
                unique_keywords.append(clean_keyword)

        try:
            with PREFERENCES_LOCK:
                preferences = read_preferences()
                preferences["priorities"]["HIGH"] = unique_keywords
                save_preferences(preferences)
            self._send_json(200, {"saved": True, "keywords": unique_keywords})
        except (OSError, ValueError, json.JSONDecodeError) as error:
            self._send_json(500, {"error": f"Could not save keywords: {error}"})

    def _classify(self, body):
        text = body.get("text")
        if not isinstance(text, str) or not text.strip() or len(text) > 20_000:
            self._send_json(
                400,
                {"error": "Notification text must contain 1–20000 characters."},
            )
            return
        try:
            result = process_notification(text.strip())
            category = normalized_category(result["category"])
            importance = result["importance"]
            if category not in VALID_CATEGORIES or importance not in VALID_IMPORTANCES:
                raise ValueError("The classifier returned an unsupported label.")
            confidence = result.get("confidence")
            if confidence is None:
                confidence = result.get("category_confidence")
            confidence = 0.0 if confidence is None else float(confidence)
            if not 0.0 <= confidence <= 1.0:
                raise ValueError("The classifier returned invalid confidence.")

            self._send_json(
                200,
                {
                    "id": f"notification-{uuid.uuid4()}",
                    "text": text.strip(),
                    "category": category,
                    "importance": importance,
                    "confidence": confidence,
                    "explanation": result["reason"],
                    "keywordOverride": (
                        result["source"] == "User priority rules"
                        and importance == "HIGH"
                    ),
                    "corrected": False,
                },
            )
        except (KeyError, TypeError, ValueError) as error:
            self._send_json(500, {"error": f"Classification failed: {error}"})
        except Exception:
            self._send_json(500, {"error": "Local model classification failed."})

    def _save_feedback(self, body):
        text = body.get("notificationText")
        predicted_category = normalized_category(body.get("predictedCategory"))
        corrected_category = body.get("correctedCategory")
        predicted_importance = body.get("predictedImportance")
        corrected_importance = body.get("correctedImportance")
        if (
            not isinstance(text, str)
            or not text.strip()
            or len(text) > 20_000
            or predicted_category not in VALID_CATEGORIES
            or corrected_category not in VALID_CATEGORIES
            or predicted_importance not in VALID_IMPORTANCES
            or corrected_importance not in VALID_IMPORTANCES
        ):
            self._send_json(400, {"error": "Feedback contains invalid values."})
            return
        try:
            with PREFERENCES_LOCK:
                save_feedback(
                    text=text.strip(),
                    predicted_category=predicted_category,
                    corrected_category=corrected_category,
                    predicted_importance=predicted_importance,
                    corrected_importance=corrected_importance,
                )
            self._send_json(200, {"saved": True})
        except OSError as error:
            self._send_json(500, {"error": f"Could not save feedback: {error}"})

    @staticmethod
    def _read_feedback():
        if not FEEDBACK_FILE.exists():
            return []
        with FEEDBACK_FILE.open("r", newline="", encoding="utf-8") as file:
            return [
                {
                    "notificationText": row.get("notification_text", ""),
                    "correctedCategory": normalized_category(
                        row.get("corrected_category", "UNKNOWN")
                    ),
                    "correctedImportance": row.get(
                        "corrected_importance", "UNKNOWN"
                    ),
                }
                for row in csv.DictReader(file)
            ]

    def _read_json_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "Invalid Content-Length."})
            return None
        if content_length <= 0 or content_length > MAX_BODY_BYTES:
            self._send_json(413, {"error": "Request body is empty or too large."})
            return None
        try:
            body = json.loads(self.rfile.read(content_length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "Request body must be valid JSON."})
            return None
        if not isinstance(body, dict):
            self._send_json(400, {"error": "Request body must be a JSON object."})
            return None
        return body

    def _send_json(self, status, payload):
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format_string, *args):
        print(f"[local-api] {format_string % args}")


def main():
    server = ThreadingHTTPServer((HOST, PORT), ApiHandler)
    print(f"BuzzKill local SLM API listening at http://{HOST}:{PORT}")
    print("This server only accepts loopback connections.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local SLM API.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
