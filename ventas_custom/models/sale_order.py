from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderMuestras(models.Model):
    _name = 'ventas.muestras'
    _description = 'Muestras de un presupuesto de venta'

    sale_id = fields.Many2one('sale.order', string='Presupuesto')
    muestra_id = fields.Many2one('product.product', string='Muestra', domain="[('es_muestra', '=', True)]")
    metodos_ids = fields.Many2many('product.template', string='Métodos')
    #metodos_id = fields.Many2many('ventas.muestras.line', 'muestra_id', string='Métodos de la muestra')
    metodologia_ids = fields.Many2many('ventas.metodologia', string='Metodología', readonly=False)
    lineas_ids = fields.Many2one('sale.order.line', string='Lineas')
    cantidad = fields.Integer(string='Cantidad')
    lote_cantidad = fields.Integer(string='Cantidad Lote', default=1)
    lote_unidad_medida = fields.Char(string='Unidad de Medida Lote')
    estandard = fields.Char(string='Estandard')
    reactivos = fields.Char(string='Reactivos')
    referencia = fields.Char(string='Referencia')
    observacion = fields.Char(string='Observación')
    metodologia = fields.Char(string='Metodología')
    presentacion_id = fields.Many2one('ventas.presentacion', string='Presentación')
    motivo_id = fields.Many2one('ventas.motivo', string='Motivo')
    principios_activos_ids = fields.Many2many('product.template', 'muestra_principios_activos_rel', 'principio_activo_id', 'producto_id', string='Principios Activos', domain=[('es_principio_activo', '=', True)])

    metodos_disponibles_ids = fields.Many2many('product.template', 'metodos_disponibles_ids_rel', compute='_compute_metodos_disponibles_ids')


    @api.depends('muestra_id')
    def _compute_metodos_disponibles_ids(self):
        for record in self:
            record.metodos_disponibles_ids = False
            if record.muestra_id:
                # Obtenemos todas las lineas del presupuesto
                order_lines = self.sale_id.order_line

                # Obtenemos los métodos (productos) disponibles en las lineas de productos
                metodos_disponibles_ids = order_lines.mapped('product_template_id').ids
                record.metodos_disponibles_ids = metodos_disponibles_ids


    @api.onchange('muestra_id')
    def _onchange_muestra_id(self):
        """
        Método para establecer los principios activos, las metodologias y los metodos de la muestra
        """
        if self.muestra_id:
            self.principios_activos_ids = self.muestra_id.principios_activos_ids
            self.metodologia_ids = self.muestra_id.metodologia_ids
            self.metodos_ids = self.muestra_id.metodos
            
    @api.onchange('metodologia_ids')
    def _onchange_metodologia_id(self):
        """
        Método para limpiar los metodos no relacionados a las metodologias seleccionadas
        """
        for metodo in self.metodos_ids:
            if metodo.metodologia_ids not in self.metodologia_ids:
                self.metodos_ids -= metodo

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    referencia = fields.Char(string='Referencia', copy=False)
    grupo_id = fields.Many2one('ventas.grupo', string='Grupo')
    grupo_acreditado = fields.Boolean(string='Grupo Acreditado', related='grupo_id.es_acreditado')
    grupo_tipo_grupo = fields.Char(string='Tipo Grupo', compute='_compute_tipo_grupo')
    metodologia_analisis = fields.Many2one('ventas.metodologia_analisis', string='Metodología de Análisis')
    
    #Campo motivo de la pestanha Muestras para ponerlo en el form de sale_order, related para que al cambiarlo tambien
    #cambie en el modelo ventas.muestras (mantenemos el funcionamiento)
    motivo_id = fields.Many2one('ventas.motivo', related='muestras_ids.motivo_id', string='Motivo', readonly=False)
    matriz_id = fields.Many2one('ventas.matriz', related='order_line.matriz_id', string='Matriz', readonly=False)

    # Campos extras para datos de analitica
    mostrar_campos_extras = fields.Boolean(string="Mostrar campos", compute='_compute_mostrar_campos_extras')
    acreditado = fields.Boolean(string='Métodos Acreditados', default=False, help="Filtrar métodos acreditados")

    # Campos para los informes
    condicion_pharma = fields.Html(string='Condición Informe Pharma')
    equipos = fields.Html(string='Equipos')

    # Presupuesto relacionado
    sale_order_id = fields.Many2one('sale.order', string='Presupuesto relacionado', copy=False)

    # Recepcion
    stock_picking_id = fields.Many2one('stock.picking', string='Albarán', copy=False)
    stock_picking_count = fields.Integer(string='Recepción', compute='_compute_stock_picking_id')

    # Muestras
    muestras_ids = fields.One2many('ventas.muestras', 'sale_id', string='Muestras', copy=True)
    version = fields.Integer(string='Versión', default=1)
    notas = fields.Html(string='Notas')
    abreviaturas = fields.Html(string='Abreviaturas')
    equipos = fields.Html(string='Equipos')
    plazo_entrega = fields.Html(string='Plazo de Entrega')
    mantenimiento_oferta = fields.Html(string='Mantenimiento de oferta')
    entrega_resultado = fields.Html(string='Entrega de resultado')
    
    @api.onchange('motivo_id')
    def _onchage_motivo_id(self):
        """
        Método para establecer el motivo en las lineas de presupuesto al cambiar motivo_id
        """
        for record in self:
            if record.motivo_id:
                # Obtenemos el motivo de la linea
                record.muestras_ids.motivo_id = record.motivo_id
            else:
                record.muestras_ids.motivo_id  = False
                
    @api.onchange('matriz_id')
    def _onchage_matriz_id(self):
        """
        Método para establecer la matriz en las lineas de presupuesto al cambiar matriz_id
        """
        for record in self:
            if record.matriz_id:
                # Obtenemos la matriz de la linea
                record.order_line.matriz_id = record.matriz_id
            else:
                record.order_line.matriz_id  = False
    
    @api.depends('grupo_id')
    def _compute_tipo_grupo(self):
        """
        Método para calcular el tipo de grupo
        """
        for record in self:
            # Agregamos la observacion
            self.observacion = record.grupo_id.observacion
            self.notas = record.grupo_id.notas
            self.abreviaturas = record.grupo_id.abreviaturas
            self.equipos = record.grupo_id.equipos
            self.plazo_entrega = record.grupo_id.plazo_entrega
            self.mantenimiento_oferta = record.grupo_id.mantenimiento_oferta
            self.entrega_resultado = record.grupo_id.entrega_resultado
            
            if record.grupo_id.tipo_grupo:
                record.grupo_tipo_grupo = record.grupo_id.tipo_grupo
            else:
                record.grupo_tipo_grupo = ""

    @api.depends('company_id')
    def _compute_mostrar_campos_extras(self):
        """
        Método para mostrar los campos extras agregados en el sale.order.line
        """
        for record in self:
            es_visible = self.env.company.campos_personalizados_ventas
            record.mostrar_campos_extras = es_visible
   
    def action_cargar_lineas(self):
        muestras = self.muestras_ids
        for muestra in muestras:
            new_lines = []
            for metodo in muestra.metodos_ids:
                product_pricelist = self.env['product.pricelist.item'].search([
                            ('product_tmpl_id', '=' , metodo.id), 
                            ('min_quantity', '=', 1),
                            ('pricelist_id', '=', self.pricelist_id.id)], limit=1)
                
                if not product_pricelist:
                    raise ValidationError(f"No se encontró el precio del metodo en la lista de precios seleccionada. {self.pricelist_id.name} - {metodo.display_name}")
                
                new_lines.append((0, 0, {
                    'muestra_id': muestra.muestra_id.id,
                    'metodologia_id': metodo.metodologia_ids.id,
                    'product_id': metodo.product_variant_id.id,
                    'name': metodo.display_name,
                    'product_uom_qty': 1,
                    'price_unit': product_pricelist.fixed_price,
                }))
            self.write({'order_line': new_lines})
   
    def action_confirm(self):
        """
        Cuando se confirma un presupuesto, generamos la secuencia que se utiliza en los informes
        """
        res = super(SaleOrder, self).action_confirm()

        for record in self:
            if record.mostrar_campos_extras:
                # Creamos la secuencia
                seq_name = f'seq_grupo_{record.grupo_tipo_grupo}'
                secuencia = self.env['ir.sequence'].sudo().next_by_code(seq_name) 

                # Guardamos en el campo referencia
                record.referencia = secuencia
            partner = record.partner_id
            # Se agrega campos a ser validados
            required_fields = {
                'Email': partner.email,
                'Direccion': partner.street,
                'Telefono': partner.phone,
            }
            missing_fields = [field for field, value in required_fields.items() if not value]
            if missing_fields:
                raise ValidationError(
                    f"No se puede confirmar la orden porque faltan los siguientes datos del cliente: {', '.join(missing_fields)}")

        return res

    def action_crear_picking(self):
        """
        Método para llamar al método de crear picking sobre demanda
        """
        self.crear_picking()
    
    def crear_picking(self):
        """
        Método para crear un albarán al confirmar la orden de venta
        """
        # Obtenemos del parametro de sistema 
        try:
            picking_type_id = self.env['ir.config_parameter'].sudo().get_param('analitica_picking_type_id') or 34
            picking_type = self.env['stock.picking.type'].sudo().search([('id', '=', picking_type_id)], limit=1)
            nombre = picking_type.sequence_id.next_by_id()

            move_lines = []

            # Iteramos por las muestras y por la cantidad de cada muestra
            for muestra in self.muestras_ids:
                # Se crean los move lines por cada muestra y por cada lote
                # Ej.: 30 unidades = 3 blisters de 10 unidades
                # En reunión del 23-05-24 Con Walter, Mercedes y Edgar D. se definió no crear un stock.move por lote
                # En conversación con Walter 23-05-24, se definió volver a agregar la creación de un stock.move por lote

                # Se genera un código diferente por cada lote de la muestra
                # El código de muestra ya no se genera aqui, debe ser por stock.move.line
                # codigo_muestra = self.generar_codigo_muestra(muestra)

                for lote in range(muestra.lote_cantidad):
                    # Agregamos un move line por cada lote 
                    move_lines.append((0, 0, {
                        'location_id': picking_type.default_location_src_id.id,
                        'location_dest_id': picking_type.default_location_dest_id.id,
                        'name': nombre,
                        'product_id': muestra.muestra_id.id,
                        'product_uom_qty': muestra.cantidad,
                        'product_uom': muestra.muestra_id.uom_id.id,
                        'motivo_id': self.motivo_id,
                        'presentacion_id': muestra.presentacion_id,
                        # 'codigo_muestra': codigo_muestra,
                        'metodos_ids': [(6, 0, muestra.metodos_ids.ids)],
                        "grupo_id": self.grupo_id.id,
                    }))

            picking_dict = {
                'name': f"{picking_type.sequence_code}{self.name}",
                'partner_id': self.partner_id.id,
                'user_id': False,
                'origin': self.name,
                'date': self.date_order,
                'picking_type_id': picking_type_id,
                'company_id': self.company_id.id,
                'location_id': picking_type.default_location_src_id.id,
                'location_dest_id': picking_type.default_location_dest_id.id,
                'move_ids_without_package': move_lines,
            }

            picking_obj = self.env['stock.picking'].create(picking_dict)
            self.stock_picking_id = picking_obj.id
        except Exception as e:
            print(e)
            pass

    @api.depends('stock_picking_id')
    def _compute_stock_picking_id(self):
        for order in self:
            order.stock_picking_count = len(order.stock_picking_id)

    def action_ver_picking_recepcion(self):
        return self._get_action_view_picking(self.stock_picking_id)

    @api.onchange('sale_order_template_id')
    def _onchange_sale_order_template_id(self):
        """
        Método para actualizar los campos html de los informes segun la plantilla seleccionada
        """
        if self.sale_order_template_id:
            self.condicion_pharma = self.sale_order_template_id.condicion_pharma
            self.equipos = self.sale_order_template_id.equipos

    def copy(self, default=None):
        """
        Método para establecer el campo sale_order_id al duplicar un presupuesto
        """
        if default is None:
            default = {}
        default['sale_order_id'] = self.id
        default['version'] = self.version + 1

        return super(SaleOrder, self).copy(default)

    def action_imprimir_presupuesto(self):
        """
        Método para imprimir el presupuesto
        """
        # TODO: Ver si se controla aca la versión del presupuesto

        tipo_grupo = self.grupo_id.tipo_grupo

        # Farma
        if tipo_grupo == 'farma':
            presupuesto_pdf = self.env.ref('ventas_custom.presupuesto_farma_action').report_action(self)

        # Toxicologico
        elif tipo_grupo == 'toxicologico':
            presupuesto_pdf = self.env.ref('ventas_custom.presupuesto_toxicologico_action').report_action(self)
        
        # Alta Complejidad
        elif tipo_grupo == 'alta_complejidad':
            presupuesto_pdf = self.env.ref('ventas_custom.presupuesto_alta_complejidad_action').report_action(self)

        # Agroquimico
        elif tipo_grupo == 'agroquimico':
            presupuesto_pdf = self.env.ref('ventas_custom.presupuesto_agroquimico_action').report_action(self)
        
        return presupuesto_pdf

    def informe_get_related_partner(self):
        """
        En el caso de que el cliente tenga un contacto relacionado, retornamos el nombre completo del contacto
        """
        partner = self.partner_id
        parent =  partner.parent_id

        if self.partner_id.parent_id:
            return self.partner_id.parent_id.name
        else:
            return ""

    def informe_obtener_version(self):
        """
        Método para obtener la versión del presupuesto
        """
        today = datetime.now()
        today_str = today.strftime('%Y%m')
        return f"{today_str}{self.referencia}-{self.version}"

    
    def informe_obtener_precio_metodo(self, muestra, metodo):
        """
        Se obtiene el precio del metodo, obteniendo el precio unitario de la linea y multiplicando por la cantidad de lotes de la muestra
        """
        precio_unitario = 0
        for line in self.order_line:
            if line.product_template_id.id == metodo.id:
                precio_unitario = line.price_unit

        total = precio_unitario * muestra.lote_cantidad

        return total
    
    def informe_obtener_cantidad_muestras(self):
        """
        Método para obtener la cantidad total de muestras
        """
        cantidad = 0
        for muestra in self.muestras_ids:
            cantidad += muestra.lote_cantidad

        return cantidad