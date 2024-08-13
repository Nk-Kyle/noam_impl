import xml.etree.ElementTree as ET
from os import path
from noam_impl.model.frequency import FrequencyTable
from noam_impl.model.diagram import ClassDiagram
from typing import List


# File is located in the same directory in folder schemas
class FrequencyReader:

    def __init__(self, folder: str):
        self.folder = folder

    def read(self) -> FrequencyTable:
        """
        Reads the frequency.xml file and returns a FrequencyTable object

        Returns
        -------
        FrequencyTable
            The frequency table object
        """

        tree = ET.parse(path.join(self.folder, "frequency.xml"))
        root = tree.getroot()

        frequency_table = FrequencyTable()
        for frequency in root:
            object_name = frequency.attrib["name"]
            object_frequency = float(frequency.text)
            object_type = frequency.attrib["type"]
            frequency_table.set_frequency(object_name, object_frequency, object_type)
        return frequency_table
