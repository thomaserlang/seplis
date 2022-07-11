import logging
from urllib.parse import urljoin
import good, aiosmtplib
import sqlalchemy as sa
from email.mime.text import MIMEText
from seplis.api.handlers import base
from seplis.api import exceptions, constants, models
from seplis.api.decorators import new_session, run_on_executor
from seplis import config
from datetime import datetime

class Handler(base.Handler):

    __schema__ = good.Schema({
        'key': str,
        'new_password': good.All(str, good.Length(min=6)),
    })

    __arguments_schema__ = good.Schema({
        'email': [str],
    })

    async def get(self):
        args = self.validate_arguments()
        user_id = await self.get_user_id(args['email'][0])
        if not user_id:
            self.set_status(204)
            return

        smtp = aiosmtplib.SMTP(
            hostname=config.data.smtp.server, 
            port=int(config.data.smtp.port),
            use_tls=config.data.smtp.use_tls, 
            loop=self.application.ioloop,
        )
        await smtp.connect()
        if config.data.smtp.user:
            await smtp.login(config.data.smtp.user, config.data.smtp.password)

        url = await self.create_reset_url(user_id)
        message = MIMEText('''
        <html>
        <body>
            Reset your SEPLIS password here: <a href="{0}">{0}</a>
        </body>
        </html>
        '''.format(url), 'html')
        message["From"] = config.data.smtp.from_email
        message["To"] = args['email'][0]
        message["Subject"] = "Reset password"
        await smtp.send_message(message)

        self.set_status(204)

    async def post(self):
        await self.reset()
        self.set_status(204)

    @run_on_executor
    def get_user_id(self, email):
        with new_session() as session:
            u = session.query(models.User.id).filter(
                models.User.email == email,
            ).first()
            if u:
                return u.id

    @run_on_executor
    def create_reset_url(self, user_id):
        with new_session() as session:
            r = models.Reset_password(
                user_id=user_id,
            )
            session.add(r)
            session.commit()
            return urljoin(config.data.web.url, f'/reset-password/{r.key}')

    @run_on_executor
    def reset(self):
        data = self.validate()        
        with new_session() as session:
            r = session.query(models.Reset_password.user_id).filter(
                models.Reset_password.key == data['key'],
                models.Reset_password.expires >= datetime.utcnow(),
            ).first()
            if not r:
                raise exceptions.Forbidden('Invalid reset key')
            session.query(models.Reset_password).filter(
                models.Reset_password.user_id == r.user_id,
            ).delete()
            user_id = r.user_id
            models.User.change_password(
                user_id=user_id,
                new_password=data['new_password'],
                session=session,
            )
            tokens = session.query(models.Token).filter(
                models.Token.user_id == user_id,
                sa.or_(
                    models.Token.expires >= datetime.utcnow(),
                    models.Token.expires == None,
                )
            ).all()
            for token in tokens:
                if token.token == self.access_token:
                    continue
                session.delete(token)
            session.commit()