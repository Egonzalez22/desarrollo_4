# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools


class MailingMailing(models.Model):
    _inherit = 'mailing.mailing'

    explicit_url_id = fields.Many2one('link.tracker.explicit_url', string='URL base')

    def action_launch(self):
        if not self.env.context.get('default_explicit_url_id'):
            for this in self:
                super(MailingMailing, self).with_context(default_explicit_url_id=this.explicit_url_id and this.explicit_url_id.id).action_launch()
        else:
            super(MailingMailing, self).action_launch()
        return

    def action_send_mail(self, res_ids=None):
        if not self.env.context.get('default_explicit_url_id'):
            for this in self:
                super(MailingMailing, self).with_context(default_explicit_url_id=this.explicit_url_id and this.explicit_url_id.id).action_send_mail(res_ids)
        else:
            super(MailingMailing, self).action_send_mail(res_ids)
        return
