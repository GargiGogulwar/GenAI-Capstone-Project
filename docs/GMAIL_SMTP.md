# Gmail verification emails

The Groq Compose configuration reads email settings from the root `.env`.
For Gmail, configure:

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
EMAIL_HOST_USER=your-address@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-google-app-password
EMAIL_FROM=your-address@gmail.com
```

Use a Google App Password, without the display spaces, rather than your normal
account password. Enable 2-Step Verification first, then create an App Password
at https://myaccount.google.com/apppasswords. Work or school account policies
can prevent this; a personal Gmail account is often simpler for a demo.
Never commit or share `.env`, and keep the password out of chat.

After the credentials are saved, recreate Identity:

```powershell
docker compose -f docker-compose.yml -f docker-compose.groq.yml up -d --no-deps --force-recreate --wait identity
```

Verify by using **Resend verification email** on your existing account, then
check the real recipient inbox and Spam folder. Emails previously captured by
MailHog do not get forwarded retroactively. Verification links still point to
`FRONTEND_URL`; localhost links work only on the machine running the project.

For local MailHog again, set `EMAIL_HOST=mailhog`, `EMAIL_PORT=1025`,
`EMAIL_USE_TLS=false`, `EMAIL_USE_SSL=false`, and clear `EMAIL_HOST_USER` and
`EMAIL_HOST_PASSWORD`, then recreate Identity.

Google references: [App Passwords](https://support.google.com/accounts/answer/185833)
and [Gmail SMTP settings](https://support.google.com/a/answer/176600).
