
from logging import Logger
from logging import getLogger

from wx import CANCEL
from wx import DEFAULT_DIALOG_STYLE
from wx import DefaultSize
from wx import EVT_BUTTON
from wx import EVT_CLOSE
from wx import ID_CANCEL
from wx import ID_OK
from wx import OK
from wx import RESIZE_BORDER
from wx import STAY_ON_TOP

from wx import CommandEvent
from wx import ColourDatabase
from wx import StdDialogButtonSizer
from wx import TextCtrl
from wx import Colour

from wx.lib.sized_controls import SizedDialog


class BaseEditDialog(SizedDialog):
    baseDlgLogger: Logger = getLogger(__name__)
    """
    Provides a common place to host duplicate code
    TODO:  This is a duplicate of Pyut's dialog of the same name
    """
    def __init__(self, parent, title='', size=DefaultSize, style: int = RESIZE_BORDER | STAY_ON_TOP | DEFAULT_DIALOG_STYLE):

        super().__init__(parent, title=title, size=size, style=style)

    def _layoutStandardOkCancelButtonSizer(self):
        """
        Call this last when creating controls;  Will take care of
        adding callbacks for the Ok and Cancel buttons
        """
        buttSizer: StdDialogButtonSizer = self.CreateStdDialogButtonSizer(OK | CANCEL)

        self.SetButtonSizer(buttSizer)
        self.Bind(EVT_BUTTON, self._onOk,    id=ID_OK)
        self.Bind(EVT_BUTTON, self._onClose, id=ID_CANCEL)
        self.Bind(EVT_CLOSE,  self._onClose)

    def _convertNone(self, checkString: str):
        """

        Args:
            checkString:  the string to possibly convert

        Returns: the same string, if string = None, return an empty string.
        """
        if checkString is None:
            checkString = ''
        return checkString

    # noinspection PyUnusedLocal
    def _onOk(self, event: CommandEvent):
        """
        """
        self.EndModal(OK)

    # noinspection PyUnusedLocal
    def _onClose(self, event: CommandEvent):
        """
        """
        self.EndModal(CANCEL)

    def _indicateEmptyTextCtrl(self, name: TextCtrl):

        self.baseDlgLogger.warning(f'Name is empty!!')
        name.BackgroundColour = ColourDatabase().Find('Red')

    def _indicateNonEmptyTextCtrl(self, name: TextCtrl, normalBackgroundColor: Colour):
        name.BackgroundColour = normalBackgroundColor
