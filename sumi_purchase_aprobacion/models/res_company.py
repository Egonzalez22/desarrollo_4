from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    restriction_receiving_import = fields.Boolean('Restricción Entrada Importación', default=False, copy=False)