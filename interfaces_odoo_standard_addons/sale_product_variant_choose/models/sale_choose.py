from odoo import _, api, fields, models



class VariantChoose(models.TransientModel):
    _name = 'sale.product.variant.choose'
    _description = 'Eleccion de productos'
    
    
    order_id = fields.Many2one('sale.order',string="Orden",required=True)
    product_template_id=fields.Many2one("product.template",string="Plantilla de producto")
    default_code=fields.Char(string="Código")
    line_ids=fields.One2many('sale.product.variant.choose.line','choose_id',string="Lineas")
    
    @api.depends('default_code')
    @api.onchange('default_code')
    def buscar_producto(self):
        if self.default_code!=False and self.default_code!="":
            product_ids=self.env['product.product'].search([('default_code','ilike',self.default_code)])
        else:
            product_ids=False
        if product_ids:
            new_lines=[]
            self.line_ids=[(5,0,0)]
            for variant in product_ids:
                line={
                    'product_id':variant.id,
                    'product_price':variant.list_price,
                    'product_stock':variant.qty_available
                    
                }
                new_lines.append((0,0,line))
            self.write({'line_ids':new_lines})
        else:
            self.line_ids=[(5,0,0)]
    
    
    @api.onchange('product_template_id')
    @api.depends('product_template_id')
    def onchange_template(self):
        if self.product_template_id:
            new_lines=[]
            self.line_ids=[(5,0,0)]
            for variant in self.product_template_id.product_variant_ids:
                line={
                    'product_id':variant.id,
                    'product_price':variant.list_price,
                    'product_stock':variant.qty_available
                    
                }
                new_lines.append((0,0,line))
            self.write({'line_ids':new_lines})
        else:
            self.line_ids=[(5,0,0)]
      
    @api.depends('line_ids','line_ids.product_id')      
    def button_confirm(self):
        new_lines=[]
        for line in self.line_ids.filtered(lambda x:x.quantity>0):
            new_line={
                'product_id':line.product_id.id,
                'name':line.product_id.display_name,
                'product_uom_qty':line.quantity,
                'price_unit':line.product_price,
                'tax_id':[(6,0,line.product_id.taxes_id.ids if line.product_id.taxes_id else [])]
            }
            new_lines.append((0,0,new_line))
        self.order_id.write({'order_line':new_lines})
    
    
class VariantChooseLine(models.TransientModel):
    _name = 'sale.product.variant.choose.line'
    _description = 'Eleccion de productos'
    
    choose_id=fields.Many2one("sale.product.variant.choose")
    product_id=fields.Many2one('product.product',string="Producto")
    product_image=fields.Binary(string="Imagen",related="product_id.image_1920")
    product_stock=fields.Float(string="Stock actual")
    product_price=fields.Float(string="Precio de lista")
    quantity=fields.Float(string="Cantidad")
    total=fields.Char(string="Total",compute="compute_total")
    
    @api.depends('quantity','product_price')
    @api.onchange('quantity','product_price')
    def compute_total(self):
        for i in self:
            if i.quantity and i.product_price:
                i.total=i.quantity * i.product_price
            else:
                i.total=0
                