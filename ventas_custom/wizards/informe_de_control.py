from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WizardInformeControl(models.TransientModel):
    _name = "wizard_informe_control"
    _description = "Wizard para reporte de informe de control"

    grupo_analisis = fields.Many2one("ventas.grupo", string="Grupo de análisis", domain="[('tipo_documento', '=', 'Informe de control')]", required=True)
    fecha_desde = fields.Date(string="Desde", required=True)
    fecha_hasta = fields.Date(string="Hasta", required=True)
    tipo_metodo = fields.Selection([
        ("todos", "Todos"),
        ("por_metodos", "Por métodos")
    ], string="Tipo", default="todos")

    metodos_ids = fields.Many2many(
        "product.template", 
        string="Métodos",
        domain="[('id', 'in', metodos_permitidos_ids)]"
    )

    ordenes_ids = fields.Many2many(
        "sale.order", 
        string="Ordenes", 
    )

    metodos_permitidos_ids = fields.Many2many(
        "product.template", 
        'wizard_informe_control_metodos_permitidos_rel',
        string="Métodos Permitidos"
    )

    @api.onchange('grupo_analisis', 'fecha_desde', 'fecha_hasta')
    def _onchange_filtro_metodos(self):
        if not all([self.grupo_analisis, self.fecha_desde, self.fecha_hasta]):
            return
            
        ordenes = self.env['sale.order'].search([
            ('grupo_id.tipo_grupo', '=', self.grupo_analisis.tipo_grupo),
            ('date_order', '>=', self.fecha_desde),
            ('date_order', '<=', self.fecha_hasta),
            ('order_line.product_id.product_tmpl_id.es_metodo', '!=', False)
        ])
        
        if ordenes:
            self.metodos_permitidos_ids = ordenes.muestras_ids.metodos_ids
            self.ordenes_ids = ordenes
        else:
            self.metodos_permitidos_ids = False
            self.ordenes_ids = False

    def action_print_pdf(self):
        data = {
            'grupo_analisis': self.grupo_analisis.id,
            'fecha_desde': self.fecha_desde,
            'fecha_hasta': self.fecha_hasta,
            'tipo_metodo': self.tipo_metodo,
            'metodos_ids': self.metodos_ids.ids if self.metodos_ids else [],
            'ordenes_ids': self.ordenes_ids.ids if self.ordenes_ids else []
        }

        return self.env.ref('ventas_custom.informe_control_pdf').report_action(self, data=data)
    
    def action_print_excel(self):
        data = {
            'grupo_analisis': self.grupo_analisis.id,
            'fecha_desde': self.fecha_desde,
            'fecha_hasta': self.fecha_hasta,
            'tipo_metodo': self.tipo_metodo,
            'metodos_ids': self.metodos_ids.ids if self.metodos_ids else [],
            'ordenes_ids': self.ordenes_ids.ids if self.ordenes_ids else []
        }

        return self.env.ref('ventas_custom.informe_control_xlsx').report_action(self, data=data)
    
    def action_cancel(self):
        return {"type": "ir.actions.act_window_close"}