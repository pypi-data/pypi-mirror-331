
from typing import NewType
from typing import cast
from typing import Dict
from typing import Tuple

from logging import Logger
from logging import getLogger

from dataclasses import dataclass

from tempfile import gettempdir

from os import sep as osSep

from networkx import read_gml
from networkx import Graph

from orthogonal.mapping.EmbeddedTypes import Position
from orthogonal.mapping.EmbeddedTypes import Positions
from orthogonal.mapping.EmbeddedTypes import ScreenCoordinates
from orthogonal.mapping.EmbeddingToScreen import EmbeddingToScreen
from orthogonal.mapping.ScreenSize import ScreenSize

from orthogonal.topologyShapeMetric.Compaction import Compaction
from orthogonal.topologyShapeMetric.OrthogonalException import OrthogonalException
from orthogonal.topologyShapeMetric.Orthogonalization import Orthogonalization
from orthogonal.topologyShapeMetric.Planarization import Planarization

from pyutplugins.ExternalTypes import OglObjects

from pyutplugins.ioplugins.gml.GMLExporter import GMLExporter
from pyutplugins.preferences.PluginPreferences import PluginPreferences
from pyutplugins.toolplugins.orthogonal.LayoutAreaSize import LayoutAreaSize
from pyutplugins.toolplugins.orthogonal.OrthogonalAdapterException import OrthogonalAdapterException

GraphicsCoordinates = NewType('GraphicsCoordinates', Tuple[int, int])
LayoutEngineInput   = NewType('LayoutEngineInput', Dict[str, GraphicsCoordinates])

EngineCoordinates  = NewType('EngineCoordinates', Tuple[int, int])
LayoutEngineOutput = NewType('LayoutEngineOutput', Dict[str, EngineCoordinates])


@dataclass
class OglCoordinate:

    __slots__ = ['x', 'y']

    x: int
    y: int


OglCoordinates = Dict[str, OglCoordinate]


class OrthogonalAdapter:

    TEMPORARY_GML_LAYOUT_FILENAME: str = 'toOrthogonalLayoutV2.gml'

    def __init__(self, umlObjects: OglObjects):

        self.logger: Logger      = getLogger(__name__)
        gmlExporter: GMLExporter = GMLExporter()            # TODO: Fix this Yeah I know bad to share this way

        gmlExporter.translate(umlObjects=umlObjects)

        if PluginPreferences().debugTempFileLocation is True:
            self._pathToLayout = f'{OrthogonalAdapter.TEMPORARY_GML_LAYOUT_FILENAME}'
        else:
            tempDir: str = gettempdir()
            self._pathToLayout = f'{tempDir}{osSep}{OrthogonalAdapter.TEMPORARY_GML_LAYOUT_FILENAME}'

        with open(self._pathToLayout, 'w') as writer:
            writer.write(gmlExporter.gml)

        self._ets:            EmbeddingToScreen = cast(EmbeddingToScreen, None)
        self._nxGraph:        Graph             = cast(Graph, None)
        self._oglCoordinates: OglCoordinates    = cast(OglCoordinates, None)

    @property
    def oglCoordinates(self) -> OglCoordinates:
        return self._oglCoordinates

    def doLayout(self, layoutAreaSize: LayoutAreaSize):

        self._nxGraph = Graph(read_gml(self._pathToLayout))

        positions: LayoutEngineInput = self._toLayoutEngineInput(self._nxGraph)

        self.logger.info(f'Generated positions: {positions}')

        compact: Compaction = self._runLayout(nxGraph=self._nxGraph, positions=positions)

        enginePositions:   LayoutEngineOutput = compact.pos
        embeddedPositions: Positions = self._toEmbeddedPositions(enginePositions)

        screenSize: ScreenSize = ScreenSize(width=layoutAreaSize.width, height=layoutAreaSize.height)
        self._ets = EmbeddingToScreen(screenSize, embeddedPositions)
        self._oglCoordinates = self._toOglCoordinates(nxGraph=self._nxGraph)

    def _runLayout(self, nxGraph: Graph, positions: LayoutEngineInput) -> Compaction:

        try:
            planar:     Planarization     = Planarization(nxGraph, positions)
            orthogonal: Orthogonalization = Orthogonalization(planar)
            compact:    Compaction        = Compaction(orthogonal)
        except OrthogonalException as oe:
            eMsg: str = f'{oe}'
            self.logger.error(eMsg)
            raise OrthogonalAdapterException(eMsg)

        return compact

    def _toLayoutEngineInput(self, nxGraph: Graph) -> LayoutEngineInput:

        positions: LayoutEngineInput = LayoutEngineInput({})
        for node in nxGraph:
            self.logger.debug(f'node: {node}')
            x: int = nxGraph.nodes[node]['graphics']['x']
            y: int = nxGraph.nodes[node]['graphics']['y']
            positions[node] = GraphicsCoordinates((x, y))

        return positions

    def _toEmbeddedPositions(self, embeddedPositions: LayoutEngineOutput) -> Positions:

        positions: Positions = {}
        for nodeName in embeddedPositions.keys():
            ePos: EngineCoordinates = embeddedPositions[nodeName]
            position: Position = Position(x=ePos[0], y=ePos[1])

            positions[nodeName] = position

        return positions

    def _toOglCoordinates(self, nxGraph: Graph) -> OglCoordinates:

        retCoordinates: OglCoordinates = {}
        for node in nxGraph:
            scrCoordinates: ScreenCoordinates = self._ets.getScreenPosition(node)
            oglCoordinates: OglCoordinate     = OglCoordinate(scrCoordinates.x, scrCoordinates.y)

            retCoordinates[node] = oglCoordinates

        return retCoordinates
