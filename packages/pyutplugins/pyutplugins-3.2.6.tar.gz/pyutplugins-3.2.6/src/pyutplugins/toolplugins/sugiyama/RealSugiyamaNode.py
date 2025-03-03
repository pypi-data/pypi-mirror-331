from typing import Tuple

from pyutplugins.toolplugins.sugiyama.SugiyamaNode import SugiyamaNode
from pyutplugins.toolplugins.sugiyama.SugiyamaNode import SugiyamaVEs

from pyutplugins.toolplugins.sugiyama.ALayoutNode import ALayoutNode

from pyutplugins.toolplugins.sugiyama.SugiyamaGlobals import SugiyamaGlobals


class RealSugiyamaNode(SugiyamaNode):
    """
    RealSugiyamaNode: A RealSugiyamaNode object is a node of the Sugiyama
    graph associated to an OglObject of the UML diagram, which can be a
    class or a note.

    For more information, see ../ToSugiyama.py

    Instantiated by: ../ToSugiyama.py

    :author: Nicolas Dubois
    :contact: nicdub@gmx.ch
    :version: $Revision: 1.4 $
    """
    def __init__(self, oglObject):
        """

        Args:
            oglObject: oglObject: diagram class or note
        """
        super().__init__()

        self.__aLayoutNode = ALayoutNode(oglObject)

    def getSize(self) -> Tuple[int, int]:
        """
        Get the size of the node.

        Returns: (int, int) : tuple (width, height)
        """
        return self.__aLayoutNode.getSize()

    def setPosition(self, xCoord: int, yCoord: int):
        """
        Set node position.

        Args:
            xCoord:  x position in absolute coordinates
            yCoord:  y position in absolute coordinates
        """
        self.__aLayoutNode.setPosition(xCoord, yCoord)

    def getPosition(self) -> Tuple[int, int]:
        """
        Get node position.

        Returns: (int, int) : tuple (x, y) in absolute coordinates
        """
        return self.__aLayoutNode.getPosition()

    def getName(self) -> str:
        """
        Get the name of the OglObject.

        @return str : name of OglObject
        @author Nicolas Dubois
        """
        return self.__aLayoutNode.getName()

    def fixAnchorPos(self):
        """
        Fix the positions of the anchor points.

        The anchor points are placed according to parent and child positions.
        Before calling this method, be sure you have set the indices of all
        parent and children (see setIndex).

        """
        # Get position and size of node
        (width, height) = self.getSize()
        (x, y) = self.getPosition()

        # Fix all children anchors position
        # Sort child list to eliminate crossing
        children: SugiyamaVEs = self.getChildren()
        children.sort(key=SugiyamaGlobals.cmpIndex)

        nChildren: int = len(children)
        # For all children
        for i in range(nChildren):
            (child, link) = children[i]
            # Fix anchors coordinates
            link.setDestAnchorPos(x + width * (i + 1) // (nChildren + 1), y + height)

        # Parent anchors position
        # Sort parents list to eliminate crossing
        parents: SugiyamaVEs = self.getParents()
        parents.sort(key=SugiyamaGlobals.cmpIndex)
        nParents: int = len(parents)
        # For all parents
        for i in range(nParents):
            (parent, link) = parents[i]
            # Fix anchors coordinates
            link.setSrcAnchorPos(x + width * (i + 1) // (nParents + 1), y)

    def __repr__(self) -> str:
        return f'RealSugiyamaNode name: {self.getName()} level: {self.getLevel()}'
