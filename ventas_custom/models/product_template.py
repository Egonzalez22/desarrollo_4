from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    es_muestra = fields.Boolean(string='Es Muestra')
    es_principio_activo = fields.Boolean(string='Es Principio Activo')
    es_metodo = fields.Boolean(string='Es Método')
    
    metodologia_ids = fields.Many2many('ventas.metodologia', string='Metodología')
    #metodos para este Producto de tipo Muestra
    metodos = fields.Many2many(
            'product.template',
            'product_template_metodos_rel',
            'product_id', 
            'metodo_id', 
            string="Métodos", 
            domain=[('es_metodo', '=', True)]
        )
    
    requisitos = fields.Html(string='Requisitos de metodología')
    presentacion = fields.Char(string='Presentación')

    acreditado = fields.Boolean(string='Acreditado')
    referencia_bibliografica = fields.Char(string='Referencia Bibliográfica')

    # Principios activos para muestras
    principios_activos_ids = fields.Many2many('product.template', 'product_template_principios_activos_rel', 'principio_activo_id', 'producto_id', string='Principios Activos', domain=[('es_principio_activo', '=', True)])

    # Equipos para metodos
    equipos = fields.Many2many('maintenance.equipment', string="Equipos")


    def _custom_get_pricelists(self):
        self.ensure_one()
        domain = ['|',
            ('product_tmpl_id', '=', self.id),
            ('product_id', 'in', self.product_variant_ids.ids)]
        pl_list =  self.env['product.pricelist.item'].search(domain)
        return pl_list

    @api.model
    def write(self, values):

        # Si el producto es una muestra, el producto debe ser del tipo almacenable y el seguimiento de stock debe ser por serie
        if 'es_muestra' in values:
            if values['es_muestra']:
                values['type'] = 'product'
                # Se comenta la obligatoriedad de que el seguimiento sea por serie
                # values['tracking'] = 'serial'
        return super(ProductTemplate, self).write(values)
    
    @api.onchange('metodologia_ids')
    def _onchange_metodologia_id(self):
        """
        Método para limpiar los metodos no relacionados a las metodologias seleccionadas
        """
        for metodo in self.metodos:
            if metodo.metodologia_ids not in self.metodologia_ids:
                self.metodos -= metodo