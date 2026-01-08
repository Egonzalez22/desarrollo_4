# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools


class SocialPost(models.Model):
    _inherit = 'social.post'

    explicit_url_id = fields.Many2one('link.tracker.explicit_url', string='URL base')

    def _action_post(self):
        if not self.env.context.get('default_explicit_url_id'):
            for this in self:
                super(SocialPost, self).with_context(default_explicit_url_id=this.explicit_url_id and this.explicit_url_id.id)._action_post()
        else:
            super(SocialPost, self)._action_post()
        return
