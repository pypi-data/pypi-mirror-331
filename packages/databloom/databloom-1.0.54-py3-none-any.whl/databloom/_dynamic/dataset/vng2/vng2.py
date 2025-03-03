# ---- render code block -----
from databloom._core.dataset import DatasetBase
from .table import *

class vng2(DatasetBase):
    def __init__(self) -> None:
        self.database_id = "67c546a183416b9075d83eb1"
        self.database_name  = "vng2"
        
        self.campaign2 = campaign2(self.database_name)
        
# ---- render code block 
    
