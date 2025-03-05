from typing import cast

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QWidget
from PySide6.QtCore import QEventLoop, QSettings, Signal, QCoreApplication

QCoreApplication.setOrganizationName("NeutroSpecUI")
QCoreApplication.setApplicationName("NeutroSpecUI")

settings = QSettings()


class RecentFilesMenu(QMenu):
    load_file = Signal(str)

    def __init__(
        self,
        key: str | None = None,
        parent: QWidget | None = None,
        MAX_RECENT_FILES: int = 10,
    ):
        super().__init__(parent)
        self.setObjectName(f"{key}FilesMenu")

        self.name = key
        self.MAX_RECENT_FILES = MAX_RECENT_FILES
        self.loop = QEventLoop()
        self.selected_file: str | None = None

        self._STORAGE_KEY = f"files/recent-{self.name}" if self.name else "files/recent"

        self.update_items()

    def update_items(self) -> None:
        self.clear()

        file_names = self.get_recent_files()

        for file_name in file_names:
            action = QAction(file_name, self)
            action.triggered.connect(
                lambda checked, item=file_name: self.item_selected(item)
            )
            self.addAction(action)

        self.addSeparator()

        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.clear_recent_files)
        self.addAction(clear_action)

    def item_selected(self, file_name: str) -> None:
        self.load_file.emit(file_name)

    def add_file_to_recent(self, file_name: str) -> None:
        recent_files = cast(list[str], settings.value(self._STORAGE_KEY, [], type=list))

        # Remove old entries of the same file
        if file_name in recent_files:
            recent_files.remove(file_name)

        # Save the new file as the most recent
        recent_files.insert(0, file_name)

        # Limit the number of recent files
        recent_files = recent_files[: self.MAX_RECENT_FILES]

        settings.setValue(self._STORAGE_KEY, recent_files)
        self.update_items()

    def get_recent_files(self) -> list[str]:
        recent_files = settings.value(self._STORAGE_KEY, [], type=list)
        return cast(list[str], recent_files)  # cast to list[str] to avoid type error

    def clear_recent_files(self) -> None:
        settings.setValue(self._STORAGE_KEY, [])
        self.update_items()

    def set_recent_files(self, files: list[str]) -> None:
        files = files[: self.MAX_RECENT_FILES]
        settings.setValue(self._STORAGE_KEY, files)
        self.update_items()
