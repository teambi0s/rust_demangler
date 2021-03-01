import string

class UnableTov0Demangle(Exception):
    def __init__(self, given_str, message="Not able the given string using v0Demangler"):
        self.message = message
        self.given_str = given_str
        super().__init__(self.message)
    
    def __str__(self):
        return f'[{self.given_str}] {self.message}'

class V0Demangler(object):

    def demangle(self, inpstr : str) -> str:

        self.sanity_check(inpstr)
        inpstr = inpstr[inpstr.index("R") + 1:]
        
        self.parser = Parser(inpstr,0)
        if inpstr[0].isupper():
            self.parser.skip_path() 

    def sanity_check(self, inpstr : str):

        if not inpstr[0].isupper():
            raise UnableTov0Demangle(inpstr)

        for i in inpstr:
            if(ord(i) & 0x80 != 0):
                raise UnableTov0Demangle(inpstr)

class Ident(object):
    def __init__(self,ascii,punycode):
        self.ascii = ascii
        self.punycode = punycode
    

class Parser(object):
    
    def __init__(self,inn,next):
        self.inn = inn
        self.next = next

    def peek(self):
        return self.inn[self.next]  

    def eat(self, b : bytes):
        if self.peek() == b:
            self.next += 1
            return True
        else:
            return False

    def next(self):
        b = self.peek()
        self.next += 1
        return b 

    def hex_nibbles(self):
        start = self.next
        while True:
            n = self.next()
            if n.isdigit() or (n in "abcdef") :
                continue
            elif n == "_":
                break
            else:
                raise UnableTov0Demangle(self.inn)
        return self.inn[start:self.next-1]

    def digit_10(self):
        d = self.peek()
        if d.isdigit():
            d = int(d)
        else:
            return "Error"
        self.next += 1
        return d
    
    def digit_62(self):
        d = self.peek()
        if d.isdigit():
            d = int(d)
        elif d.islower():
            d = 10 + (ord(d) - ord("a"))
        elif d.isupper():
            d = 10 + 26 + (ord(d) - ord("A"))
        else:
            raise UnableTov0Demangle(self.inn)
        self.next += 1
        return d

    def integer_62(self):
        if self.eat('_'):
            return 0
        x = 0
        while not self.eat('_'):
            d = self.digit_62()
            x *= 62
            x += d
        return x+1
        
    def opt_integer_62(self,tag: str):
        if not self.eat(tag):
            return 0
        return self.integer_62() + 1 

    def disambiguator(self):
        return self.opt_integer_62('s')
        
    def namespace(self): 
        n = self.next()
        if n.isupper():
            return n 
        elif n.islower():
            return
        else:
            raise UnableTov0Demangle(self.inn)
        
    def backref(self):
        s_start = self.next + 1
        i = self.integer_62()
        if i >= s_start:
            raise UnableTov0Demangle(self.inn)
        self.next = i
    
    def ident(self):
        is_punycode = self.eat('u')
        len = self.digit_10()
        if len != 0:
            while True:
                d = self.digit_10()
                if d == "Error":
                    break
                len += 10
                len += int(d)

        self.eat('_')

        start = self.next
        self.next += len
        if self.next > len(self.inn):
            raise UnableTov0Demangle(self.inn)
        
        ident = self.inn[start:self.next]

        if is_punycode:
            if '_' in ident:
                i = ident.index('_')
                idt = Ident(ident[:i],ident[i+1:])
            else:
                idt = Ident("",ident)

            if not idt.punycode:
                raise UnableTov0Demangle(self.inn)
            
            return idt

        else:
            idt = Ident(ident,"")
            return idt

    
    def skip_path(self):
        if self.next().startswith('C'):
            self.disambiguator()
            self.indent()

        elif self.next().startswith('N'):
            self.namespace()
            self.skip_path()
            self.disambiguator()
            self.ident()

        elif self.next().startswith('M'):
            self.disambiguator()
            self.skip_path()
            self.skip_type()

        elif self.next().startswith('Y'):
            self.skip_type()
            self.skip_path()

        elif self.next().startswith('I'):
            self.skip_path()
            while not self.eat('E'):
                self.skip_generic_arg()

        elif self.next().startswith('B'):
            self.backref()
        
        else:
            raise UnableTov0Demangle(inpstr) 
        
    def skip_generic_arg(self):
        if self.eat('L'):
            self.integer_62()
        elif self.eat('K'):
            self.skip_const()
        else:
            self.skip_type()
        

    def skip_type(self):
        n = self.next()
        tag = n
        if basic_type(tag): 
            pass
        elif n == 'R' or n == 'Q':
            if self.eat('L'):
                self.integer_62()
            else:
                self.skip_type()
        elif n == 'P' or n == 'O' or n == 'S':
            self.skip_type()
        elif n == 'A':
            self.skip_type()
            self.skip_const()
        elif n == 'T':
            while not self.eat('E'):
                self.skip_type()
        elif n == 'F':
            _binder = self.opt_integer_62('G')
            _is_unsafe = self.eat('U')
            if self.eat('K'):
                c_abi = self.eat('C')
                if not c_abi:
                    abi = self.ident()
                    if abi.ascii or (not abi.punycode):   
                        raise UnableTov0Demangle(self.inn)
            while not self.eat('E'):
                self.skip_type()
            self.skip_type()
        elif n == 'D':
            _binder = self.opt_integer_62('G')
            while not self.eat('E'):
                self.skip_path()
                while self.eat('p'):
                    self.ident()
                    self.skip_type()
            if not self.eat("L"):
                raise UnableTov0Demangle(self.inn)
            self.integer_62()
        elif n == 'B':
            self.backref()
        else:
            self.next -= 1
            self.skip_path()
    
    def skip_const(self):
        if self.eat('B'):
            self.backref()
            return 

        ty_tag = self.next()
        if ty_tag == 'p' :
            return 
        type1 = ['h','t','m','y','o','j','b','c']
        type2 = ['a''s','l','x','n','i']

        if ty_tag in type1: 
            pass
        elif ty_tag in type2:
            _ = self.eat('n')
        else:
            raise UnableTov0Demangle(self.inn)
        self.hex_nibbles()
        return 


    


