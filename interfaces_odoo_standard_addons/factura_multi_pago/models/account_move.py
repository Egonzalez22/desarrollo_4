from odoo import fields, api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    tipo_factura = fields.Char(string='Tipo de Factura', compute='compute_tipo_factura')

    def compute_tipo_factura(self):
        for this in self:
            tipo_factura = ''
            if this.invoice_date_due:
                if this.invoice_date == this.invoice_date_due:
                    tipo_factura = 'contado'
                else:
                    tipo_factura = 'credito'
            this.tipo_factura = tipo_factura
