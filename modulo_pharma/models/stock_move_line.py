import random
from datetime import datetime

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    def name_get(self):
        res = []
        for record in self:
            # As I understood prj_id it is many2one field. For example I set name of prj_id
            res.append((record.id, record.codigo_muestra))
        
        return res