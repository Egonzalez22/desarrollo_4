# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    explicit_url_ids = fields.One2many('link.tracker.explicit_url', 'company_id', string='URLs de la Compañía')
