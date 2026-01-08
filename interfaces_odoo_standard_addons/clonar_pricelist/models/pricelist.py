from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import date


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def action_clone_pricelist(self, from_pricelist):
        items_to_delete = self.item_ids.filtered(
            lambda x: x.compute_price == 'fixed')
        items_to_delete.unlink()
        items_to_copy = from_pricelist.item_ids.filtered(
            lambda x: x.compute_price == 'fixed')
        new_items = []
        for item in items_to_copy:
            new_item = {
                'compute_price': 'fixed',
                'fixed_price': from_pricelist.currency_id._convert(item.fixed_price, self.currency_id, self.env.company, date.today()),
                'applied_on': item.applied_on,
                'product_tmpl_id': item.product_tmpl_id.id if item.product_tmpl_id else False,
                'product_id': item.product_id.id if item.product_id else False,
                'categ_id': item.categ_id.id if item.categ_id else False,
                'min_quantity': item.min_quantity,
                'date_start': item.date_start,
                'date_start': item.date_end,
                'currency_id': self.currency_id.id
            }
            new_items.append((0, 0, new_item))
        self.write({'item_ids': new_items})

    def button_clone_pricelist(self):
        view_id = self.env.ref('clonar_pricelist.wizard_clonar_form')
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'clonar_pricelist.wizard.clonar',
            'view_mode': 'form',
            'view_id': view_id.id,
            'target': 'new',
            'context':{'default_dest_pricelist_id':self.id}
        }
