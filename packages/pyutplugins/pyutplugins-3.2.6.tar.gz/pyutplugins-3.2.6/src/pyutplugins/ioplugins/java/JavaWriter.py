
from typing import List
from typing import cast

from logging import Logger
from logging import getLogger

from os import O_CREAT
from os import O_WRONLY

from os import open
from os import write

from os import sep as osSep

from pyutmodelv2.PyutLink import PyutLink
from pyutmodelv2.PyutLink import PyutLinks
from pyutmodelv2.PyutClass import PyutClass
from pyutmodelv2.PyutMethod import PyutMethod
from pyutmodelv2.PyutParameter import PyutParameter

from pyutmodelv2.enumerations.PyutLinkType import PyutLinkType
from pyutmodelv2.enumerations.PyutStereotype import PyutStereotype

from ogl.OglClass import OglClass

from pyutplugins.ExternalTypes import OglClasses
from pyutplugins.ExternalTypes import OglObjects


class JavaWriter:

    def __init__(self, writeDirectory: str):
        """

        Args:
            writeDirectory:
        """
        self.logger:          Logger = getLogger(__name__)
        self._writeDirectory: str    = writeDirectory

        # defining Constants    TODO: Make REAL constants
        self.__tab = "    "
        self.__visibility = {
            "+": "public",
            "-": "private",
            "#": "protected"
        }

    def write(self, oglObjects: OglObjects):

        oglClasses: OglClasses = cast(OglClasses, [oglObject for oglObject in oglObjects if isinstance(oglObject, OglClass)])

        for oglClass in oglClasses:
            self.logger.debug(f'{oglClass=}')
            pyutClass: PyutClass = cast(PyutClass, oglClass.pyutObject)
            self._writeClass(pyutClass)

    def _writeClass(self, pyutClass: PyutClass):
        """
        Writing a class to a file.

        Args:
            pyutClass:  The PyutClass object to write
        """
        className = pyutClass.name

        # Opening a file for each class
        fqn:        str = f'{self._writeDirectory}{osSep}{className}.java'
        flags:      int = O_WRONLY | O_CREAT
        javaFileFD: int = open(fqn, flags)

        # Extract the data from the class
        fields  = pyutClass.fields
        methods = pyutClass.methods
        parents = pyutClass.parents

        allLinks: PyutLinks   = pyutClass.links

        stereotype: PyutStereotype = pyutClass.stereotype

        # List of links
        interfaces: PyutLinks = PyutLinks([])     # List of interfaces implemented by the class
        links:      PyutLinks = PyutLinks([])     # Aggregation and compositions

        self._separateLinks(allLinks, interfaces, links)

        # Is it an interface
        classInterface = "class"
        if stereotype.name is not None:
            stereotypeName: str = stereotype.name
            if stereotypeName.lower() == "interface":
                classInterface = "interface"

        self._writeClassComment(javaFileFD, className, classInterface)
        write(javaFileFD, f'public {classInterface} {className}'.encode())

        self._writeParent(javaFileFD, parents)
        self._writeInterfaces(javaFileFD, interfaces)
        write(javaFileFD, ' {\n\n'.encode())

        self._writeFields(javaFileFD, fields)

        # Aggregation and Composition
        self._writeLinks(javaFileFD, links)
        self._writeMethods(javaFileFD, methods)
        write(javaFileFD, '}\n'.encode())

    def _separateLinks(self, allLinks, interfaces, links):
        """
        Separate the different plugintypes of links into lists.

        Args:
            allLinks:   list of links of the class
            interfaces: list of interfaces implemented by the class
            links:

        Returns:

        """
        for link in allLinks:
            pyutLink: PyutLink = cast(PyutLink, link)
            linkType: PyutLinkType = pyutLink.linkType
            self.logger.debug(f'Found linkType: `{linkType}`')
            if linkType == PyutLinkType.INTERFACE:
                interfaces.append(link)
            elif linkType == PyutLinkType.COMPOSITION or linkType == PyutLinkType.AGGREGATION:
                links.append(link)

    def _writeClassComment(self, file: int, className, classInterface):
        """
        Write class comment with doxygen organization.

        Args:
            file:       file descriptor
            className:
            classInterface:
        """
        write(file, f'/**\n * {classInterface} {className}\n * Class information here \n */\n'.encode())

    def _writeFields(self, file: int, fields):
        """
        Write fields in file.

        Args:
            file:   file object to write to
            fields: list of all fields of a class
        """
        # Write fields header
        if len(fields) > 0:
            write(file, f'{self.__tab}// ------\n{self.__tab}// Fields\n{self.__tab}// ------\n\n'.encode())
        # Write all fields in file
        for field in fields:
            # Visibility converted from "+" to "public", ...
            visibility = self.__visibility[str(field.visibility)]

            # Type
            fieldType: str = str(field.type)    # TODO could just be field.type.value
            self.logger.debug(f'fieldType: {fieldType}')

            # Name
            name = field.name

            # Default value
            default = field.defaultValue
            if default is not None and default != "":
                if fieldType.lower() == 'string':
                    default = f' = "{default}"'
                else:
                    default = f' = {default}'
            else:
                default = ""

            # Comments
            if fieldType == "":
                comments = " // Warning: no type"
            else:
                comments = ""

            self._writeFieldComment(file, name, self.__tab)
            write(file, f'{self.__tab}{visibility} {fieldType} {name}{default};{comments}\n'.encode())

    def _writeFieldComment(self, file: int, name: str, tab=""):
        """
        Write method comment using doxygen format.

        Args:
            file:   File descriptor
            name:   The field name
            tab:    `tab` character to use
        """
        write(file, f'{tab}/**\n'.encode())
        write(file, f'{tab} * field {name}\n'.encode())
        write(file, f'{tab} * More field information here.\n'.encode())

        write(file, f'{tab} */\n'.encode())

    def _writeParent(self, file: int, parents):
        """
        Writing parent for inheritance.  (Java only has single inheritance)

        Args:
            file:       file descriptor
            parents:    list of parents
        """
        nbr = len(parents)

        # If there is a parent:
        if nbr != 0:
            write(file, " extends ".encode())

            # Only one parent allowed
            parent: PyutClass = parents[0]
            name:   str       = parent.name
            write(file, name.encode())

    def _writeInterfaces(self, file: int, interfaces: List[PyutLink]):
        """
        Writing interfaces implemented by the class.

        Args:
            file:       file descriptor
            interfaces: list of implemented interfaces
        """
        nbr = len(interfaces)

        # If there is at least one interface:
        if nbr != 0:
            write(file, " implements ".encode())

            # Write the first interface
            interfaceName: str = interfaces[0].destination.name
            write(file, interfaceName.encode())

            # For all next interfaces, write the name separated by a ','
            for interface in interfaces[1:]:
                write(file, f', {interface.destination.name}'.encode())

    def _writeLinks(self, file, links):
        """
        Write relation links in file.

        Args:
            file:   The file descriptor
            links:  The class links
        """
        write(file, "\n".encode())
        # Write all relation links in file
        for link in links:
            link = cast(PyutLink, link)
            # Get Class linked (type of variable)
            destinationLinkName = link.destination.name
            # Get name of aggregation
            name = link.name
            # Array or single variable
            if link.destinationCardinality.find('n') != -1 or link.destinationCardinality.find('*') != -1:
                array = "[]"
            else:
                array = ""

            write(file, f'{self.__tab}private {destinationLinkName} {name}{array};\n'.encode())

    def _writeMethods(self, file: int, methods):
        """
        Writing methods in source (.java) file

        Args:
            file:       file descriptor
            methods:    list of all method of a class
        """
        # Write header
        if len(methods) > 0:
            header: str = f'\n{self.__tab}// -------\n{self.__tab}// Methods\n{self.__tab}// -------\n\n'
            write(file, header.encode())

        # for all method in methods list
        for aMethod in methods:
            method: PyutMethod = cast(PyutMethod, aMethod)
            self.logger.debug(f'method: {method}')
            self._writeMethodComment(file, method, self.__tab)
            self._writeMethod(file, method)

    def _writeMethodComment(self, file: int, method: PyutMethod, tab=""):
        """
        Write method comment with doxygen organization.

        Args:
            file:   file descriptor
            method: pyutMethod
            tab:    tab character(s) to use

        """
        write(file, f'{tab}/**\n'.encode())
        write(file, f'{tab} * method {method.name}\n'.encode())
        write(file, f'{tab} * More info here.\n'.encode())

        for param in method.parameters:
            write(file, f'{tab} * @param {param.name} : {str(param.type)}\n'.encode())

        if str(method.returnType.value) != '':
            write(file, f'{tab} * @return {str(method.returnType)}\n'.encode())

        write(file, f'{tab} */\n'.encode())

    def _writeMethod(self, file: int, method: PyutMethod):
        """
        Writing a method in file : name(param, param, ...).

        Args:
            file:       File descriptor
            method:     method object
        """
        name:       str = method.name
        visibility: str = self.__visibility[str(method.visibility)]
        returnType: str = str(method.returnType)
        if returnType == "":
            returnType = "void"

        write(file, f'{self.__tab}{visibility} {returnType} {name}('.encode())

        # for all param
        nbParam = len(method.parameters)
        self.logger.debug(f'# params: {nbParam}')
        for param in method.parameters:
            # writing param
            self._writeParam(file, param)

            # comma between param
            nbParam = nbParam - 1
            if nbParam > 0:
                write(file, ' , '.encode())

        write(file, f') {{\n{self.__tab}}}\n\n'.encode())

    def _writeParam(self, file: int, param: PyutParameter):
        """
        Writing params to file.

        Args:
            file:   file descriptor
            param:  pyut parameter object to write
        """
        paramType: str = param.type.__str__()
        paramName: str = param.name
        write(file, f'{paramType} {paramName}'.encode())
