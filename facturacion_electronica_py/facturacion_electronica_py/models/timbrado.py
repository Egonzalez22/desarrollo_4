from odoo import _, api, fields, models, exceptions


class InterfacesTimbrado(models.Model):
    _inherit = 'interfaces_timbrado.timbrado'

    tipo_documento = fields.Selection(
        string="Tipo de documento",
        selection=[
            ('out_invoice', 'Factura'),
            ('out_refund', 'Nota de credito'),
            ('nota_remision', 'Nota de remision'),
            ('autofactura', 'Autofactura'),
            ('nota_debito', 'Nota de débito'),
        ],
        default="out_invoice",
    )

    # Campos relacionados a sifen
    idcsc = fields.Char(string='ID del CSC')
    csc = fields.Char(string='CSC')
    serie = fields.Char('Serie', required=False)
