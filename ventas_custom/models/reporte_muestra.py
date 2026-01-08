from odoo import models, fields, api, exceptions, _

class ReporteMuestra(models.AbstractModel):
    _name = 'report.ventas_custom.reporte_muestra'
    _description = 'Reporte de Muestra Normalizado'

    @api.model
    def _get_report_values(self, docids, data=None):
        if docids:
            picking_id = docids[0]
        else:
            picking_id = data.get('picking_id')

        docs = self.env['stock.picking'].sudo().browse(picking_id)
        sale_order = self.env['sale.order'].sudo().search([('name','=',docs.origin)], limit=1)
        muestra_grupo_id = self.env['ventas.grupo'].sudo().search([
            ('tipo_grupo', '=', sale_order.grupo_id.tipo_grupo),
            ('tipo_documento', '=', 'Solicitud de Análisis de Muestras'),
            ('company_id', '=', sale_order.company_id.id),
            ('fecha_desde', '<=', fields.Date.today()),
            '|',('fecha_hasta', '>=', fields.Date.today()),('fecha_hasta', '=', False)
        ], limit=1)

        return {
            'doc_ids': docids,
            'docs':  docs,
            'doc_model': 'stock.picking',
            'sale_order': sale_order,
            'muestra_grupo_id': muestra_grupo_id,
        }