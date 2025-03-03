
from typing import List

from logging import Logger
from logging import getLogger

from pyutmodelv2.PyutClass import PyutClass

from ogl.OglClass import OglClass


class ElementTreeData:

    def __init__(self, pyutClass: PyutClass, oglClass: OglClass):

        self.logger: Logger = getLogger(__name__)

        self.pyutClass:         PyutClass  = pyutClass
        self.oglClass:          OglClass   = oglClass
        self._childElementNames: List[str] = []

    def addChild(self, childClassName: str):
        self._childElementNames.append(childClassName)

    @property
    def childElementNames(self) -> List[str]:
        return self._childElementNames

    @childElementNames.setter
    def childElementNames(self, theNewValues: List[str]):
        self._childElementNames = theNewValues

    def __str__(self):
        retStr: str = f'ElementTreeData - ClassName: {self.pyutClass.name} oglClass position: {self.oglClass.GetPosition()}\n'

        for childName in self.childElementNames:
            retStr += f'\t\tchildName: {childName}\n'
        return retStr

    def __repr__(self):
        return self.__str__()
