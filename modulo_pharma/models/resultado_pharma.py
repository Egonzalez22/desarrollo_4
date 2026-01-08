from odoo import models, fields, api
import locale


class ResultadosPharma(models.Model):
    _name = 'resultados.pharma'
    _rec_name = 'numero_certificado'

    name = fields.Char()
    acta_muestreo = fields.Char(string="Acta de Muestreo") 
    descripcion = fields.Char(string="Descripción") 
    analizado_por = fields.Many2one('hr.employee', string="Analizado por")
    equipos = fields.Many2many('maintenance.equipment', string="Equipos utilizados")
    metodologia = fields.Many2one('ventas.metodologia_analisis', string='Metodología de Análisis')
    periodo_desde = fields.Date(string="Periodo de Análisis desde") 
    periodo_hasta = fields.Date(string="Periodo de Análisis hasta") 
    detalle_pharma_line = fields.One2many('resultados.pharma.detalle', 'resultado_pharma_id', string='Principio Activo')
    presupuesto = fields.Many2one('sale.order', string="Presupuesto")
    detalle_pharma_order = fields.One2many('resultados.pharma.sale', 'resultado_pharma_id', string='Principio Activo')
    ph = fields.Char(string="PH")
    densidad = fields.Char(string="Densidad")
    numero_certificado = fields.Char()
    muestra_lote = fields.Many2one('stock.move', string="Muestra - Lote")
    state = fields.Selection(
        string='Estado',
        selection=[
            ('draft', 'Borrador'),
            ('posted', 'Publicado'),
        ],
        default="draft",
    )
    observacion = fields.Html()
    forma_farma = fields.Many2one('ventas.presentacion', string="Forma Farmacéutica", compute='_compute_forma_farma')
    principios_activos_descripcion = fields.Char()
    lote = fields.Many2one('stock.lot', string='Lote/N° de serie')
    fecha_vencimiento_lote = fields.Date()
    cantidad_lote =  fields.Float()
    muestra_lote_line = fields.Many2one('stock.move.line', string="Código de muestra")

    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)

    # def muestra_lote_get(self):
    #     res = []
    #     for record in self:
    #         # As I understood prj_id it is many2one field. For example I set name of prj_id
    #         res.append((record.id, record.codigo_muestra))
    #     return res
    


    @api.onchange('presupuesto')
    def seleccion_muestra(self):
        if self.presupuesto:

            move_ids = self.presupuesto.stock_picking_id.move_ids
            domain = [('id', 'in', move_ids.ids)]
            # muestra_lote_names = [(f"{move.id} - {move.codigo_muestra}") for move in move_ids]
            # print("ll: ", muestra_lote_names)
            # return {'domain': {'muestra_lote': domain}, 'value': {'muestra_lote': muestra_lote_names}}
            return {'domain': {'muestra_lote': domain}, 'value': {'muestra_lote': False}}
        else:
            # Si no se selecciona un presupuesto, limpiar el campo 'muestra_lote'
            return {'domain': {'muestra_lote': []}}

                

    @api.onchange('muestra_lote', 'presupuesto')
    def _compute_forma_farma(self):
        if self.muestra_lote and self.presupuesto:
            for muestra in self.presupuesto.muestras_ids:
                if muestra.muestra_id.id == self.muestra_lote.product_id.id:
                    if muestra.presentacion_id:
                        self.forma_farma = muestra.presentacion_id.id
                    else:
                        self.forma_farma = False
                    
                    if muestra.estandard:
                         self.principios_activos_descripcion = muestra.estandard
                    else:
                        self.principios_activos_descripcion = False
                    return
                
        self.forma_farma = False 
        self.principios_activos_descripcion = False
        
    @api.onchange('muestra_lote', 'presupuesto', 'lote')
    def agregar_lineas_sale(self):
        if self.muestra_lote and self.presupuesto and self.lote and self.muestra_lote_line:
            self.update({'detalle_pharma_line': [(5, 0, 0)]})
            self.update({'detalle_pharma_order': [(5, 0, 0)]})
            #Buscamos el lote y tomamos el id mayor para obtener el lote y el vencimiento guardamos en una variable para poder agregar a la linea
            linea = self.env['stock.move.line'].search([('move_id', '=', self.muestra_lote.id), 
                                                        ('lot_id', '=', self.lote.id)])
            
            


            if linea:
                id_line_move = max(linea)
               
                if id_line_move.nro_lote:
                    lote_num = id_line_move.nro_lote
                else:
                    lote_num = ''

                if id_line_move.fecha_vencimiento_lote:
                    vencimiento_lote = id_line_move.fecha_vencimiento_lote
                else:
                    vencimiento_lote = ''
                
                if id_line_move.qty_done:
                    cantidad_move = id_line_move.qty_done
                else:
                    cantidad_move = ''
                    
            else:
                lote_num = ''
                vencimiento_lote = ''
                cantidad_move = ''
            
            if vencimiento_lote:
                self.fecha_vencimiento_lote = vencimiento_lote
            
            if cantidad_move:
                self.cantidad_lote = cantidad_move
                


            for muestra in self.presupuesto.muestras_ids:
                if  muestra.muestra_id.id == self.muestra_lote.product_id.id:
                    if muestra.principios_activos_ids:
                        for principio1 in muestra.principios_activos_ids:
                            new_line1 = {
                                    'principios_activos': principio1.id,
                                    'lote':lote_num,
                                    'vencimiento':vencimiento_lote,
                                    'titulo':'',
                                    'conservacion': '',
                                    'humedad': '',
                                }
                            self.write({'detalle_pharma_line': [(0, 0, new_line1)]})    
                        
                        for metodo in muestra.metodos_ids:
                            if metodo.metodo_asociado and not metodo.es_metodo:
                                for principio in muestra.principios_activos_ids:
                                    if principio.id:
                                        new_line = {
                                            'ensayo_muestra_line': metodo.id,
                                            'principio_activo': principio.id,
                                            'resultado': '',
                                            'limite_aceptacion': '',
                                            'limite_deteccion': '',
                                            # 'vencimiento':vencimiento_lote,
                                            # 'conservacion': '',
                                            # 'humedad': '',
                                            # 'lote':lote_num,
                                        }
                                        self.write({'detalle_pharma_order': [(0, 0, new_line)]})
                            
                            if metodo.es_metodo and not metodo.metodo_asociado:
                                new_line = {
                                    'ensayo_muestra_line': metodo.id,
                                    'principio_activo': '',
                                    'resultado': '',
                                    'limite_aceptacion': '',
                                    'limite_deteccion': '',
                                    # 'vencimiento':vencimiento_lote,
                                    # 'conservacion': '',
                                    # 'humedad': '',
                                    # 'lote':lote_num,
                                }
                                self.write({'detalle_pharma_order': [(0, 0, new_line)]})
                    else:
                        for metodo in muestra.metodos_ids:
                            new_line = {
                                'ensayo_muestra_line': metodo.id,
                                'principio_activo': '',
                                'resultado': '',
                                'limite_aceptacion': '',
                                'limite_deteccion': '',
                                # 'vencimiento':vencimiento_lote,
                                # 'conservacion': '',
                                # 'humedad': '',
                                # 'lote':lote_num,
                            }
                            self.write({'detalle_pharma_order': [(0, 0, new_line)]})
       

    def button_publicar(self): 
        for record in self:
            # if not record.numero_certificado:
                # seq_name = f'seq_cer_pharma'
                # secuencia = self.env['ir.sequence'].sudo().next_by_code(seq_name) 

                # Guardamos en el campo referencia
            codigo_muestra = self.muestra_lote_line.codigo_muestra
            if codigo_muestra:
                ultima_parte = codigo_muestra.split('-')[-1]
                record.numero_certificado = ultima_parte
                record.codigo_muestra_lote = codigo_muestra
                
        data = {
            'state': 'posted',
        }
        self.write(data)
    
    def button_restablecer_borrador(self):
        self.write({'state': 'draft'})
    

    def get_current_date(self):
        """
        Obtenemos la fecha actual en formato dd de MMMM del YYYY
        """
        # Establecemos el locale
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

        # Generamos la fecha actual y retornamos
        return fields.Date.today().strftime('%d de %B del %Y')

    @api.onchange('presupuesto')
    def get_metodologia(self):
        if self.presupuesto:
            if self.presupuesto.metodologia_analisis:
                self.metodologia = self.presupuesto.metodologia_analisis
            else:
                self.metodologia = False
    

    

    @api.onchange('presupuesto', 'muestra_lote', 'muestra_lote_line')
    def get_lotes(self):
        if self.presupuesto and self.muestra_lote and self.muestra_lote_line:
            lotes_agregados = self.env['resultados.pharma'].search([
                ('presupuesto', '=', self.presupuesto.id),
                ('muestra_lote', '=', self.muestra_lote.id),
                ('muestra_lote_line', '=', self.muestra_lote_line.id),
            ]).mapped('lote.id')
            num_lot = []
            consulta = self.env['stock.move.line'].search([('id','=', self.muestra_lote_line.id),
                                                           ('move_id','=', self.muestra_lote.id)])
            for dato in consulta:
                if dato.lot_id.id not in num_lot and dato.lot_id.id not in lotes_agregados:
                    num_lot.append(dato.lot_id.id)
            self.lote = False # Reinicia el valor del campo lote para que el usuario no conserve selecciones anteriores que ya no son válidas
            return {'domain': {'lote': [('id', 'in', num_lot)]}}
    

    @api.onchange('presupuesto', 'muestra_lote')
    def get_muestra_line(self):
        if self.presupuesto and self.muestra_lote:
            lotes_agregados = self.env['resultados.pharma'].search([
                ('presupuesto', '=', self.presupuesto.id),
                ('muestra_lote', '=', self.muestra_lote.id),
            ]).mapped('muestra_lote_line.id')
            num_line = []
            consulta = self.env['stock.move.line'].search([('move_id','=', self.muestra_lote.id)])
            for dato in consulta:
                if dato.id not in num_line and dato.id not in lotes_agregados:
                    num_line.append(dato.id)
            self.muestra_lote_line = False # Reinicia el valor del campo lote para que el usuario no conserve selecciones anteriores que ya no son válidas

            return {'domain': {'muestra_lote_line': [('id', 'in', num_line)]}}
