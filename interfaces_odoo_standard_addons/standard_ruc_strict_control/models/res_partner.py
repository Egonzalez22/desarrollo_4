# -*- coding: utf-8 -*-
from odoo import models, fields, exceptions, api
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('vat', 'obviar_validacion')
    def val_ruc(self):
        result = super().val_ruc()
        for this in self:
            company = this.company_id or this.env.company
            if company.no_contact_main_vat_duplicates and (this.company_type == 'company' or (this.company_type == 'person' and not this.parent_id)):
                contacts = this.search([
                    ('id', 'not in', this.ids + this.child_ids.ids),
                    ('vat', '=', this.vat),
                    '|',
                    ('company_type', '=', 'company'),
                    '&',
                    ('company_type', '=', 'person'),
                    ('parent_id', '=', False),
                ])
                if contacts:
                    raise exceptions.ValidationError('Ya existe un contacto con el mismo RUC, no se puede crear un nuevo contacto')
        return result
