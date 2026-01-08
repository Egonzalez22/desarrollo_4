import random
from datetime import datetime

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"
    
    def name_get(self):
        res = []
        for record in self:
            # As I understood prj_id it is many2one field. For example I set name of prj_id
            res.append((record.id, record.product_id.name))
        return res