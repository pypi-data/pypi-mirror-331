from typing import Type

from PySide6.QtWidgets import QApplication

from NeutroSpecUI.main_window import NeutroSpecWindow
from NeutroSpecUI.backends import Backend, BackendHandler
from NeutroSpecUI.backends.neutro import NeutroBackend


class NeutroApp(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend = BackendHandler(NeutroBackend)  # use NeutroBackend as default

    def load_backend(self, backend: Type[Backend]):
        self.backend.load_backend(backend)

    def start_neutro(self):
        self.window = NeutroSpecWindow()
        self.window.show()
        return super().exec()
