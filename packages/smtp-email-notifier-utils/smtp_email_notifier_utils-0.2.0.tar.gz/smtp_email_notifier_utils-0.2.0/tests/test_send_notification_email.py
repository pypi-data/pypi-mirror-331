import os
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from smtp_email_notifier_utils.send_notification_email import main

@pytest.fixture
def runner():
    return CliRunner()

def test_main_success(runner):
    with patch("smtp_email_notifier_utils.send_notification_email.send_notification", return_value=True):
        result = runner.invoke(main, [
            "--recipient", "test@example.com",
            "--subject", "Test Subject",
            "--message", "Test Message",
            "--verbose"
        ])
        assert result.exit_code == 0
        assert "Notification sent successfully!" in result.output

def test_main_missing_recipient(runner):
    result = runner.invoke(main, [
        "--subject", "Test Subject",
        "--message", "Test Message",
        "--verbose"
    ])
    assert result.exit_code == 1
    assert "--recipient was not specified" in result.output

def test_main_missing_subject(runner):
    result = runner.invoke(main, [
        "--recipient", "test@example.com",
        "--message", "Test Message",
        "--verbose"
    ])
    assert result.exit_code == 1
    assert "--subject was not specified" in result.output

def test_main_missing_message(runner):
    result = runner.invoke(main, [
        "--recipient", "test@example.com",
        "--subject", "Test Subject",
        "--verbose"
    ])
    assert result.exit_code == 1
    assert "--message was not specified" in result.output

def test_main_create_outdir(runner):
    with patch("os.path.exists", return_value=False):
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            with patch("smtp_email_notifier_utils.send_notification_email.send_notification", return_value=True):
                result = runner.invoke(main, [
                    "--recipient", "test@example.com",
                    "--subject", "Test Subject",
                    "--message", "Test Message",
                    "--outdir", "/tmp/test_outdir",
                    "--verbose"
                ])
                assert result.exit_code == 0
                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
                assert "Created output directory '/tmp/test_outdir'" in result.output

def test_main_default_logfile(runner):
    with patch("smtp_email_notifier_utils.send_notification_email.send_notification", return_value=True):
        result = runner.invoke(main, [
            "--recipient", "test@example.com",
            "--subject", "Test Subject",
            "--message", "Test Message",
            "--verbose"
        ])
        assert result.exit_code == 0
        assert "--logfile was not specified and therefore was set to" in result.output

def test_main_failure(runner):
    with patch("smtp_email_notifier_utils.send_notification_email.send_notification", return_value=False):
        result = runner.invoke(main, [
            "--recipient", "test@example.com",
            "--subject", "Test Subject",
            "--message", "Test Message",
            "--verbose"
        ])
        assert result.exit_code == 0
        assert "Failed to send notification" in result.output
