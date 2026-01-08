# -*- coding: utf-8 -*-

from odoo import api, fields, models
import locale
from odoo import models, api, fields, exceptions,_
import logging
_logger = logging.getLogger(__name__)

condicion = """
<p>1. <strong>Precio:</strong> Los precios incluyen el IVA.</p>
<p>2. <strong>Plazo de entrega:</strong> Inmediata (En stock, salvo venta interin), previa confirmación de compra mediante Orden de Compra.</p>
<p>3. <strong>Forma de pago:</strong> Factura credito a 30 dias, luego de la entrega de los productos.</p>
<p>4. <strong>Validez de la oferta:</strong> 20 (veinte) días, luego de este plazo sujeto a revisión. <br></p>
"""

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_default_cotizacion_nro(self):
        seq = self.env['ir.sequence'].sudo().next_by_code('seq_cotizacion_nro_informes_presupuestos')
        return seq

    @api.model
    def _get_default_cotizacion_calificativo_nro(self):
        seq = self.env['ir.sequence'].sudo().next_by_code('seq_cotizacion_calificativo_nro_informes_presupuestos')
        return seq

    # La cotizacion comparte entre los informes preventivo y correctivo
    cotizacion_nro = fields.Char(string='Cotización Nro', default=_get_default_cotizacion_nro, copy=False)
    cotizacion_calificativo_nro = fields.Char(string='Cotización Nro', default=_get_default_cotizacion_calificativo_nro, copy=False)
    codigo_calidad = fields.Char(string='Código de calidad', default="SU-RE-072 V.03")
    vigencia_calidad = fields.Char(string='Vigencia', default="25/10/2023")
    departamento = fields.Char(string='Departamento')
    # Obtenemos los partners relacionados al partner seleccionado
    atencion_de = fields.Many2one('res.partner', string='Atención de', domain="[('parent_id', '=', partner_id)]")

    tipo_presupuesto = fields.Selection([
        ('analitico', 'Analítico'),
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
        ('calificativo', 'Calificativo'),
    ],
        string='Tipo de presupuesto',
        default='analitico'
    )

    titulo = fields.Char(string='Título')
    observacion = fields.Html(string='Observación')
    condicion = fields.Html(string='Condición', default=condicion)

    def get_cotizacion_format(self):
        """
        Obtenemos los dos ultimos digitos del año actual
        """
        year = fields.Date.today().strftime('%y')
        cotizacion = f"{self.cotizacion_nro}/{year}"
        return cotizacion

    def get_current_date(self):
        """
        Obtenemos la fecha actual en formato dd de MMMM del YYYY
        """
        # Establecemos el locale
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

        # Generamos la fecha actual y retornamos
        return fields.Date.today().strftime('%d de %B del %Y')
    
    def get_formatted_date_order(self):
        """
        Formateamos la fecha de la orden en formato "dd de MMMM del YYYY"
        """
        # Aseguramos que el locale está configurado a español
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        
        # Convertimos la fecha de `date_order` a un objeto datetime si no lo es
        if self.date_order:
            # Formateamos la fecha en el formato deseado
            return self.date_order.strftime('%d de %B del %Y')
        return ''

    def get_related_partner(self):
        """
        En el caso de que el cliente tenga un contacto relacionado, retornamos el nombre completo del contacto
        """
        # if self.atencion_de:
        #     return self.atencion_de.name
        # else:
        return self.partner_id.name

    def get_amount_format(self, amount, currency=None):
        """
        Formateamos el monto con separadores de miles y decimales
        """
        # Formateamos con separadores de miles y decimales
        if currency and currency.name == 'PYG':
            amount = "{:,.0f}".format(amount).replace(',', '.')
            return amount

        # Si no hay currency o es diferente a PYG, formateamos con 2 decimales
        amount = "{:,.2f}".format(amount).replace(',', 'X').replace('.', ',').replace('X', '.')
        return amount

    def amount_to_text(self, monto):
        """
        Convertimos el monto a texto
        """

        return self.env['interfaces_tools.tools'].numero_a_letra(monto)

    # Obtenemos el empleado asociado al usuario
    def get_employee(self):
        """
        Obtenemos el empleado asociado al usuario y retornamos el nombre y puesto
        """
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if not employee:
            return ['', '']

        nombre = employee.name if employee.name else self.env.user.name
        puesto = employee.job_title

        return [nombre, puesto]