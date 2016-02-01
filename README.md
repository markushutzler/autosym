autosym - Automated Schematic Symbol Generation
===============================================
This project is the first step to generate schematic symbols by 
using a simple symbol description format. Generalising schematic 
symbols into a plaintext based language has several advantages:
- version control
- portability
- simplicity

I'm using this script for quite a while and decided to share it. 
Autosym uses a pure python approach to generate schematic symbols. 
Well, its still work in progress but I'm getting close to rewrite 
my code to make it usable for others.

Usage
-----
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

Installation
-----------
```shell
python setup.py install
```