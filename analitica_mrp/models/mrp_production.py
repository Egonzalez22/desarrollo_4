from odoo import _, api, fields, models


class MRPProduction(models.Model):
    _inherit = 'mrp.production'
    _rec_names_search = ['name', 'codigo_muestra']

    muestra_id = fields.Many2one("product.product",string="Muestra")
    muestra_lot_id = fields.Many2one("stock.lot","Nro. lote muestra",compute="compute_muestra")
    codigo_muestra = fields.Char(string="Código de muestra")
    codigo_muestra_compute = fields.Char(string="Código de muestra", compute="compute_muestra")
    cantidad_muestra = fields.Float(string="Cant. muestra")
    grupo_id = fields.Many2one("ventas.grupo",string="Grupo")
    fecha_estimada_entrega = fields.Datetime(string="Fecha a Entregar", compute="_compute_fecha_estimada_entrega")
    tipo_grupo = fields.Selection([
        ('toxicologico', 'Toxicológico'),
        ('farma', 'Farma'),
        ('alta_complejidad', 'Alta Complejidad'),
        ('agroquimico', 'Agroquímico'),
    ], string='Tipo de Presupuesto', related="grupo_id.tipo_grupo")

    def write(self,vals):
        if vals.get('cantidad_muestra'):
            for record in self:
                if len(record.move_raw_ids)==1:
                    record.move_raw_ids.write({'product_uom_qty':vals.get('cantidad_muestra')})
                    record.move_raw_ids.move_line_ids.write({'qty_done':vals.get('cantidad_muestra')})
        return super(MRPProduction,self).write(vals)

    def open_mrp_form(self):
        return{
            'name':_("Products to Process"),
            'view_mode': 'form',
            'view_id':self.env.ref('mrp.mrp_production_form_view').id,
            'res_model': 'mrp.production',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
        }

    def compute_muestra(self):
        for record in self:
            record.muestra_id=False
            record.muestra_lot_id=False
            record.codigo_muestra=False
            record.codigo_muestra_compute=False

            if record.move_raw_ids and len(record.move_raw_ids)==1:
                if record.move_raw_ids.move_line_ids and len(record.move_raw_ids.move_line_ids)==1:
                    if record.move_raw_ids.move_line_ids.codigo_muestra:
                        record.write({'muestra_id':record.move_raw_ids.move_line_ids.product_id.id})
                        record.muestra_lot_id=record.move_raw_ids.move_line_ids.lot_id
                        record.codigo_muestra=record.move_raw_ids.move_line_ids.codigo_muestra
                        record.codigo_muestra_compute=record.move_raw_ids.move_line_ids.codigo_muestra

    def _compute_fecha_estimada_entrega(self):
        for record in self:
            picking_type = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
            picking = self.env['stock.picking'].search([
                ('origin', '=', record.origin),
                ('picking_type_id', '=', picking_type.id)
            ], limit=1)
            record.fecha_estimada_entrega = picking.scheduled_date if picking else False

    def name_get(self):
        context = self.env.context
        custom_name = context.get('name', False)
        result = []
        if custom_name:
            name = custom_name
        else:
            name = self._rec_name
        name = 'codigo_muestra'
        if name in self._fields:
            convert = self._fields[name].convert_to_display_name
            for record in self:
                convert_name = convert(record[name], record)
                if not convert_name:
                    name = self._rec_name
                    result.append((record.id, convert(record[name], record) or ""))
                else:
                    result.append((record.id, convert_name or ""))
        else:
            for record in self:
                result.append((record.id, "%s,%s" % (record._name, record.id)))
        return result
    