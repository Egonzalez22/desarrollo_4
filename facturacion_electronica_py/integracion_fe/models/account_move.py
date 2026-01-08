from odoo import _, api, fields, models
import base64

class AccountMove(models.Model):
    _inherit = 'account.move'



    def action_post_fe(self):
        for record in self:
            try:
                record.action_post()
                kude = self.env['ir.actions.report'].sudo().with_context(
                            force_report_rendering=True)._render_qweb_pdf(
                                'facturacion_electronica_py.facturas_template', res_ids=record.id)
                return {'cdc':record.cdc,'dcarQR':record.dcarQR,'kude_pdf': base64.encodebytes(kude[0]).decode(),'name':record.name}
            except Exception as ex:
                return False