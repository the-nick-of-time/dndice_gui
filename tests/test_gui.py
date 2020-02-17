import unittest
from unittest.mock import MagicMock

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from dndice.lib.evaltree import EvalTree
from dndice.lib.exceptions import EvaluationError

from dndice.gui import RollDisplay, Roller, RollInput, History

window = QApplication([])


class TestRollDisplay(unittest.TestCase):
    window = window

    def setUp(self):
        self.display = RollDisplay()
        self.text = '2+3 = 5'
        EvalTree.verbose_result = lambda tree: self.text

    def test_normal(self):
        EvalTree.is_critical = MagicMock(return_value=False)
        EvalTree.is_fail = MagicMock(return_value=False)
        tree = EvalTree('1d4')
        self.display.populate(tree)
        self.assertEqual(self.display.text(), self.text)
        self.assertEqual(self.display.styleSheet(), 'color: black')

    def test_crit(self):
        EvalTree.is_critical = MagicMock(return_value=True)
        EvalTree.is_fail = MagicMock(return_value=False)
        tree = EvalTree('1d4')
        self.display.populate(tree)
        self.assertEqual(self.display.text(), self.text)
        self.assertEqual(self.display.styleSheet(), 'color: green')

        # crit wins out even in cases where it hits both
        # which should never happen in normal play, as it would require 2 d20s to be considered at once
        EvalTree.is_critical = MagicMock(return_value=True)
        EvalTree.is_fail = MagicMock(return_value=True)
        tree = EvalTree('1d4')
        self.display.populate(tree)
        self.assertEqual(self.display.text(), self.text)
        self.assertEqual(self.display.styleSheet(), 'color: green')

    def test_fail(self):
        EvalTree.is_critical = MagicMock(return_value=False)
        EvalTree.is_fail = MagicMock(return_value=True)
        tree = EvalTree('1d4')
        self.display.populate(tree)
        self.assertEqual(self.display.text(), self.text)
        self.assertEqual(self.display.styleSheet(), 'color: red')

    def test_error(self):
        def new_verbose(tree):
            raise EvaluationError('Oops')

        EvalTree.verbose_result = new_verbose
        tree = EvalTree('1d4')
        self.display.populate(tree)
        self.assertEqual(self.display.text(), 'Oops')
        self.assertEqual(self.display.styleSheet(), 'color: red')


class TestRollInput(unittest.TestCase):
    def setUp(self):
        self.callback = MagicMock()
        self.input = RollInput(self.callback)

    def test_normal_keypress(self):
        QTest.keyPress(self.input, '1')
        self.assertEqual(self.input.text(), '1')
        QTest.keyPress(self.input, '2')
        self.assertEqual(self.input.text(), '12')
        QTest.keyPress(self.input, Qt.Key_Backspace)
        self.assertEqual(self.input.text(), '1')

    def test_enter_keypress(self):
        self.input.setText('12')
        QTest.keyPress(self.input, Qt.Key_Enter)
        self.assertEqual(self.input.text(), '12')
        self.callback.assert_called_once_with()

    def test_history(self):
        QTest.keyPress(self.input, '1')
        QTest.keyPress(self.input, Qt.Key_Enter)
        QTest.keyPress(self.input, Qt.Key_Backspace)
        QTest.keyPress(self.input, '2')
        QTest.keyPress(self.input, Qt.Key_Up)
        self.assertEqual(self.input.text(), '1')
        QTest.keyPress(self.input, Qt.Key_Down)
        self.assertEqual(self.input.text(), '2')


class TestBase(unittest.TestCase):
    def setUp(self):
        self.app = Roller()

    def test_button(self):
        self.app.entry.setText('14')
        QTest.mouseClick(self.app.button, Qt.LeftButton)
        self.assertEqual(self.app.display.text(), '14 = 14')

    def test_enter(self):
        self.app.entry.setText('14')
        QTest.keyPress(self.app.entry, Qt.Key_Enter)
        self.assertEqual(self.app.display.text(), '14 = 14')

    def test_error(self):
        self.app.entry.setText('14d')
        QTest.mouseClick(self.app.button, Qt.LeftButton)
        self.assertEqual(self.app.display.text(), 'Unexpected end of expression.\n    14d\n       ^')


class TestHistory(unittest.TestCase):
    def test_commit(self):
        hist = History()
        self.assertEqual(hist.index, 0)
        hist.commit()
        self.assertEqual(hist.index, 1)

    def test_no_move_before_start(self):
        hist = History()
        hist.move_back()
        self.assertEqual(hist.index, 0)

    def test_no_move_past_end(self):
        hist = History()
        hist.move_forward()
        self.assertEqual(hist.index, 0)

    def test_update(self):
        hist = History()
        hist.update_current('15')
        self.assertEqual(hist.history[hist.index], '15')
        current = hist.move_forward()
        self.assertEqual(current, '15')
        self.assertEqual(hist.index, 0)

    def test_no_empty_trailing(self):
        hist = History()
        hist.update_current('1')
        hist.commit()
        hist.commit()
        self.assertEqual(hist.index, 1)

    def test_no_edit_history(self):
        hist = History()
        hist.update_current('1')
        hist.commit()
        hist.move_back()
        hist.update_current('2')
        self.assertEqual(hist.history[hist.index], '1')


if __name__ == '__main__':
    unittest.main()
