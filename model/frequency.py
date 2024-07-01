from collections import defaultdict


class FrequencyTable:
    def __init__(self):
        self.data = defaultdict(lambda: ("unknown", 0))

    def get_frequency(self, obj_name: str):
        return self.data.get(obj_name, ("unknown", 0))[1]

    def set_frequency(self, obj_name: str, frequency: float, type):
        self.data[obj_name] = (type, frequency)

    def __str__(self):
        # return as a table
        result = ""

        # Get the max length of the object names
        max_length = max([len(obj) for obj in self.data.keys()])
        max_length = max(max_length, len("Object"))
        max_length += 2

        # Get the max length of the type names
        max_length_type = max([len(self.data[obj][0]) for obj in self.data.keys()])
        max_length_type = max(max_length_type, len("Type"))
        max_length_type += 2

        # Get the max length of the frequency values
        max_length_freq = max([len(str(self.data[obj][1])) for obj in self.data.keys()])
        max_length_freq = max(max_length_freq, len("Frequency"))
        max_length_freq += 2

        # Create the header
        result += f"{'Object':<{max_length}}{'Type':<{max_length_type}}{'Frequency':<{max_length_freq}}\n"
        result += "-" * (max_length + max_length_type + max_length_freq) + "\n"

        # Create the table
        for obj in self.data.keys():
            result += f"{obj:<{max_length}}{self.data[obj][0]:<{max_length_type}}{self.data[obj][1]:<{max_length_freq}}\n"

        return result
