
import unittest
from unittest.mock import patch

from notification_agent import process_notification


class TestNotificationAgent(unittest.TestCase):

    def test_high_priority_rule(self):
        result = process_notification(
            "Your examination starts tomorrow"
        )

        self.assertEqual(result["importance"], "HIGH")
        self.assertEqual(result["source"], "User priority rules")

    def test_low_priority_rule(self):
        result = process_notification(
            "A new promotion starts tonight"
        )

        self.assertEqual(result["importance"], "LOW")
        self.assertEqual(result["source"], "User priority rules")

    @patch(
        "notification_agent.classify_importance",
        return_value=("MEDIUM", 0.85, 0.2)
    )
    @patch(
        "notification_agent.classify_category",
        return_value=("Shopping", 0.85)
    )
    def test_local_ai_decision(self, mock_category, mock_importance):
        result = process_notification(
            "The courier collected your parcel"
        )

        self.assertEqual(result["category"], "Shopping")
        self.assertEqual(result["importance"], "MEDIUM")
        self.assertEqual(result["source"], "Local importance AI")
        mock_category.assert_called_once()
        mock_importance.assert_called_once()

    @patch(
        "notification_agent.classify_importance",
        return_value=("HIGH", 0.20, 0.01)
    )
    @patch(
        "notification_agent.classify_category",
        return_value=("Education", 0.20)
    )
    def test_low_confidence_fallback(self, mock_category, mock_importance):
        result = process_notification(
            "An unfamiliar message with no priority keyword"
        )

        self.assertEqual(result["importance"], "UNKNOWN")
        self.assertEqual(result["source"], "Local importance AI")
        mock_category.assert_called_once()
        mock_importance.assert_called_once()

    @patch("notification_agent.classify_category")
    def test_empty_notification(self, mock_classifier):
        result = process_notification("   ")

        self.assertEqual(result["category"], "Unknown")
        self.assertEqual(result["importance"], "UNKNOWN")
        mock_classifier.assert_not_called()

    @patch("notification_agent.classify_importance")
    @patch(
        "notification_agent.classify_category",
        return_value=("Education", 0.9),
    )
    def test_priority_skips_importance_model(self, mock_category, mock_importance):
        result = process_notification(
            "Your assignment deadline is tomorrow"
        )

        self.assertEqual(result["importance"], "HIGH")
        mock_category.assert_called_once()
        mock_importance.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
