"""
Will python - aka wpy library - entry point for all modules
"""

"""
Import all branches of wpy
"""
from willpy.Algorithms.Wpya import Wpya
from willpy.Aerodynamics.Wpyaero import Wpyaero
from willpy.DataStructure.Wpyd import Wpyd
from willpy.MachineLearning.Wpyml import Wpyml

class Wpy(Wpya, Wpyd, Wpyml, Wpyaero):
    """
    Will python - aka wpy library - entry point for all modules
    """
    __version__ = "0.0.1"
    def __init__(self):
        super().__init__()
    

__all__ = ['Wpya', 'Wpyd', 'Wpyml', 'Wpyaero']