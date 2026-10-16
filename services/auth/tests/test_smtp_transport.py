"""Exercise the actual verification sender's Django SMTP transport."""
from unittest import TestCase
from unittest.mock import patch
from django.test import override_settings
from users.email_service import SMTPEmailBackend


class SMTPTransportTests(TestCase):
    def test_encryption_modes(self):
        for implicit_ssl, port in [(False, 587), (True, 465)]:
            with self.subTest(port=port), override_settings(
                EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
                EMAIL_HOST="smtp.gmail.com", EMAIL_PORT=port,
                EMAIL_HOST_USER="sender@example.test", EMAIL_HOST_PASSWORD="test-app-password",
                EMAIL_FROM="sender@example.test", EMAIL_USE_TLS=not implicit_ssl,
                EMAIL_USE_SSL=implicit_ssl, EMAIL_TIMEOUT=20,
            ), patch("django.core.mail.backends.smtp.smtplib.SMTP") as plain, patch(
                "django.core.mail.backends.smtp.smtplib.SMTP_SSL"
            ) as encrypted:
                chosen = encrypted if implicit_ssl else plain
                unused = plain if implicit_ssl else encrypted
                chosen.return_value.sendmail.return_value = {}
                SMTPEmailBackend().send("recipient@example.test", "Verify", "<p>Verify</p>", "Verify")
                chosen.assert_called_once()
                unused.assert_not_called()
                chosen.return_value.login.assert_called_once_with("sender@example.test", "test-app-password")
                if implicit_ssl:
                    chosen.return_value.starttls.assert_not_called()
                else:
                    chosen.return_value.starttls.assert_called_once()
                chosen.return_value.sendmail.assert_called_once()

    def test_local_backend(self):
        from django.core import mail
        with override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
                               EMAIL_FROM="sender@example.test"):
            SMTPEmailBackend().send("recipient@example.test", "Verify", "<p>Verify</p>", "Verify")
            self.assertEqual(mail.outbox[-1].to, ["recipient@example.test"])
            self.assertEqual(mail.outbox[-1].body, "Verify")
            self.assertEqual(mail.outbox[-1].alternatives[0].mimetype, "text/html")
