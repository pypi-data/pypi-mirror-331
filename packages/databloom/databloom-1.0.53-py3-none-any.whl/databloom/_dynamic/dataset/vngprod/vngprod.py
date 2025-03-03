# ---- render code block -----
from databloom._core.dataset import DatasetBase
from .table import *

class vngprod(DatasetBase):
    def __init__(self) -> None:
        self.database_id = "67c4fe8c83416b9075d83eaf"
        self.database_name  = "vngprod"
        
        self.campaign = campaign(self.database_name)
        
# ---- render code block 
    
