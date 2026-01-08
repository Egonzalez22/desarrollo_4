from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    no_retener_iva = fields.Boolean(string="No retener IVA")
    constancia_no_retencion_iva = fields.Boolean(string="Constancia de no retención de IVA")
    fecha_inicio_no_ret = fields.Date(string="Fecha de inicio")
    fecha_fin_no_ret = fields.Date(string="Fecha de fin")

    @api.model
    def inhabilitar_contancia_no_retencion(self):
        partner_ids = self.env["res.partner"].search([("no_retener_iva", "=", True), ("fecha_fin_no_ret", "!=", False)])
        for partner in partner_ids:
            if fields.Date.today() > partner.fecha_fin_ret:
                partner.write({"no_retener_iva": False})
