import dataclasses
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QLabel,
    QScrollArea,
    QMessageBox,
)
from PySide6.QtGui import QFontMetrics
from PySide6.QtCore import Signal, Qt

from NeutroSpecUI.material_widget import MaterialWidget
from NeutroSpecUI.material import Material, ExperimentData
from NeutroSpecUI.parameter import Parameter
from NeutroSpecUI.plot import PlotWidgetStacked
from NeutroSpecUI.simulate import FittingController
from NeutroSpecUI import read_file
from NeutroSpecUI.static_params import StaticParams


if TYPE_CHECKING:
    from NeutroSpecUI.main_window import NeutroSpecWindow


class ExperimentalSetup(QWidget):
    materialUpdate = Signal()

    def __init__(
        self,
        window: "NeutroSpecWindow",
        parent: QWidget | None = None,
        name: str = "Experiment",
    ) -> None:
        super().__init__(parent)
        self.name = name
        self.mat_widgets: list[MaterialWidget] = []

        self.setObjectName(name)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # TODO: make static_params dynamic
        static_params = [Parameter(1, name="scale"), Parameter(0, name="background")]
        self.exp_data = ExperimentData(None, self.get_materials(), static_params)
        self.materialUpdate.connect(self.update_materials)

        self.fitting_controler = FittingController(self)
        self.fitting_controler.resultReady.connect(self.exp_data.set_fit_sim)

        self.plot = PlotWidgetStacked(self.exp_data, parent=self)
        window.addPlotWidget(self.plot)

        delete_btn = QPushButton("Delete Experiment")
        delete_btn.setStyleSheet("background-color: #FF6961")
        delete_btn.setObjectName("deleteExperimentBtn")
        delete_btn.clicked.connect(self.confirm_delete_experiment)
        self.main_layout.addWidget(delete_btn)

        material_btn = QPushButton("Add Material")
        material_btn.setStyleSheet("background-color: #408140")
        material_btn.setObjectName("addMaterialBtn")
        material_btn.clicked.connect(self.create_empty_material)
        self.main_layout.addWidget(material_btn)

        load_file_btn = QPushButton("Load File")
        load_file_btn.setStyleSheet("background-color: #c88839")
        load_file_btn.setObjectName("loadFileBtn")
        load_file_btn.clicked.connect(self.load_file_dialog)
        self.main_layout.addWidget(load_file_btn)

        self.loaded_file_path: str | None = None
        self.loaded_file_label = QLabel("No file loaded", parent=self)
        self.loaded_file_label.setObjectName("loadedFileLabel")
        self.loaded_file_label.setBuddy(load_file_btn)
        self.main_layout.addWidget(self.loaded_file_label)

        fit_btn = QPushButton("Fit Plots")
        fit_btn.setObjectName("fitPlotBtn")
        fit_btn.clicked.connect(self.fit_simulation)
        self.main_layout.addWidget(fit_btn)

        self.container = QWidget(self)
        self.container.setObjectName("materialContainer")
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.container.setLayout(self.container_layout)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.container)
        self.main_layout.addWidget(self.scroll_area)

        static_params_input = StaticParams(static_params, parent=self)
        static_params_input.valueUpdate.connect(self.materialUpdate)
        self.container_layout.addWidget(static_params_input)

        self.save_fit_btn = QPushButton("Save Fit")
        self.save_fit_btn.setObjectName("saveFitBtn")
        self.save_fit_btn.clicked.connect(self.save_fit)
        self.main_layout.addWidget(self.save_fit_btn)

    def create_empty_material(self) -> MaterialWidget:
        mat = Material(
            "Material",
            thickness=Parameter(1, name="thickness"),
            fraction=Parameter(1, name="fraction"),
            roughness=Parameter(1, name="roughness"),
            rho=Parameter(1e-6, name="rho"),
        )
        return self.add_material(mat)

    def add_material(self, mat: Material) -> MaterialWidget:
        mat_widget = MaterialWidget(
            material=mat,
            parent=self,
            remove=self.remove_material,
        )
        self.mat_widgets.append(mat_widget)
        mat_widget.setObjectName(f"mat_{len(self.mat_widgets)}")
        mat_widget.valueUpdate.connect(self.materialUpdate)
        self.container_layout.addWidget(mat_widget)

        self.materialUpdate.emit()

        return mat_widget

    def remove_material(self, mat_widget: MaterialWidget) -> None:
        self.mat_widgets.remove(mat_widget)
        mat_widget.deleteLater()

    def deleteLater(self):
        self.plot.deleteLater()
        self.fitting_controler.deleteLater()
        return super().deleteLater()

    def get_materials(self) -> list[Material]:
        return [mat_widget.material for mat_widget in self.mat_widgets]

    def load_file_dialog(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Open .txt, .mft or .csv file",
            dir="",
            filter="Text, MFT and CSV Files (*.txt *.mft *.csv)",
        )

        if file_name:
            self.load_file(file_name)
        else:
            print("No file loaded")

    def load_file(self, file_name: str) -> None:
        data = read_file.load_file(file_name)
        self.exp_data.set_data(data)

        self.loaded_file_path = file_name
        metrics = QFontMetrics(self.font())
        elipsis = metrics.elidedText(file_name, Qt.TextElideMode.ElideLeft, 200)
        self.loaded_file_label.setText(elipsis)
        self.loaded_file_label.setToolTip(file_name)

    def update_materials(self) -> None:
        self.exp_data.set_materials(self.get_materials())

    def fit_simulation(self):
        if self.exp_data.data is None:
            print("No data loaded")
            # TODO: Make a dialog box to inform the user
            return

        self.plot.display_loading()
        self.fitting_controler.fit(self.exp_data.data, self.exp_data.sim)

    def confirm_delete_experiment(self):
        """
        Shows a confirmation dialog to confirm the deletion of the experimental setup.
        """
        reply = QMessageBox.question(
            self,
            "Delete Experiment",
            "Do you really want to delete this experimental setup?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.deleteLater()

    def clear(self) -> None:
        for mat_widget in self.mat_widgets:
            mat_widget.deleteLater()
        self.mat_widgets.clear()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "materials": [dataclasses.asdict(mat) for mat in self.get_materials()],
            "data_file": self.loaded_file_path,
        }

    def from_dict(self, data: dict) -> None:
        self.blockSignals(True)  # block signals to avoid multiple updates
        self.exp_data.blockSignals(True)

        self.clear()
        for mat_data in data["materials"]:
            mat = Material.from_dict(mat_data)
            self.add_material(mat)

        try:
            self.load_file(data["data_file"])
        except:
            print("No file loaded")  # TODO: Show error message as a dialog

        self.exp_data.blockSignals(False)
        self.blockSignals(False)
        self.materialUpdate.emit()  # emit only one update signal after loading

    def save_fit(self):
        file_name, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save fit data",
            dir="",
            filter="CSV Files (*.csv)",
        )

        if file_name:
            self.exp_data.fit.to_dataframe().to_csv(file_name, index=False)
            print(f"Fit data saved to {file_name}")
        else:
            print("No file selected")
