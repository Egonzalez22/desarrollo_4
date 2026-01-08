from datetime import datetime

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def action_imprimir_etiqueta_analitica(self):
        print("Hello world")
        return self.env.ref('etiqueta_analitica.action_report_etiqueta_analitica').report_action(self)