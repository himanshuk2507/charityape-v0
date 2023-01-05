import os
from pathlib import Path
from jinja2 import Template

class HTMLTemplate:
    '''
    Creates a HTMLTemplate utility object that holds a pointer to a template.
    This allows for a standardised, modular, isolated way to create and render templates
    throughout the app. 
    The HTMLTemplate class also makes changing the underlying template engine trivial 
    as long as the public API is maintained.
    '''
    def __init__(self, file_path: str):
        self.file_path = file_path
        with open(file_path, 'r') as file:
            self.file = file.read()
        self.template = Template(self.file)

    def render(self, **kwargs):
        return self.template.render(
            **kwargs
        )

    @classmethod
    def templates_folder_path(cls):
        return Path(__file__).parent
        # return Path(__file__)/'src'/'library'/'html_templates'