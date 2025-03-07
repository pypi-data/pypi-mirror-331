from pathlib import Path
from collections import UserDict
import xml.etree.ElementTree as ET
import json
import xmltodict


class XMLFile(UserDict):
    """
    Parent class for XML and psa representation that loads XML as a
    python-internal tree and as a dict.

    Parameters
    ----------
    path_to_file : Path | str :
        the path to the xml file

    Returns
    -------

    """

    def __init__(self, path_to_file: Path | str):
        self.path_to_file = Path(path_to_file)
        self.file_name = self.path_to_file.name
        self.file_dir = self.path_to_file.parents[0]
        self.input = ""
        with open(self.path_to_file, "r") as file:
            for line in file:
                self.input += line
        self.xml_tree = ET.fromstring(self.input)
        self.data = xmltodict.parse(self.input)

    def to_xml(self, file_name=None, file_path=None):
        """
        Writes the dictionary to xml.

        Parameters
        ----------
        file_name : str :
            the original files name (Default value = self.file_name)
        file_path : pathlib.Path :
            the directory of the file (Default value = self.file_dir)

        Returns
        -------

        """
        file_path = self.file_dir if file_path is None else file_path
        file_name = self.file_name if file_name is None else file_name
        with open(Path(file_path).joinpath(file_name), "w") as file:
            file.write(xmltodict.unparse(self.data, pretty=True))

    def to_json(self, file_name=None, file_path=None):
        """
        Writes the dictionary representation of the XML input to a json
        file.

        Parameters
        ----------
        file_name : str :
            the original files name (Default value = self.file_name)
        file_path : pathlib.Path :
            the directory of the file (Default value = self.file_dir)

        Returns
        -------

        """
        file_path = self.file_dir if file_path is None else file_path
        file_name = self.file_name if file_name is None else file_name
        with open(Path(file_path).joinpath(file_name + ".json"), "w") as file:
            json.dump(self.data, file, indent=4)


class XMLCONFile(XMLFile):
    """ """

    def __init__(self, path_to_file):
        super().__init__(path_to_file)


class PsaFile(XMLFile):
    """ """

    def __init__(self, path_to_file):
        super().__init__(path_to_file)
