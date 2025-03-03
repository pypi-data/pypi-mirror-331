from copy import copy

class Collection:
    def __init__(self, 
                 collection,
                 parameters,
                 file_pattern: str = "*.*",
                 separator: str = "_"):
        self.files = collection
        self.param_definitions = {k: v for k, v in enumerate(parameters)}
        self.file_pattern = file_pattern
        self.separator = separator
        
    def __copy__(self):
        """Create a shallow copy of the object"""
        new_obj = type(self)(collection=self.files.copy(),
                             parameters=list(self.param_definitions.values()))  # Create new instance of the same class

        # # Copy mutable objects
        # new_obj.files = self.files.copy()  # Shallow copy of the list
        # new_obj.params = list(self.param_definitions.values())  # Shallow copy of the dict

        # Copy immutable objects directly
        new_obj.file_pattern = self.file_pattern
        new_obj.separator = self.separator
        return new_obj
    
    def copy(self):
        return self.__copy__()
    
    def __eq__(self, other):
        return self.files == other.files
    
files = [f'file #{_}' for _ in range(20)]
params = [f'param #{_}' for _ in range(3)]

collection1 = Collection(files, params)
collection2 = collection1
collection3 = copy(collection1)
collection4 = collection1.copy()

print(collection1 is collection2, collection1 == collection2)
print(collection1 is collection3, collection1 == collection3)
print(collection1 is collection4, collection1 == collection4)
print(collection3 is collection4, collection3 == collection4)