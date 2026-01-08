import datetime
import logging

from odoo import _, exceptions, fields, models

_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = 'product.template'

    codigo_dncp_general = fields.Char(string="Código de la DNC General", copy=False)
    codigo_dncp_especifico = fields.Char(string="Código de la DNC Específico", copy=False)