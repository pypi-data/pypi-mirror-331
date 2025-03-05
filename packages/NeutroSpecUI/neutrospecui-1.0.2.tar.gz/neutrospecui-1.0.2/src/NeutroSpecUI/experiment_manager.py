import json, dataclasses
from typing import TYPE_CHECKING, cast

from PySide6.QtWidgets import QTabWidget, QFileDialog

from NeutroSpecUI.experimental_setup import ExperimentalSetup
from NeutroSpecUI.plot import PlotButtons

if TYPE_CHECKING:
    from NeutroSpecUI.main_window import NeutroSpecWindow


class ExperimentManager(QTabWidget):
    def __init__(self, window: "NeutroSpecWindow", parent=None) -> None:
        super().__init__(parent)
        self.main_window = window

        self.plot_btn_switch = PlotButtons(self.main_window)
        self.main_window.addRightWidget(self.plot_btn_switch)

    def add_experiment(self, exp: ExperimentalSetup) -> None:
        self.addTab(exp, exp.name)
        self.plot_btn_switch.idClicked.connect(exp.plot.setCurrentIndex)

    def create_empty_experiment(self, name: str) -> ExperimentalSetup:
        exp = ExperimentalSetup(window=self.main_window, name=name)
        self.add_experiment(exp)
        return exp

    def remove_experiment(self, exp: ExperimentalSetup) -> None:
        self.removeTab(self.indexOf(exp))
        exp.deleteLater()

    def get_experiments(self) -> list[ExperimentalSetup]:
        return [cast(ExperimentalSetup, self.widget(i)) for i in range(self.count())]

    def clear(self) -> None:
        for exp in self.get_experiments():
            self.removeTab(self.indexOf(exp))
            exp.deleteLater()

    def update_plot_layout(self) -> None:
        for exp in self.get_experiments():
            exp.plot.update_plot_layout()

    def save_dialog(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save File",
            dir="",  # TODO: remember last directory
            filter="JSON Files (*.json)",
        )

        if not file_name:
            print("No file loaded")  # TODO: Show error message as a dialog
            return

        self.save(file_name)

    def save(self, file_name: str) -> None:
        with open(file_name, "w") as file:
            if not file_name.endswith(".json"):
                file_name += ".json"
            json.dump(self.to_dict(), file, indent=4, cls=EnhancedJSONEncoder)
            self.main_window.recent_files_menu.add_file_to_recent(file_name)
            print("File created in path:", file_name)

    def load_dialog(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Load File",
            dir="",  # TODO: remember last directory
            filter="JSON Files (*.json)",
        )

        if not file_name:
            print("No file loaded")  # TODO: Show error message as a dialog
            return

        self.load(file_name)

    def load(self, file_name: str) -> None:
        # TODO: warning message if there are unsaved changes
        with open(file_name, "r") as file:
            data = json.load(file)
            self.main_window.recent_files_menu.add_file_to_recent(file_name)
            self.from_dict(data)

    def to_dict(self) -> dict:
        return {
            "experimental_setups": [exp.to_dict() for exp in self.get_experiments()]
        }

    def from_dict(self, data: dict) -> None:
        self.clear()
        for exp_data in data["experimental_setups"]:
            exp = self.create_empty_experiment(exp_data["name"])
            exp.from_dict(exp_data)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)  # type: ignore
        return super().default(o)
