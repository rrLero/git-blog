# -*- coding: utf-8 -*-


class Textovka:
    def __init__(self):
        self.english = {"message": "message", "commit": "my commit message",
                        "author": "author", "name": "name", "email": "email"}

    def get_text(self, param):
        return self.english[param]
