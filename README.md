# rust_demangler

A package for demangling Rust symbols, written in Python.

Setup
-----
```bash
pip install rust_demangler
```

Usage
-----
```py
from rust_demangler import demangle
print(demangle(<mangled_name>))
```
Example 
-------
```py
demangle("_ZN3foo3barE") == "foo::bar"  #legacy style
demangle("_RNvC6_123foo3bar") == "123foo::bar"  #v0 style
```

License 
-------

This project is licensed under the [MIT License](LICENSE)
