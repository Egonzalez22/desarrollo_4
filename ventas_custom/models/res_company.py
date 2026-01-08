from odoo import _, api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    campos_personalizados_ventas = fields.Boolean(string="Puede ver campos personalizados para ventas", default=False)
    logo_acreditacion = fields.Binary(string="Logo de Acreditación")
