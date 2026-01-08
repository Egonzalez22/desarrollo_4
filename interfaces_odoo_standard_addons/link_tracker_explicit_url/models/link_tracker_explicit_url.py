# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LinkTrackerExplicitURL(models.Model):
    _name = 'link.tracker.explicit_url'
    _sql_constraints = [('name_unique', 'unique(name)', 'Esta URL ya existe, verificar si no está asignada a otra compañía')]
    _description = 'URL disponible para una compañía'

    name = fields.Char()
    company_id = fields.Many2one('res.company')
