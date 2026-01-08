from odoo import _, api, fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    es_documento_electronico = fields.Boolean(string="Es documento electrónico", default=False, copy=False)
    tipo_documento_electronico=fields.Selection(string="Tipo de documento electrónico",selection=[('out_invoice','Factura de cliente'),
                                                                                                  ('out_refund','Nota de crédito de cliente'),
                                                                                                  ('nota_remision','Nota de remisión de cliente'),
                                                                                                  ('nota_debito','Nota de débito'),
                                                                                                  ('autofactura','Autofactura')])
    encabezado_kude_img=fields.Binary(string="Encabezado KuDE", help="Tamaño recomendado 1000px x 250px. Puede ser menor o mayor, manteniendo el ratio de 4")

    habilitar_datos_establecimiento = fields.Boolean(string="Habilitar datos de establecimiento", default=False, copy=False)
    nombre_establecimiento = fields.Char(string="Nombre del establecimiento", help="Nombre del establecimiento", copy=False)
    direccion_establecimiento = fields.Char(string="Dirección del establecimiento", help="Dirección del establecimiento", copy=False)
    telefono_establecimiento = fields.Char(string="Teléfono del establecimiento", help="Teléfono del establecimiento", copy=False)
    ciudad_establecimiento = fields.Char(string="Ciudad del establecimiento", help="Ciudad del establecimiento", copy=False)
    actividad_economica_ids = fields.Many2many('fe.actividad_economica', string="Actividades económicas", copy=False)