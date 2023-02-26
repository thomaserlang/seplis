import os
import aiosmtplib
import jinja2
from email.mime.text import MIMEText
from .. import config, logger

template_loader = jinja2.FileSystemLoader(searchpath=os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'templates'))
templateEnv = jinja2.Environment(
    loader=template_loader,
    auto_reload=config.data.debug,
)

async def send_email(template_name: str, subject: str, to: str, **kwargs):
    if not config.data.smtp.from_email:
        logger.warn('No smtp server has been configured')
        return
    template = templateEnv.get_template(template_name)
    message = MIMEText(template.render(kwargs), 'html')
    message["From"] = config.data.smtp.from_email
    message["To"] = to
    message["Subject"] = subject
    await aiosmtplib.send(
        message,
        hostname=config.data.smtp.server,
        username=config.data.smtp.user,
        password=config.data.smtp.password,
        port=int(config.data.smtp.port),
        use_tls=config.data.smtp.use_tls,
    )


async def send_reset_password(to: str, url: str):
    await send_email('email/reset_password.html', 'Reset password', to, url=url)


async def send_password_changed(to: str):
    await send_email('email/password_changed.html', 'Password changed', to)
