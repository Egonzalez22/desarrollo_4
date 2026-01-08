from odoo import fields, models, api
from lxml import etree

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    resultado_alta_ids = fields.One2many('resultado.alta', 'workorder_id', string="Resultados Alta Complejidad")
    resultado_farma_ids = fields.One2many('resultado.farma', 'workorder_id', string="Resultados Farma")
    resultado_toxi_ids = fields.One2many('resultado.toxi', 'workorder_id', string="Resultados Toxicológico")
    resultado_agro_ids = fields.One2many('resultado.agro', 'workorder_id', string="Resultados Agroquímico")

    tipo_grupo = fields.Selection([
        ('toxicologico', 'Toxicológico'),
        ('farma', 'Farma'),
        ('alta_complejidad', 'Alta Complejidad'),
        ('agroquimico', 'Agroquímico'),
    ], string='Tipo de Presupuesto', related="production_id.tipo_grupo")

    show_results_page = fields.Boolean(string="Mostrar página de resultados", default=False, copy=False)

    def get_workorder_data(self):
        data = super().get_workorder_data()
        if self.resultado_alta_ids:
            data['views']['resultados_view'] = self.env.ref('modulo_pharma.res_alta_complejidad_form_tablet').id
            data['resultados'] = self.resultado_alta_ids.ids
            data['res_model'] = 'resultado.alta'
        elif self.resultado_farma_ids:
            data['views']['resultados_view'] = self.env.ref('modulo_pharma.res_farma_form_tablet').id
            data['resultados'] = self.resultado_farma_ids.ids
            data['res_model'] = 'resultado.farma'
        elif self.resultado_toxi_ids:
            data['views']['resultados_view'] = self.env.ref('modulo_pharma.res_toxicologico_form_tablet').id
            data['resultados'] = self.resultado_toxi_ids.ids
            data['res_model'] = 'resultado.toxi'
        elif self.resultado_agro_ids:
            data['views']['resultados_view'] = self.env.ref('modulo_pharma.res_agroquimico_form_tablet').id
            data['resultados'] = self.resultado_agro_ids.ids
            data['res_model'] = 'resultado.agro'
        else:
            data['resultados'] = []
            data['tipo_grupo'] = False

        data['tipo_grupo'] = self.tipo_grupo
        return data

    @api.model_create_multi
    def create(self, values):
        res = super().create(values)
        for record in res:
            record.cargarResultados()
        return res

    def cargarResultados(self):
        if self.workcenter_id.code == 'FINAL':
            if self.tipo_grupo == 'alta_complejidad':
                for sa in self.product_id.product_tmpl_id.sustancias_activas_ids:
                    vals = {
                        'workorder_id': self.id,
                        'sustancia_activa_id': sa.id,
                        'lod': sa.lod,
                        'intervalo_referencia': sa.intervalo_referencia
                    }
                    self.write({'resultado_alta_ids': [(0, 0, vals)]})
            elif self.tipo_grupo == 'farma' or self.tipo_grupo == 'agroquimico':
                order = self.env['sale.order'].search([('company_id', '=', self.company_id.id),
                                                       ('grupo_id.tipo_grupo', '=', self.tipo_grupo),
                                                       ('state', '=', 'sale'),
                                                       ('name', '=', self.production_id.origin)], limit=1)
                for m in order.muestras_ids:
                    if m.muestra_id in self.production_id.muestra_id and self.product_id.product_tmpl_id in m.metodos_ids:
                        for pa in order.mapped('muestras_ids.principios_activos_ids'):
                            vals = {
                                'workorder_id': self.id,
                                'principio_activo_id': pa.id
                            }
                            if self.tipo_grupo == 'farma':
                                self.write({'resultado_farma_ids': [(0, 0, vals)]})
                            else:
                                self.write({'resultado_agro_ids': [(0, 0, vals)]})
            elif self.tipo_grupo == 'toxicologico':
                for sa in self.product_id.product_tmpl_id.sustancias_activas_ids:
                    vals = {
                        'workorder_id': self.id,
                        'sustancia_activa_id': sa.id
                    }
                    self.write({'resultado_toxi_ids': [(0, 0, vals)]})
            self.write({'show_results_page': True})


