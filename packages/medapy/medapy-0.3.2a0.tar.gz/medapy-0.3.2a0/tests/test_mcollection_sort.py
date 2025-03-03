from pathlib import Path

from medapy.collection import (MeasurementCollection, DefinitionsLoader,
                               ParameterDefinition, MeasurementFile, ContactPair)


# Load default parameter definitions
parameters = DefinitionsLoader().get_all()

# Set path to folder with files
path = Path(__file__).parent.absolute() / 'files'

# Initialize folder as measurement collection
collection = MeasurementCollection(path, parameters)
# print(collection) # uncomment this line

collection.head(6) # default 5
collection.tail()
print()

c = sorted(collection[2:], key=lambda x: x.state_of('temperature').value)
print(type(c))