from odoo import fields, models, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    allowed_user_ids_inflows = fields.Many2many('res.users', relation='stock_location_res_users_allow_inflows',
                                                string='Usuarios Autorizados a validar Recepciones')
    allowed_user_ids_outflows = fields.Many2many('res.users', relation='stock_location_res_users_allow_outflows',
                                                 string='Usuarios Autorizados a validar Salidas')
