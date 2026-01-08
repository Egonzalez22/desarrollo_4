from odoo import _, api, fields, models, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sequence_code_type = fields.Char(string="Codigo de tipo de envio", related="picking_type_id.sequence_code")

    def crear_remision(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "notas_remision_account.nota.remision",
            "context": {'default_estirar_desde': 'envios', 'default_picking_ids': [(6, 0, [self.id])], 'default_partner_id': self.partner_id.id},
            "name": "Nota de remision",
            'view_mode': 'form',
            'target': 'current'
        }
        return result