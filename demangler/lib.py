#!/usr/bin/env python3

from legacy import legacy_demangle
#from v0 import v0_demangle
import string

def is_symbol_like(s):
    for i in s:
        if i.isalnum() or is_ascii_punctuation(i):
            continue
        else:
            return False

    return True

def is_ascii_punctuation(c):
    if c in string.punctuation:
        return True
    else:
        return False

def demangled(s):
    if ".llvm." in s:
        l = s.find(".llvm.")
        candidate = s[l+6:]
        for i in candidate: 
            if i not in string.hexdigits + "@":
                print("Error: llvm symbol error") 
        s = s[:l]   #removing ThinLTO LLVM internal symbols 

    if legacy_demangle(s) == False:
        #if v0_demangle(s) == False:
        #    return s + "\n" + "Not a rust symbol"
        #demang = v0_demangle(s)
        print("legacy failed dammit!")
    else:
        demang = legacy_demangle(s)  #return format {demangled string, `E`+suffix}


    demangled = demang[0]
    suffix = demang[1][1:] #remove `E` from the returned string    

    if suffix:
        if suffix.startswith(".") and is_symbol_like(suffix):
            demangled += suffix
        #else it is not suffix and we dont append to mangled

    return demangled #the final demangled string 

if __name__ == "__main__":
    mangled = input()
    print(demangled(mangled))

