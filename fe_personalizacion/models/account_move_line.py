import math
import re

from odoo import _, api, exceptions, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def getdDesProSer(self):
        # Solamente se muestra el nombre del producto sin su codigo
        if self.product_id:
            name = self.product_id.name
        else:
            name = self.name
        
        if not name:
            name = ""
            return name
        
        # Limpiamos el texto de caracteres raros
        name = name.replace('\n', ' ')
        name = name.replace('\r', ' ')
        name = name.replace('\t', ' ')
        name = re.sub('\W+',' ', name)

        return name
