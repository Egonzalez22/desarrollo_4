from odoo import _, api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
        
    def _action_done(self):
        res=super(StockPicking,self)._action_done()
        for picking in self:
            if picking.origin:
                order_id=self.env['sale.order'].search([('name','=',picking.origin)])
                if order_id:
                    muestra_lines=picking.move_ids.mapped('move_line_ids')
                    for muestra in muestra_lines:
                        for line in order_id.order_line.filtered(lambda x: x.muestra_id == muestra.product_id):
                            product_id=self.env['product.product'].search([('product_tmpl_id','=',line.product_template_id.id)])
                            for i in range(int(line.product_uom_qty)):
                                if product_id and product_id.bom_ids:
                                    mrp_prod={
                                        'product_id':product_id.id,
                                        'bom_id':product_id.bom_ids[0].id,
                                        'product_qty':1,
                                        'date_planned_start':fields.Datetime.now(),
                                        'company_id':self.env.company.id,
                                        'grupo_id':order_id.grupo_id.id,
                                        'muestra_id':muestra.product_id.id,
                                        'move_raw_ids':[(0,0,{
                                            'product_id':muestra.product_id.id,
                                            'product_uom':muestra.product_uom_id.id,
                                            'product_uom_qty':0
                                        })]    
                                    }
                                    mrp_production_id=self.env['mrp.production'].create(mrp_prod)
                                    if mrp_production_id:
                                        mrp_production_id.action_confirm()
                                        mrp_production_id.move_raw_ids.write({'move_line_ids':[(0,0,
                                            {'product_id':muestra.product_id.id,
                                            'lot_id':muestra.lot_id.id,
                                            'product_uom_id':muestra.product_uom_id.id,
                                            'codigo_muestra':muestra.codigo_muestra,
                                            'nro_lote':muestra.nro_lote,
                                            'fecha_vencimiento_lote':muestra.fecha_vencimiento_lote,
                                            'observaciones':muestra.observaciones})]})
        return res
