#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script to check if required libraries are installed."""

import sys
import io

# Set output encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Testing imports...")

try:
    import pandas
    print("OK: pandas")
except ImportError as e:
    print(f"FAIL: pandas - {e}")

try:
    import numpy
    print("OK: numpy")
except ImportError as e:
    print(f"FAIL: numpy - {e}")

try:
    import sklearn
    print("OK: sklearn")
except ImportError as e:
    print(f"FAIL: sklearn - {e}")

try:
    import lightgbm
    print("OK: lightgbm")
except ImportError as e:
    print(f"FAIL: lightgbm - {e}")

try:
    import catboost
    print("OK: catboost")
except ImportError as e:
    print(f"FAIL: catboost - {e}")

try:
    import xgboost
    print("OK: xgboost")
except ImportError as e:
    print(f"FAIL: xgboost - {e}")

try:
    import matplotlib
    print("OK: matplotlib")
except ImportError as e:
    print(f"FAIL: matplotlib - {e}")

try:
    import seaborn
    print("OK: seaborn")
except ImportError as e:
    print(f"FAIL: seaborn - {e}")

print("\nAll imports tested!")

