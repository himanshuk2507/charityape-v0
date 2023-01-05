from src.library.html_templates.base_template import HTMLTemplate


class OnAdminSignupTemplate(HTMLTemplate):
    def __init__(self):
        file_path = HTMLTemplate.templates_folder_path()/'on_admin_signup.html'
        super().__init__(file_path)

    def render(self, name=None, otp=None, validity='10 minutes'):
        if not name or not otp:
            raise '`name` and `otp` are required in OnAdminSignupTemplate::render'
        return super().render(
            name=name, otp=otp, validity=validity
        )
        

class ForgotPasswordMailTemplate(HTMLTemplate):
    def __init__(self):
        file_path = HTMLTemplate.templates_folder_path()/'forgot_password_email.html'
        super().__init__(file_path)

    def render(self, name=None, otp=None, validity='10 minutes'):
        if not name or not otp:
            raise '`name` and `otp` are required in ForgotPasswordMailTemplate::render'
        return super().render(
            name=name, otp=otp, validity=validity
        )
        


class WelcomeToSkraggleMailTemplate(HTMLTemplate):
    def __init__(self):
        file_path = HTMLTemplate.templates_folder_path()/'on_admin_verified.html'
        super().__init__(file_path)

    def render(self, name=None):
        if not name:
            raise '`name` is required in WelcomeToSkraggleMailTemplate::render'
        return super().render(
            name=name
        )
        