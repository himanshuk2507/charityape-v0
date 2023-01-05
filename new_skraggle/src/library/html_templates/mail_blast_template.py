from src.library.html_templates.base_template import HTMLTemplate


class MailBlastTemplate(HTMLTemplate):
    def __init__(self):
        file_path = HTMLTemplate.templates_folder_path()/'mail_blast.html'
        super().__init__(file_path=file_path)

    def render(self, email_body: str = None):
        return super().render(
            email_body=email_body
        )