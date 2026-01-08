from odoo import _, api, fields, models


class WizardClonePricelist(models.TransientModel):
    _name = 'clonar_pricelist.wizard.clonar'
    _description = 'Wizard clonar pricelist'

    dest_pricelist_id = fields.Many2one(comodel_name='product.pricelist', string='Tarifa destino',required=True)
    origin_pricelist_id = fields.Many2one(comodel_name='product.pricelist', string='Tarifa origen',required=True)


    def button_confirm(self):
        self.dest_pricelist_id.action_clone_pricelist(self.origin_pricelist_id)
