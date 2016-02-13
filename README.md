autosym - Automated Schematic Symbol Generation
===============================================
This project is created to generate schematic symbols by using a simple symbol description format. Generalising schematic symbols into a plaintext based language has several advantages:
- version control
- portability
- simplicity

I'm using this script for quite a while and decided to share it. Autosym uses a generic python approach to generate schematic symbols from symbol description files.

Well, its still work in progress but I'm getting close to rewrite my code to make it usable for others. gschem is currently the only supported schematic application. I'm planing to add eagle support next.

Script Usage
------------
The generation script allows you to generate symbols for gschem:
```
./autosym-generate.py library output
```

Module Usage
------------
If you want to use autosym in your own script you can use the following lines as a basic template or look into autosym-generate.py
```python
from autosym.description import Description
from autosym.render import gschem

symd = Description("test.symd")
symd.parse()
g = gschem.Symbol(symd)
data = g.generate(0)
h = open("symbol.sch", 'w')
h.write(data)
h.close()
```
Note that the module needs to be installed first.

Installation
-----------
The package does not have to be installed if used directly from autosim-generate.py if you want to import the library in you own
script run:
```shell
python setup.py install
```
