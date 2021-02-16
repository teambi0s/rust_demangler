from rust_legacy import LegacyDemangler
from rust_v0 import V0Demangler

class TypeNotFoundError(Exception):
    def __init__(self, given_str, message="Not able to detect the Type for the given string"):
        self.message = message
        self.given_str = given_str
        super().__init__(self.message)
    
    def __str__(self):
        return f'[{self.given_str}] {self.message}'

class RustDemangler(object):
    LEGACYTYPE = 0
    V0TYPE = 1

    def __init__(self):
        self.legacy = LegacyDemangler()
        self.v0 = V0Demangler()

    def demangle(self, inpstr: str) -> str:
        """ Demangle the given string

        Args:
            inpstr (str): String to be demangled
        """
        curr_type = self.determine_type(inpstr)
        if curr_type == self.LEGACYTYPE:
            return self.legacy.demangle(inpstr)
        else:
            return self.v0.demangle(inpstr)


    def determine_type(self, inpstr: str) -> int:
        """ Determine the type of the given string

        Args:
            inpstr (str): Input String

        Raises:
            TypeNotFoundError: If the string can't be determined

        Returns:
            int: type of the string
        """ 
        if inpstr.startswith("_ZN") or inpstr.startswith("ZN") or inpstr.startswith("__ZN"):
            return self.LEGACYTYPE
        elif inpstr.startswith("v0-type-idk"):
            return self.V0TYPE
        else:
            raise TypeNotFoundError(inpstr)
