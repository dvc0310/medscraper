import json
import numpy as np

class DataHandler:
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            return json.JSONEncoder.default(self, obj)

    def __init__(self, filename):
        self.filename = filename

    def save_data(self, data):
        with open(self.filename, 'w', encoding='utf-8')  as file:
            file.write('[\n')  # Write the opening bracket of the JSON list
            for i, entry in enumerate(data):
                # Write each dictionary as a JSON string followed by a comma and newline, except for the last entry
                if i < len(data) - 1:
                    file.write(json.dumps(entry, cls=self.NumpyEncoder) + ',\n')
                else:
                    # The last entry should not have a comma at the end
                    file.write(json.dumps(entry, cls=self.NumpyEncoder) + '\n')
            file.write(']')  # Write the closing bracket of the JSON list
            
    def load_data(self):
        with open(self.filename, 'r') as file:
            data = json.load(file)
        return data


