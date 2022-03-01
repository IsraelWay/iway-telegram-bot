#  Author: Ilya Polotsky (ipolo.box@gmail.com). Copyright (c) 2022.
class DetailedResponse:
    def __init__(self, result, message, payload=None):
        self.result = result
        self.message = message
        self.payload = payload
