print('pakg1.module1 __name__ is:',__name__)

from .module2 import v2

print(v2)

import sys

print('module1 sys path is ',sys.path)


