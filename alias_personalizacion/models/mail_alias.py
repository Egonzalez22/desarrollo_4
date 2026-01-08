from odoo import fields, models, api

class Alias(models.Model):
    _inherit = 'mail.alias'
    
    @api.depends('alias_name')
    def _compute_alias_domain(self):
        super(Alias, self)._compute_alias_domain()
        for rec in self:
            if rec.env.company.id != 1:
                rec.alias_domain = rec.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain_analitica")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    alias_domain = fields.Char('Alias Domain', readonly=False)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id.id == 1:
            self.alias_domain = self.env['ir.config_parameter'].sudo().get_param('mail.catchall.domain')
        else:
            self.alias_domain = self.env['ir.config_parameter'].sudo().get_param('mail.catchall.domain_analitica')