from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)
from PySide6.QtCore import Signal

from NeutroSpecUI.material_widget import ParameterInputField
from NeutroSpecUI.parameter import Parameter


class StaticParams(QFrame):
    """Widget to hold all the static parameters for a simulation.

    Attributes:
        params (list[Parameter]): List of all the static parameters.
        valueUpdate (Signal): Signal to trigger when a parameter is updated.
    """

    valueUpdate = Signal()

    def __init__(
        self,
        params: list[Parameter],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__()

        self.setParent(parent)
        self.setFrameStyle(QFrame.Shape.Box)
        self.my_layout = QVBoxLayout(self)
        self.setLayout(self.my_layout)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.my_layout.setSpacing(0)
        self.my_layout.setContentsMargins(0, 0, 0, 0)

        self.params = params

        for param in self.params:
            param_input = ParameterInputField(param, parent=self)
            param_input.valueUpdate.connect(self.valueUpdate)
            self.my_layout.addWidget(param_input)
