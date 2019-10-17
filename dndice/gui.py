from typing import Callable

import PyQt5.QtCore as qtcore
import PyQt5.QtGui as qtgui
import PyQt5.QtWidgets as qt
from dndice.core import verbose


class Roller(qt.QDialog):
    def __init__(self):
        super().__init__()
        self.entry = RollInput(self.roll)

        self.display = qt.QLabel()

        self.button = qt.QPushButton('Roll')
        self.button.clicked.connect(self.roll)
        self._draw()

    def roll(self):
        self.display.setText(verbose(self.entry.text()))

    def _draw(self):
        layout = qt.QGridLayout()
        layout.addWidget(qt.QLabel('Expression'), 0, 0)
        layout.addWidget(self.entry, 1, 0)
        layout.addWidget(self.display, 2, 0)
        layout.addWidget(self.button, 2, 1)
        layout.setAlignment(qtcore.Qt.AlignHCenter)
        self.setLayout(layout)


class RollInput(qt.QLineEdit):
    def __init__(self, populator: Callable[[], None]):
        super().__init__()
        self.callback = populator

    def keyPressEvent(self, event: qtgui.QKeyEvent) -> None:
        if event.key() in (qtcore.Qt.Key_Enter, qtcore.Qt.Key_Return):
            self.callback()
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    window = qt.QApplication([])
    application = Roller()
    application.show()
    window.exec_()
