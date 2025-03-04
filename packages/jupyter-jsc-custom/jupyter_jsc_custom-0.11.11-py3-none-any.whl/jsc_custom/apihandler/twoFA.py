import json
import os
import uuid
from datetime import datetime
from datetime import timedelta

from jupyterhub.handlers import default_handlers
from jupyterhub.handlers.base import BaseHandler
from jupyterhub.utils import url_path_join
from tornado import web

from .misc import NoXSRFCheckAPIHandler
from .utils.twoFA_mail import send_user_mail
from .utils.twoFA_mail import send_user_mail_delete
from .utils.twoFA_orm import TwoFAORM
from .utils.twoFA_unity import add_user_2fa
from .utils.twoFA_unity import delete_user_2fa


class TwoFAAPIHandler(NoXSRFCheckAPIHandler):
    """
    With this APIHandler JupyterHub offers a workflow to
    activate 2FA at Unity-JSC.

    Workflow:
        Login Required
        Client visits ../handler/page_handlers.TwoFAHandler
        Click on "Request 2FA", sends POST request to .TWOFAAPIHandler
        -> JupyterHub sends creates an unique code, which is valid for x hours and sends it via email to the user
        Client clicks on link in email (confirms user has access to the mail address)
        -> Visits .TwoFACodeHandler
        -> validate unique code
        -> ssh call to Unity-JSC, triggering a bash script which activates 2FA for this user
        -> User is asked to logout / login again
        -> User has to configure its TOTP app

    Deletion Workflow:
        Login required
        Click on "Remove 2FA"
        -> ssh call to Unity-JSC, triggering a bash script which deactivates 2FA for this user
    """

    def check_xsrf_cookie(self):
        pass

    @web.authenticated
    async def post(self):
        user = self.current_user
        username = user.name.replace("_at_", "@")
        uuidcode = uuid.uuid4().hex
        self.log.info(
            f"{username} - uuidcode={uuidcode} - action=request2fa - will receive an email with a generated code"
        )
        send2fa_config_path = os.environ.get("SEND2FA_CONFIG_PATH", None)
        if not send2fa_config_path:
            self.log.error(
                f"{username} - Please define $SEND2FA_CONFIG_PATH environment variable."
            )
            send2fa_config = {}
        else:
            with open(send2fa_config_path, "r") as f:
                send2fa_config = json.load(f)

        code = uuid.uuid4().hex
        generated = datetime.now()
        unit = ""
        value = ""
        if (
            send2fa_config.get("timedelta", {}).get("unit", "default") == "default"
            or send2fa_config.get("timedelta", {}).get("unit", "default") == "hours"
        ):
            expired = generated + timedelta(
                hours=send2fa_config.get("timedelta", {}).get("value", 2)
            )
            unit = "hours"
            value = send2fa_config.get("timedelta", {}).get("value", 2)
        elif send2fa_config.get("timedelta", {}).get("unit", "default") == "days":
            expired = generated + timedelta(
                days=send2fa_config.get("timedelta", {}).get("value", 1)
            )
            unit = "days"
            value = send2fa_config.get("timedelta", {}).get("value", 1)
        elif send2fa_config.get("timedelta", {}).get("unit", "default") == "minutes":
            expired = generated + timedelta(
                minutes=send2fa_config.get("timedelta", {}).get("value", 30)
            )
            unit = "minutes"
            value = send2fa_config.get("timedelta", {}).get("value", 30)
        else:
            expired = generated + timedelta(hours=2)
            unit = "hours"
            value = 2
        generated_s = generated.strftime("%Y-%m-%d-%H:%M:%S")
        expired_s = expired.strftime("%Y-%m-%d-%H:%M:%S")

        twofa_orm = TwoFAORM.find(self.db, user_id=user.id)
        if twofa_orm is None:
            twofa_orm = TwoFAORM(
                user_id=user.id, code=code, generated=generated_s, expired=expired_s
            )
            self.db.add(twofa_orm)
        else:
            twofa_orm.code = code
            twofa_orm.generated = generated_s
            twofa_orm.expired = expired_s
        self.db.commit()

        url = "https://" + url_path_join(self.request.host, self.hub.base_url, "/")
        send_user_mail(username, code, unit, str(value), url)
        self.set_header("Content-Type", "text/plain")
        self.set_status(200)

    @web.authenticated
    async def delete(self):
        user = self.current_user
        username = user.name.replace("_at_", "@")
        if user:
            try:
                uuidcode = uuid.uuid4().hex
                self.log.info(
                    f"{username} - uuidcode={uuidcode} - action=delete2fa - Remove User from 2FA optional group"
                )

                self.log.debug(
                    f"{username} - uuidcode={uuidcode} - Delete user from group via ssh to Unity VM"
                )
                delete_user_2fa(username)

                self.log.debug(
                    f"{username} - uuidcode={uuidcode} - Send user a confirmation mail"
                )
                send_user_mail_delete(username)

                self.set_header("Content-Type", "text/plain")
                self.set_status(204)
            except:
                self.log.exception(f"{username} - Bugfix required")
                self.set_status(500)
                self.write(
                    "Something went wrong. Please contact support to deactivate two factor authentication."
                )
                self.flush()
        else:
            self.set_header("Content-Type", "text/plain")
            self.set_status(404)
            raise web.HTTPError(
                404,
                "User not found. Please logout, login and try again. If this does not help contact support.",
            )


class TwoFACodeHandler(BaseHandler):
    @web.authenticated
    async def get(self, code):
        uuidcode = uuid.uuid4().hex
        user = self.current_user
        username = user.name.replace("_at_", "@")
        self.log.info(
            f"{username} - uuidcode={uuidcode} - action=activate2fa".format(
                uuidcode, username
            )
        )

        result = TwoFAORM.validate_token(TwoFAORM, self.db, user.id, code)
        if result:
            self.db.delete(result)
            self.db.commit()

            expired_s = result.expired
            expired = datetime.strptime(expired_s, "%Y-%m-%d-%H:%M:%S")
            if expired > datetime.now():
                try:
                    self.log.debug(
                        f"{username} - uuidcode={uuidcode} - Add user to 2FA group in unity"
                    )
                    add_user_2fa(username)
                    code_success = True
                    code_header = "2FA activation successful"
                    code_text = "You'll be able to add a second factor the next time you log in."
                except:
                    self.log.exception(
                        f"{username} - uuidcode={uuidcode} - Unknown Error in Code2FA"
                    )
                    code_success = False
                    code_header = "2FA activation failed"
                    code_text = (
                        "Please contact support to activate 2-Factor Authentication."
                    )
            else:
                self.log.error(
                    "{} - uuidcode={} - Expired code. Now: {} - Expired: {}".format(
                        username,
                        uuidcode,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        expired.strftime("%Y-%m-%d %H:%M:%S"),
                    )
                )
                code_success = False
                code_header = "2FA activation failed"
                code_text = (
                    "The link is expired since {}. Please request a new one.".format(
                        expired.strftime("%Y-%m-%d %H:%M:%S")
                    )
                )
        else:
            self.log.error(
                f"{username} - uuidcode={uuidcode} - There is no such token {code}"
            )
            code_success = False
            code_header = "2FA activation failed"
            code_text = "Please contact support to activate 2-Factor Authentication."

        html = await self.render_template(
            "2FA.html",
            user=user,
            code=True,
            code_success=code_success,
            code_header=code_header,
            code_text=code_text,
        )
        self.finish(html)


default_handlers.append((r"/api/2FA", TwoFAAPIHandler))
default_handlers.append((r"/2FA/([^/]+)", TwoFACodeHandler))
