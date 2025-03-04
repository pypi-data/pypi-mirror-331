import os
import sys
import ctypes
from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import shutil

import RagPUREAI_chunks_clean
import RagPUREAI_meta
import RagPUREAI_extract
import RagPUREAI_embed
import RagPUREAI_libs