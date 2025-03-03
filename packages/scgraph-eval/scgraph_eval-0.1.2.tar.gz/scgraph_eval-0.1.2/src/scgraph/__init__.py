"""
scGraph - A tool for analyzing single-cell data across batches
"""

__version__ = "0.1.2"  # Update this to match your current version

# Import main classes/functions to make them available at package level
from .scgraph import scGraph

# You can add other imports here as needed
# from .other_module import OtherClass

# Define what should be imported with "from scgraph import *"
__all__ = ["scGraph"]