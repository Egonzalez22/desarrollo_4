from datetime import datetime

from odoo import api, fields, models


class SaleOrderTemplate(models.Model):
    _inherit = 'sale.order.template'

    acreditado = fields.Boolean(default=False)
    acreditado_codigo_vigencia = fields.Text(string='Acreditado Código/Vigencia')
    acreditado_fecha = fields.Date(string='Acreditado Vigencia Hasta')
    referencia = fields.Html(string="Referencia")
    
