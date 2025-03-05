from collections.abc import Callable

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QWidget,
    QPushButton,
    QCheckBox,
    QSizePolicy,
)
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Signal

from NeutroSpecUI.material import Material
from NeutroSpecUI.parameter import Parameter


class MaterialWidget(QFrame):
    valueUpdate = Signal()

    def __init__(
        self,
        material: Material,
        closed: bool = False,
        parent: QWidget | None = None,
        remove: Callable[["MaterialWidget"], None] = lambda x: None,
    ) -> None:
        super().__init__()

        self.setParent(parent)
        self.setFrameStyle(QFrame.Shape.Box)
        self.my_layout = QVBoxLayout(self)
        self.setLayout(self.my_layout)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        self.my_layout.setSpacing(0)
        self.my_layout.setContentsMargins(0, 0, 0, 0)

        self.material = material
        # ich weiß nicht wofür dieses Attribut ist, wird bis jetzt nicht verwendet
        self.closed = closed

        self.init_material_inputs()

        self.remove_button = QPushButton("Remove", self)
        self.remove_button.setObjectName("deleteMaterialBtn")
        self.remove_button.setFixedHeight(20)
        self.remove_button.setStyleSheet("background-color: #FF6961")
        self.remove_button.clicked.connect(lambda: remove(self))
        self.remove_button.clicked.connect(self.valueUpdate)
        self.my_layout.addWidget(self.remove_button)

    # Wird nicht benutzt bis jetzt
    def toggle(self) -> None:
        self.closed = not self.closed

    def init_material_inputs(self) -> None:
        name = AttributeInputField(self, "name", parent=self)
        name.valueUpdate.connect(self.valueUpdate)
        self.my_layout.addWidget(name)

        thickness = ParameterInputField(self.material.thickness, parent=self)
        thickness.valueUpdate.connect(self.valueUpdate)
        self.my_layout.addWidget(thickness)

        fraction = ParameterInputField(self.material.fraction, parent=self)
        fraction.valueUpdate.connect(self.valueUpdate)
        self.my_layout.addWidget(fraction)

        roughness = ParameterInputField(self.material.roughness, parent=self)
        roughness.valueUpdate.connect(self.valueUpdate)
        self.my_layout.addWidget(roughness)

        rho = ParameterInputField(self.material.rho, parent=self)
        rho.valueUpdate.connect(self.valueUpdate)
        self.my_layout.addWidget(rho)


class AttributeInputField(QWidget):
    valueUpdate = Signal()

    def __init__(
        self, mat_widget: MaterialWidget, attr_name: str, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        input_field = QLineEdit(self)
        input_field.setFixedHeight(20)
        input_field.setText(getattr(mat_widget.material, attr_name))
        input_field.setObjectName(f"{attr_name}Input")
        input_field.editingFinished.connect(self.valueUpdate)

        label = QLabel(attr_name, self)
        label.setFixedHeight(20)
        layout.addWidget(label)
        layout.addWidget(input_field)

        input_field.textChanged.connect(
            lambda text: setattr(mat_widget.material, attr_name, str(text))
        )


class ParameterInputField(QFrame):
    valueUpdate = Signal()

    def __init__(self, param: Parameter, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QGridLayout(self)
        self.setLayout(layout)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 0, 5, 0)

        input_field = QLineEdit(self)
        input_field.setFixedHeight(20)
        input_field.setText(str(param.value))
        input_field.setObjectName(f"{param.name}Input")
        input_field.editingFinished.connect(self.valueUpdate)
        # TODO: signal is currently emitted on the first focus out event after creation
        # it would be good to fix that behavior an only emit after truly editing the value

        label = QLabel(param.name, self)
        label.setFixedHeight(20)

        checkbox = QCheckBox("Set locked", self)
        checkbox.setFixedHeight(20)
        checkbox.setChecked(param.locked)
        checkbox.setObjectName(f"{param.name}SetLocked")

        layout.addWidget(label, 0, 0)
        layout.addWidget(checkbox, 0, 1)
        layout.addWidget(input_field, 1, 0, 1, 2)

        validator = QDoubleValidator(input_field)
        input_field.setValidator(QDoubleValidator(input_field))
        input_field.textChanged.connect(
            lambda text: setattr(param, "value", validator.locale().toDouble(text)[0])
        )
        checkbox.stateChanged.connect(
            lambda state: setattr(param, "locked", state == 2)
        )
