import os
from email.header import Header
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr

import aiosmtplib
import jinja2
from loguru import logger

from .. import config

template_loader = jinja2.FileSystemLoader(
    searchpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
)
templateEnv = jinja2.Environment(
    loader=template_loader,
)


async def send_email(template_name: str, subject: str, to: str, **kwargs) -> None:
    if not config.smtp.from_email:
        logger.warning('No smtp server has been configured')
        return
    template = templateEnv.get_template(template_name)
    message = MIMEText(template.render(kwargs), 'html')
    display_name, address = parseaddr(config.smtp.from_email)
    message['From'] = formataddr((str(Header(display_name, 'utf-8')), address))
    message['To'] = formataddr(('', to), 'utf-8')
    message['Subject'] = str(Header(subject, 'utf-8'))
    await aiosmtplib.send(
        message,
        hostname=config.smtp.server,
        username=config.smtp.user,
        password=config.smtp.password,
        port=int(config.smtp.port),
        use_tls=config.smtp.use_tls,
    )


async def send_reset_password(to: str, url: str) -> None:
    try:
        await send_email('email/reset_password.html', 'Reset password', to, url=url)
    except Exception as e:
        logger.exception(e)
        raise


async def send_password_changed(to: str) -> None:
    try:
        await send_email('email/password_changed.html', 'Password changed', to)
    except Exception as e:
        logger.exception(e)


async def send_new_login(to: str, ip: str) -> None:
    try:
        await send_email('email/new_login.html', 'New login', to, ip=ip)
    except Exception as e:
        logger.exception(e)
