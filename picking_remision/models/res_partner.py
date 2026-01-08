from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    matricula = fields.Char(string="Matricula")
    identidad_vehiculo = fields.Selection(string="Tipo de identidad del vehiculo",
                                          selection=[('1', 'Numero de Identificacion del vehiculo'), ('2', 'Numero de Matricula del vehiculo')])
    marca_vehiculo = fields.Char(string="Marca del vehiculo de transporte")
    responsable_flete = fields.Selection(string="Responsable del costo del flete",
                                         selection=[('1', 'Emisor de la factura electronica'), ('2', 'Receptor de la factura electronica'), ('3', 'Tercero'), ('4', 'Agente intermediario del transporte')])
    tipo_transporte = fields.Selection(string="Tipo de transporte", selection=[('1', 'Propio'), ('2', 'Tercero')])



