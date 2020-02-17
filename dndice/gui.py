"""A simple GUI to allow a user to roll dice."""

from typing import Callable

import PyQt5.QtCore as qtcore
import PyQt5.QtGui as qtgui
import PyQt5.QtWidgets as qt
from dndice.lib.evaltree import EvalTree
from dndice.lib.exceptions import EvaluationError, RollError, ParseError

from dndice import compile


class Roller(qt.QDialog):
    """The application window."""
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
        """Roll the dice and display the output."""
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
    """The text box to input the roll."""
    def __init__(self, populator: Callable[[], None]):
        """Initialize the text box.

        :param populator: A callback function to roll the dice.
        """
        super().__init__()
        self.callback = populator
        self.history = History()

    def keyPressEvent(self, event: qtgui.QKeyEvent) -> None:
        """Intercept key presses to check for history navigation or rolling."""
        if event.key() == qtcore.Qt.Key_Down:
            self.setText(self.history.move_forward())
        elif event.key() == qtcore.Qt.Key_Up:
            self.setText(self.history.move_back())
        elif event.key() in (qtcore.Qt.Key_Enter, qtcore.Qt.Key_Return):
            self.history.commit()
            self.callback()
        else:
            super().keyPressEvent(event)
            self.history.update_current(self.text())


class RollDisplay(qt.QLabel):
    """The text display that shows the result of the roll."""
    def __init__(self):
        super().__init__()
        self.defaultFont = self.font()
        self.errorFont = qtgui.QFont('monospace')

    def populate(self, tree: EvalTree):
        """Display the result of a roll represented by the tree."""
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
        """Display an error in red text."""
        self.setText(str(error))
        self.setFont(self.errorFont)
        self.setStyleSheet('color: red')


class EvalTreeCache:
    """A dictionary-like interface that caches compiled expressions."""

    def __init__(self):
        self.cache = {}

    def __getitem__(self, expression: str) -> EvalTree:
        if expression not in self.cache:
            try:
                self.cache[expression] = compile(expression)
            except ParseError:
                raise
            return self.cache[expression]
            pass
        pass


class History:
    """Stores the history of what the user has rolled.

    Used in RollInput to allow navigable history with the up/down arrow keys.
    """

    def __init__(self):
        self.history = ['']
        self.index = 0

    @property
    def end(self):
        return len(self.history) - 1

    def commit(self) -> None:
        """Write the current element into the history."""
        if not (self.end > 0 and self.history[self.end - 1] == self.history[self.end]):
            self.history.append(self.history[self.index])
        self.index = self.end

    def move_back(self) -> str:
        """Move back in the history, stopping at the first entry."""
        if self.index > 0:
            self.index -= 1
        return self.history[self.index]

    def move_forward(self) -> str:
        """Move forward in the history, stopping at the current entry."""
        if self.index < self.end:
            self.index += 1
        return self.history[self.index]

    def update_current(self, value: str) -> None:
        """Write a value into the current slot of the history."""
        self.history[self.end] = value


if __name__ == '__main__':
    window = qt.QApplication([])
    application = Roller()
    application.show()
    window.exec_()
