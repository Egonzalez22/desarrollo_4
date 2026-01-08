from odoo import fields, models, exceptions

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.picking_ids:
                tc=order.currency_id._get_rates(
                    order.company_id, order.date_order or fields.Date.today())
                if tc:
                    for picking in order.picking_ids:
                        picking.tipo_cambio = 1/tc.get(order.currency_id.id)
                else:
                    raise exceptions.ValidationError(
                        "No existe un tipo de cambio para la moneda %s para la fecha %s" % (
                            order.curency_id.name, order.date_order or fields.Date.today()
                        )
                    )
        return res