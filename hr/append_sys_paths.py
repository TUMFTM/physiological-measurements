# Copyright Feiler 2021

"""Script appends sys.path for module import"""

import os
import sys
cur_top_level_path = os.path.split(os.path.dirname(os.path.join(os.getcwd(),
                                                                __file__)))[0]
if cur_top_level_path not in sys.path:
    sys.path.append(cur_top_level_path)
