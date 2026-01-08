# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools
from werkzeug import urls


class LinkTracker(models.Model):
    _inherit = 'link.tracker'

    explicit_url_id = fields.Many2one('link.tracker.explicit_url', string='URL base')

    @api.depends('code')
    def _compute_short_url(self):
        res = super(LinkTracker, self)._compute_short_url()
        for this in self.filtered(lambda x: x.explicit_url_id):
            short_url_host = tools.validate_url(this.explicit_url_id.name + '/r/')
            this.short_url = urls.url_join(short_url_host, '%(code)s' % {'code': this.code})
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'explicit_url_id' not in vals and self.env.context.get('default_explicit_url_id'):
                vals.update({'explicit_url_id': self.env.context.get('default_explicit_url_id')})
        res = super(LinkTracker, self).create(vals_list)
        return res
