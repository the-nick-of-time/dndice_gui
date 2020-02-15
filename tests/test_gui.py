import unittest
from unittest.mock import MagicMock

from PyQt5.QtWidgets import QApplication
from dndice.lib.evaltree import EvalTree
from dndice.lib.exceptions import EvaluationError

from dndice.gui import RollDisplay

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

    def tearDown(self):
        self.window.closeAllWindows()


class TestRollInput(unittest.TestCase):
    def test_normal_keypress(self):
        pass

    def test_enter_keypress(self):
        pass


class TestBase(unittest.TestCase):
    def test_initialize(self):
        pass

    def test_button(self):
        pass

    def test_enter(self):
        pass


if __name__ == '__main__':
    unittest.main()
