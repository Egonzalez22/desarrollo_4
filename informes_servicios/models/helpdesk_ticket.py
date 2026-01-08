# -*- coding: utf-8 -*-

from odoo import api, fields, models
import locale
from odoo import models, api, fields, exceptions,_
import logging
_logger = logging.getLogger(__name__)

condicion = """
"""

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    cotizacion_nro = fields.Char(string="Cotización Nro")
    invoice_id = fields.Many2one('account.move', string="Factura", copy=False)

   
    descripcion_calificacion = fields.Html(string='Descripción Calificación', default=condicion)
    atencion_de = fields.Many2one('res.partner', string='Atención de', domain="[('parent_id', '=', partner_id)]")
    nro_contrato = fields.Char(string='Nro. Contrato')
    
    # TODO: Ver si se puede utilizar la hoja de trabajo
    # piezas_cambiadas = fields.Html(string='Piezas Cambiadas')

    # Obtenemos el empleado asociado al usuario
    # TODO: Cambiar esta funcion, se puede obtener directo desde la relacion de employee y en el xml
    def get_employee(self):
        """
        Obtenemos el empleado asociado al usuario y retornamos el nombre y puesto
        """
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if not employee:
            return ""

        nombre = employee.name if employee.name else self.env.user.name
        puesto = employee.job_title

        return [nombre, puesto]