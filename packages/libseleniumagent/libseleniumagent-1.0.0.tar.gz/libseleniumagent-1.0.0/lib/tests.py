import importlib
import sys
import os
from inspect import getmembers, isclass
from typing import Dict, List, Any
from libseleniumagent.base import TestBase

TESTS_DIR = os.getenv('TESTS_DIR', '/data/tests')
assert os.path.isdir(TESTS_DIR), 'invalid TEST_DIR'
sys.path.append(TESTS_DIR)

TESTS: List[TestBase] = []

for fn in sorted(os.listdir(TESTS_DIR)):
    if not fn.endswith('.py'):
        continue
    mod = importlib.import_module(fn[:-3])
    for _, cls in getmembers(mod, isclass):
        if TestBase in cls.__bases__:
            TESTS.append(cls)
