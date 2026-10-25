import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from unittest.mock import patch

import local_api


class LocalApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = local_api.ThreadingHTTPServer(
            ("127.0.0.1", 0),
            local_api.ApiHandler,
        )
        cls.server_thread = threading.Thread(
            target=cls.server.serve_forever,
            daemon=True,
        )
        cls.server_thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.server_thread.join(timeout=2)

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.preferences_path = self.directory / "user_preferences.json"
        self.feedback_path = self.directory / "feedback.csv"
        self.preferences_path.write_text(
            json.dumps({"priorities": {"HIGH": ["urgent"], "MEDIUM": [], "LOW": []}}),
            encoding="utf-8",
        )
        self.preferences_patch = patch.object(
            local_api,
            "PREFERENCES_PATH",
            self.preferences_path,
        )
        self.feedback_patch = patch.object(local_api, "FEEDBACK_FILE", self.feedback_path)
        self.preferences_patch.start()
        self.feedback_patch.start()

    def tearDown(self):
        self.preferences_patch.stop()
        self.feedback_patch.stop()
        self.temp_dir.cleanup()

    def test_health_and_keywords_are_available(self):
        self.assertEqual({"status": "ok"}, self.get("/api/health"))
        self.assertEqual({"keywords": ["urgent"]}, self.get("/api/keywords"))

    def test_keywords_update_preferences_used_by_classifier(self):
        result = self.send(
            "PUT",
            "/api/keywords",
            {"keywords": [" OTP ", "otp", "bank"]},
        )

        self.assertEqual(["OTP", "bank"], result["keywords"])
        saved = json.loads(self.preferences_path.read_text(encoding="utf-8"))
        self.assertEqual(["OTP", "bank"], saved["priorities"]["HIGH"])
        self.assertEqual([], saved["priorities"]["MEDIUM"])

    def test_classification_is_mapped_to_frontend_shape(self):
        result = {
            "category": "Unknown",
            "importance": "UNKNOWN",
            "source": "Local AI",
            "confidence": None,
            "category_confidence": 0.7,
            "reason": "Not enough signal.",
        }
        with patch.object(local_api, "process_notification", return_value=result):
            response = self.send("POST", "/api/classify", {"text": "A short message"})

        self.assertEqual("UNKNOWN", response["category"])
        self.assertEqual("UNKNOWN", response["importance"])
        self.assertEqual(0.7, response["confidence"])
        self.assertEqual("Not enough signal.", response["explanation"])
        self.assertFalse(response["keywordOverride"])

    def test_empty_classification_input_is_rejected(self):
        with self.assertRaises(HTTPError) as response:
            self.send("POST", "/api/classify", {"text": " "})
        self.assertEqual(400, response.exception.code)

    def test_feedback_is_saved_and_read_back(self):
        with patch.object(local_api, "save_feedback") as save_feedback:
            response = self.send(
                "POST",
                "/api/feedback",
                {
                    "notificationText": "Bank message",
                    "predictedCategory": "Security",
                    "predictedImportance": "MEDIUM",
                    "correctedCategory": "Security",
                    "correctedImportance": "HIGH",
                },
            )
        self.assertTrue(response["saved"])
        save_feedback.assert_called_once()

        self.feedback_path.write_text(
            "notification_text,predicted_category,corrected_category,"
            "predicted_importance,corrected_importance,timestamp\n"
            "Bank message,Security,Security,MEDIUM,HIGH,2026-10-25T12:00:00\n",
            encoding="utf-8",
        )
        self.assertEqual(
            [
                {
                    "notificationText": "Bank message",
                    "correctedCategory": "Security",
                    "correctedImportance": "HIGH",
                }
            ],
            self.get("/api/feedback")["feedback"],
        )

    def get(self, path):
        with urlopen(self.base_url + path, timeout=3) as response:
            return json.loads(response.read())

    def send(self, method, path, body):
        request = Request(
            self.base_url + path,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method=method,
        )
        with urlopen(request, timeout=3) as response:
            return json.loads(response.read())


if __name__ == "__main__":
    unittest.main()
