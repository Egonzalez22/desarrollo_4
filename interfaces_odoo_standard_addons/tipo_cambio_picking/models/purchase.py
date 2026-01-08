from odoo import _, api, fields, models, exceptions


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        tc = self.currency_id._get_rates(
            self.company_id, self.date_order or fields.Date.today())
        if tc:
            res['tipo_cambio'] = 1/tc.get(self.currency_id.id)
        else:
            raise exceptions.ValidationError("No existe un tipo de cambio para la moneda %s para la fecha %s" % (
                self.currency_id.name, self.date_order or fields.Date.today()))
        return res
