# KindHeart — Gmail OTP & Password Reset Reference

## Scope
Implement only email-based OTP and password reset using Gmail SMTP.

## Requirements

### Gmail
- Use a dedicated Gmail account for KindHeart.
- Use Gmail SMTP.
- Use a Gmail App Password.
- Never hard-code credentials.

### Environment variables
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
```

### Email OTP
- Generate a 6-digit OTP.
- Store it securely with expiry.
- OTP expires after a short configurable period.
- OTP is single-use.
- Add resend cooldown.
- Limit verification attempts.
- Mark email as verified after successful verification.

### Password Reset
- Use Django's existing password-reset mechanism where possible.
- Send password-reset email through the Gmail email backend.
- Password-reset tokens must expire and be single-use.
- Never send passwords by email.

### Code structure
- Reuse the existing KindHeart authentication/user system.
- Reuse existing models/services when possible.
- Create a reusable email/OTP service only if one does not already exist.
- Do not create duplicate authentication systems.

### Security
- Keep secrets only in `.env`.
- Do not commit `.env`.
- Do not expose OTPs or credentials in logs.
- Do not modify unrelated modules.

## Testing
Test:
1. Gmail SMTP connection.
2. Send email OTP.
3. Verify valid OTP.
4. Reject expired/invalid OTP.
5. Resend OTP.
6. Forgot-password email.
7. Password reset with valid token.
8. Reject expired/used reset token.
