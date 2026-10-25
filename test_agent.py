
import unittest
from unittest.mock import patch

from notification_agent import process_notification


class TestNotificationAgent(unittest.TestCase):

    def test_high_priority_rule(self):
        result = process_notification(
            "Your examination starts tomorrow"
        )

        self.assertEqual(result["importance"], "HIGH")
        self.assertEqual(result["source"], "Priority rules")

    def test_low_priority_rule(self):
        result = process_notification(
            "Flash sale ends tonight"
        )

        self.assertEqual(result["importance"], "LOW")
        self.assertEqual(result["source"], "Priority rules")

    @patch(
        "notification_agent.classify_notification",
        return_value=("Shopping", 0.85)
    )
    def test_local_ai_decision(self, mock_classifier):
        result = process_notification(
            "The courier collected your parcel"
        )

        self.assertEqual(result["category"], "Shopping")
        self.assertEqual(result["importance"], "MEDIUM")
        self.assertEqual(result["source"], "Local AI")
        mock_classifier.assert_called_once()

    @patch(
        "notification_agent.classify_notification",
        return_value=("Education", 0.20)
    )
    def test_low_confidence_fallback(self, mock_classifier):
        result = process_notification(
            "An unfamiliar message with no priority keyword"
        )

        self.assertEqual(result["importance"], "UNKNOWN")
        self.assertEqual(result["source"], "Local AI + fallback")

    @patch("notification_agent.classify_notification")
    def test_empty_notification(self, mock_classifier):
        result = process_notification("   ")

        self.assertEqual(result["category"], "Unknown")
        self.assertEqual(result["importance"], "UNKNOWN")
        mock_classifier.assert_not_called()

    @patch("notification_agent.classify_notification")
    def test_priority_skips_ai(self, mock_classifier):
        result = process_notification(
            "Your assignment deadline is tomorrow"
        )

        self.assertEqual(result["importance"], "HIGH")
        mock_classifier.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
