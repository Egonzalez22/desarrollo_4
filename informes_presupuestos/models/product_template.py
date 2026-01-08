from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    codigo_fabricante = fields.Char(string='Código fabricante', compute='_compute_codigo_fabricante', store=True)
    division = fields.Char(string='División', compute='_compute_division', store=True)

    
    @api.depends('default_code')
    def _compute_codigo_fabricante(self):
        """ 
        Eliminamos los primeros 3 grupos separados por guiones
        Ej.: EA-TE-MU-TE-0581 -> TE-0581
        """
        for record in self:
            if record.default_code and "-" in record.default_code:
                if len(record.default_code.split('-')) > 3:
                    codigo_fabricante = record.default_code.split('-')[3:]
                    codigo_fabricante = '-'.join(codigo_fabricante)
                    record.codigo_fabricante = codigo_fabricante
            else:
                record.codigo_fabricante = ''

    @api.depends('default_code')
    def _compute_division(self):
        """ 
        Dejamos el primer grupo separados por guiones
        Ej.: EA-TE-MU-TE-0581 -> EA
        """
        for record in self:
            if record.default_code and "-" in record.default_code:
                division = record.default_code.split('-')[0]
                record.division = division
            else:
                record.division = ''