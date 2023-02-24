import smtplib
from socket import gaierror

from tgbot.backoffice.definitions import DEFAULT_EMAIL_TEMPLATE
from tgbot.gfvgbo.secrets import SMTP_SERVER, SMTP_USER, SMTP_PASSWORD, EMAIL_SENDER

from tgbot.telegram_bot.log_utils import email_logger as logger

SMTP_PORT = 25


def send_email(receiver, email_subject, email_content, sender=EMAIL_SENDER, email_template=DEFAULT_EMAIL_TEMPLATE):

    if SMTP_SERVER is None:
        return

    message = email_template.format(email_subject, receiver, sender, email_content)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_SENDER, receiver, message)

        # tell the script to report if your message was sent or which errors need to be fixed
        logger.info(f'email sent to {receiver}')
    except (gaierror, ConnectionRefusedError):
        logger.error('Failed to connect to the server. Bad connection settings?')
    except smtplib.SMTPServerDisconnected:
        logger.error('Failed to connect to the server. Wrong user/password?')
    except smtplib.SMTPException as e:
        logger.error('SMTP error occurred: ' + str(e))


if __name__ == '__main__':
    send_email(EMAIL_SENDER, "test email", "this is a test")


