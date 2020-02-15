from typing import Callable

import PyQt5.QtCore as qtcore
import PyQt5.QtGui as qtgui
import PyQt5.QtWidgets as qt
from dndice.lib.evaltree import EvalTree
from dndice.lib.exceptions import EvaluationError, RollError, ParseError

from dndice import compile


class EvalTreeCache:
    def __init__(self):
        self.cache = {}

    def __getitem__(self, expression: str) -> EvalTree:
        if expression not in self.cache:
            try:
                self.cache[expression] = compile(expression)
            except ParseError:
                raise
        return self.cache[expression]


class Roller(qt.QDialog):
    def __init__(self):
        super().__init__()
        self.window().setWindowTitle('Dice roller')
        self.entry = RollInput(self.roll)
        self.entry.setFocus()

        self.display = RollDisplay()

        self.button = qt.QPushButton('Roll')
        self.button.clicked.connect(self.roll)
        self.cache = EvalTreeCache()
        self._draw()

    def roll(self):
        try:
            self.display.populate(self.cache[self.entry.text()])
        except ParseError as e:
            self.display.show_error(e)

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


class RollDisplay(qt.QLabel):
    def __init__(self):
        super().__init__()
        self.defaultFont = self.font()
        self.errorFont = qtgui.QFont('monospace')

    def populate(self, tree: EvalTree):
        try:
            tree.evaluate()
            text = tree.verbose_result()
            color = 'black'
            if tree.is_critical():
                color = 'green'
            elif tree.is_fail():
                color = 'red'
            self.setText(text)
            self.setFont(self.defaultFont)
            self.setStyleSheet('color: {}'.format(color))
        except EvaluationError as e:
            self.show_error(e)

    def show_error(self, error: RollError):
        self.setText(str(error))
        self.setFont(self.errorFont)
        self.setStyleSheet('color: red')


if __name__ == '__main__':
    window = qt.QApplication([])
    application = Roller()
    application.show()
    window.exec_()
