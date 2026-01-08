from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    reporte_libro_inventario_base_report_bg = fields.Many2one(
        'account.report',
        string='Reporte base para el Balance General',
        related='company_id.reporte_libro_inventario_base_report_bg',
        help='Estructura de reportes que se utilizará para el Balance General en el reporte de Libro Inventario',
        readonly=False
    )
    reporte_libro_inventario_base_report_er = fields.Many2one(
        'account.report',
        string='Reporte base para el Estado de Resultados',
        related='company_id.reporte_libro_inventario_base_report_er',
        help='Estructura de reportes que se utilizará para el Estado de Resultados en el reporte de Libro Inventario',
        readonly=False
    )
