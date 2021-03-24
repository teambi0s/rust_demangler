import string

class UnableToLegacyDemangle(Exception):
    def __init__(self, given_str, message="Not able to demangle the given string using LegacyDemangler"):
        self.message = message
        self.given_str = given_str
        super().__init__(self.message)
    
    def __str__(self):
        return f'[{self.given_str}] {self.message}'

class LegacyDemangler(object):

    def demangle(self, inpstr : str) -> str:
        self.elements = 0

        disp = ""
        inpstr = inpstr[inpstr.index("N") + 1:]
        self.sanity_check(inpstr)

        if ".llvm." in inpstr:
            l = inpstr.find(".llvm.")
            candidate = inpstr[l+6:]
            for i in candidate: 
                if i not in string.hexdigits + "@":
                    raise UnableToLegacyDemangle(inpstr) 
            inpstr = inpstr[:l]   

        inn = inpstr
        for ele in range(self.elements):
            
            rest = inn
            for i in rest:
                if i.isdigit():
                    rest = rest[1:]
                    continue
                else:
                    break    
            
            num = int(inn[0:len(inn)-len(rest)]) 

            inn = rest[num:]   
            rest = rest[:num]   

            if ele != 0:
                disp += "::"

            if ele + 1 == self.elements:  
                if self.is_rust_hash(rest):
                    disp += rest
                    break
            
            if rest.startswith("_$"):
                rest = rest[1:]

            while True:
                if rest.startswith("."):
                    if rest[1:].startswith("."):  
                        disp += "::"
                        rest = rest[2:]
                    else:
                        disp += "."
                        rest = rest[1:]

                elif rest.startswith("$"):
                    end = rest[1:].find("$")
                    escape = rest[1:end+1]
                    after_escape = rest[end+2:] 
                
                    unescaped ={'SP': '@' , 'BP': '*' , 'RF': '&' , 'LT': '<' , 'GT':'>' , 'LP':'(' , 'RP':')' , 'C':','}

                    if escape.startswith("u"):
                        digits = escape[1:]

                        for i in digits:
                            if i not in string.hexdigits:
                                raise UnableToLegacyDemangle(inpstr)    

                        c = int(digits,16)
                        disp += chr(c)

                        rest = after_escape
                        continue 
                    
                    else:
                        disp += unescaped[escape]
                        rest = after_escape
                        continue
                
                elif ("$" or ".") in rest:
                    dollar = rest.find("$")
                    dot = rest.find(".")

                    if dollar == -1:        
                        disp += rest[:dot]
                        rest = rest[dot:]
                        continue

                    if dot == -1:           
                        disp += rest[:dollar]
                        rest = rest[dollar:]
                        continue

                    if dollar < dot:
                        disp += rest[:dollar]
                        rest = rest[dollar:]
                    else:
                        disp += rest[:dot]
                        rest = rest[dot:]
                else:
                    break
            disp += rest    

        self.suffix = inn[1:]
        if self.suffix:
            if self.suffix.startswith(".") and self.is_symbol_like(self.suffix):
                disp += self.suffix

        return disp  
            
    def is_symbol_like(self,suffix):
        for i in suffix:
            if i.isalnum() or self.is_ascii_punctuation(i):
                continue
            else:
                return False

        return True

    def is_ascii_punctuation(self,c):
        if c in string.punctuation:
            return True
        else:
            return False

    def is_rust_hash(self, s):
        if s.startswith("h"):
            for i in s[1:]:
                if i not in string.hexdigits:
                    return False
            return True
        else:
            return False 

    def sanity_check(self, inpstr : str):
        for i in inpstr:
            if(ord(i) & 0x80 != 0):
                raise UnableToLegacyDemangle(inpstr)

        self.elements = 0  
        c = 0
        while inpstr[c] != "E":
            len = 0
            if not inpstr[c].isdigit():
                raise UnableToLegacyDemangle(inpstr)

            while inpstr[c].isdigit():                
                len = len *10 + int(inpstr[c])
                c += 1
            
            c += len
            self.elements += 1