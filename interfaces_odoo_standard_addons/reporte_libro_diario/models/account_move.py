from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    nro_asiento = fields.Integer(compute='_get_nro_asiento')
    secuencia_asiento = fields.Char(string="Secuencia del asiento")

    def _get_nro_asiento(self):
        years = list(set([y.year for y in self.mapped('date')]))
        companies = self.mapped('company_id')
        for company in companies:
            for year in years:
                last_date = max(self.filtered(lambda move: move.company_id == company and move.date.year == year).mapped('date'))
                moves = self.search([
                    ('date', '>=', '01-01-' + str(year)),
                    ('date', '<=', last_date),
                    ('state', '=', 'posted'),
                    ('company_id', '=', company.id)
                ]).sorted(key=lambda x: (x.date, x.secuencia_asiento is False, x.secuencia_asiento, x.id))
                i = 1
                for this in moves:
                    this.nro_asiento = i
                    i += 1
