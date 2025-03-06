import pytest
from unittest.mock import patch, MagicMock
from smtp_email_notifier_utils.notifier import send_notification

@patch("smtp_email_notifier_utils.notifier.smtplib.SMTP")
@patch("smtp_email_notifier_utils.notifier.MIMEText")
def test_send_notification_success(mock_mime_text, mock_smtp):
    # Arrange
    mock_mime_text.return_value = MagicMock()
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value

    # Act
    result = send_notification("test@example.com", "Test Subject", "Test Message")

    # Assert
    assert result is True
    mock_mime_text.assert_called_once_with("Test Message")
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with("your_email@example.com", "your_password")
    mock_smtp_instance.send_message.assert_called_once()

@patch("smtp_email_notifier_utils.notifier.smtplib.SMTP")
@patch("smtp_email_notifier_utils.notifier.MIMEText")
def test_send_notification_failure(mock_mime_text, mock_smtp):
    # Arrange
    mock_mime_text.return_value = MagicMock()
    mock_smtp_instance = mock_smtp.return_value.__enter__.return_value
    mock_smtp_instance.send_message.side_effect = Exception("SMTP error")

    # Act
    result = send_notification("test@example.com", "Test Subject", "Test Message")

    # Assert
    assert result is False
    mock_mime_text.assert_called_once_with("Test Message")
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with("your_email@example.com", "your_password")
    mock_smtp_instance.send_message.assert_called_once()
