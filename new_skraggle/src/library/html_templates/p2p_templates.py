from src.library.html_templates.base_template import HTMLTemplate


class OnP2PCreatedTemplate(HTMLTemplate):
    def __init__(self):
        file_path = HTMLTemplate.templates_folder_path()/'on_p2p_created.html'
        super().__init__(file_path=file_path)

    def render(self, **kwargs):
        return super().render(**kwargs)