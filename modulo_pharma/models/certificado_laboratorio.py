import hashlib
from string import ascii_uppercase

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import locale
import qrcode
from io import BytesIO
import base64

class CertificadosLaboratorio(models.Model):
    _name = 'certificados.laboratorio'
    _rec_name= "certificado_analisis_nro"


    company_id = fields.Many2one('res.company', string='Compañia', required=True, default=lambda self: self.env.company)
    state = fields.Selection(string='Estado', selection=[('draft', 'Borrador'),('posted', 'Publicado'),('impreso', 'Impreso'),
                                                         ('enviado', 'Enviado a Recepción'),], default="draft",)
    order_id = fields.Many2one('sale.order', string='Orden de Venta')
    stock_move_line_id = fields.Many2one('stock.move.line', string='Línea de Movimiento de Stock')
    stock_picking_id = fields.Many2one('stock.picking', string='Recepción')
    stock_move_id = fields.Many2one('stock.move', string='Movimiento de Stock Relacionado')
    sale_line_id = fields.Many2one('sale.order.line', string="Línea del Pedido de venta")


    tipo_grupo = fields.Selection([
        ('toxicologico', 'Toxicológico'),
        ('farma', 'Farma'),
        ('alta_complejidad', 'Alta Complejidad'),
        ('agroquimico', 'Agroquímico'),
    ], string='Tipo de Presupuesto', related="grupo_id.tipo_grupo")


    ### CABECERA ###
    grupo_id = fields.Many2one('ventas.grupo', string='Grupo', required=True, domain="[('tipo_documento', '=', 'Certificado'),('fecha_hasta','=',False)]")
    codigo_muestra = fields.Many2one('mrp.production', string='Código de Muestra', domain="[('tipo_grupo','=',tipo_grupo)]")
    certificado_analisis_nro = fields.Char(string='Certificado de Análisis Nro.')
    city_id = fields.Many2one(string='Ciudad', related="company_id.city_id")
    version_formato = fields.Char(string='Versión Formato', compute='_compute_version_formato', store=True)

    ###### FARMA ######

    ### INFORMACIÓN DE LA MUESTRA ###
    muestra_lote = fields.Many2one('product.product', string="Muestra - Lote", related="stock_move_id.product_id")
    muestra_lote_code = fields.Char(string="Producto", related="muestra_lote.default_code")
    nombre_comercial = fields.Char(string="Nombre comercial", related="muestra_lote.name")
    principios_activos = fields.Many2many('product.template', string="Principios Activos")
    forma_farma = fields.Char(string="Forma Farmacéutica", related='stock_picking_id.forma_farmaceutica')
    nro_lote = fields.Char(string='Número de Lote', related='stock_move_line_id.nro_lote', readonly=True)
    cantidad = fields.Float(string='Cantidad', related='stock_move_line_id.qty_done', readonly=True)
    acta_muestreo = fields.Char(string="Acta de Muestreo")
    descripcion_envase = fields.Char(string="Descripción del Envase", related="stock_picking_id.descipcion_envase")
    fecha_vencimiento = fields.Date(string='Fecha de Vencimiento', related='stock_move_line_id.fecha_vencimiento_lote',
                                    readonly=True)
    condicion_almacenamiento = fields.Char(string="Condición de Almacenamiento", related="stock_picking_id.condicion_almacenamiento")


    ### CLIENTE/CONTACTO ###
    cliente_id = fields.Many2one('res.partner', string='Cliente', related="order_id.partner_id")
    contacto = fields.Char(string="Contacto", related="cliente_id.name")
    remitente_id = fields.Many2one('res.partner', string='Remitido por', related="order_id.partner_id")
    solicitante_id = fields.Many2one('res.partner', string='Solicitante', related="order_id.partner_id")
    analizado_por = fields.Many2one('res.users', string='Analizado por')
    motivo_id = fields.Many2one('stock.move', string='Motivo de análisis')
    fabricante = fields.Char(related='stock_picking_id.fabricante', string='Fabricante')
    origen = fields.Char(related='stock_picking_id.origen', string='Origen')


    ### OTROS DATOS ###
    metodologia_analisis_id = fields.Many2one('ventas.metodologia_analisis', string='Metodología del Análisis')
    ph = fields.Char(string='pH')
    densidad = fields.Char(string='Densidad')

    ### FECHAS ###
    fecha_recepcion = fields.Datetime(string='Fecha de Recepción', related='stock_picking_id.date_done',
                                      readonly=True)
    fecha_analisis = fields.Datetime(string='Fecha de Análisis', related="codigo_muestra.date_finished")
    fecha_finalizacion = fields.Date(string='Fecha de Finalización', default=fields.Date.today)


    equipos = fields.Many2many('maintenance.equipment', string="Equipos utilizados")
    detalle_pharma_line = fields.One2many('resultados.pharma.detalle', 'certificado_laboratorio_id', string='Información del Estándar')

    metodos_ids = fields.Many2many('product.template', 'metodos_ids', string='Métodos')
    metodos_default_code = fields.Char(string="Productos")

    resultados_obtenidos_ids = fields.One2many('certificados.resultados_obtenidos','certificados_id',
                                               string='Resultados Obtenidos')

    conclusion = fields.Text(
        string='Conclusión',
        help='Ingrese la conclusión del análisis')

    codigo_muestra_lote = fields.Char(store=True)

    resultado_farma_ids = fields.Many2many('resultado.farma', string="Resultados")


    ###### FIN FARMA ######

    ###### ALTA COMPLEJIDAD ######
    ensayo_en = fields.Many2one('product.product', string="Ensayo en", related="stock_move_id.product_id")

    ### DATOS PROVISTOS POR EL CLIENTE ###
    matriz_id = fields.Many2one('ventas.matriz', string='Matriz', related="sale_line_id.matriz_id")
    #nro_lote
    procedencia = fields.Char(related='stock_picking_id.procedencia', string='Procedencia')

    ### INFORMACIÓN DE MUESTRA ###
    #codigo_muestra
    nro_solicitud = fields.Char(string='Nro. de Solicitud')
    peso = fields.Float(string="Peso", related="stock_move_line_id.qty_done")
    product_uom_id = fields.Many2one('uom.uom',string="Peso", related="stock_move_line_id.product_uom_id")

    ### Cliente_id y contacto ###

    #### Fechas ###

    ### ANALISIS SOLICITADOS / REFERENCIA ###
    analisis_referencia_ids = fields.One2many('certificados.analisis_referencias', 'certificado_id', string="Análisis/Referencias")

    resultado_alta_ids = fields.Many2many("mrp.workorder", string="Resultados")

    ###### FIN ALTA COMPLEJIDAD ######

    ###### AGROQUIMICO ######
    #product_id = fields.Many2one('product.product', string="Producto")
    #principios_activos_ids
    #nro_lote
    #fecha_vencimiento

    tipo_solicitud = fields.Char(string='Tipo de Solicitud')
    tipo_envase = fields.Char(string='Tipo Envase')
    concentracion = fields.Char(string='Concentración')
    composicion = fields.Char(string='Composición')
    tipo_formulacion = fields.Char(string='Tipo de Formulación')
    uso = fields.Char(string='Uso')
    importador = fields.Char(string='Importador/Distribuidor/Fabricante')
    fecha_elaboracion = fields.Date(string='Fecha Elaboración')
    lugar_muestreo = fields.Char(string='Lugar de Muestreo')

    #cliente
    #contacto

    #metodos_ids
    #equipos

    #### Fechas ####

    estandar_ids = fields.One2many('certificados.estandar_agro', 'certificado_id', string="Información del Estándar")

    propiedades_fisicas_ids = fields.One2many('certificados.propiedades_fisicas', 'certificado_id', string="Propiedades Físicas")

    resultado_agro_ids = fields.Many2many('resultado.agro', string="Resultados")


    ##### FIN AGROQUIMICO #####

    ##### TOXICOLOGICO #####
    #codigo_muestra
    #muestra_lote // tipo_muestra
    paciente = fields.Char(string='Paciente')
    sexo = fields.Boolean(string='Sexo (check=M)')
    edad = fields.Char(string='Edad')
    nro_orden = fields.Char(string='Nro. Orden')
    medico = fields.Char(string='Médico')
    codigo_remision = fields.Char(string='Código Remisión')
    almacenamiento = fields.Char(string='Almacenamiento')
    #remitido_por // remitente_id
    #solicitado_por // solicitante_id
    #fecha_recepcion
    #tipo_solicitud
    #metodos_ids

    #fecha_recepcion
    #fecha_analisis
    resultado_toxi_ids = fields.Many2many('resultado.toxi', string="Resultados Toxicologico")
    ##### FIN TOXICOLOGICO #####

    qr_code = fields.Binary(string="QR Code", compute="generate_qr_code")

    def generate_qr_code(self):
        for i in self:
            base_url = self.env['ir.config_parameter'].sudo(
            ).get_param('web.base.url')

            route = "/certificado_check?certificado_id="+str(i.id)+"&token="+i.genera_token(str(i.id))
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data("%s%s" % (base_url, route))
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            i.qr_code = qr_image

    def genera_token(self,id_certificado):
        palabra=id_certificado+"amakakeruriunohirameki"
        return hashlib.sha256(bytes(palabra,'utf-8')).hexdigest()

    def _generate_certificate_pdf(self):
        for record in self:
            if record.tipo_grupo == 'farma':
                report = self.env.ref('modulo_pharma.reporte_certificado_laboratorio_action')
            elif record.tipo_grupo == 'alta_complejidad':
                report = self.env.ref('modulo_pharma.reporte_certificado_alta_complejidad_action')
            elif record.tipo_grupo == 'agroquimico':
                report = self.env.ref('modulo_pharma.reporte_certificado_agroquimico_action')
            elif record.tipo_grupo == 'toxicologico':
                report = self.env.ref('modulo_pharma.reporte_certificado_toxicologico_action')
            #pdf_content, _ = report._render_qweb_pdf(record.id)
            return self.env['ir.actions.report'].sudo().with_context(force_report_rendering=True)._render_qweb_pdf(report, res_ids=record.id)[0]

    def button_publicar(self):
        for record in self:
            codigo_muestra = record.codigo_muestra.codigo_muestra
            if codigo_muestra:
                ultima_parte = codigo_muestra.split('-')[-1]
                #record.numero_certificado = ultima_parte
                record.codigo_muestra_lote = codigo_muestra

        data = {
            'state': 'posted',
        }
        self.write(data)

    def _get_next_version_code(self, codigo_actual):
        """
        Genera el siguiente código de versión basado en el formato del código actual.
        Ejemplo: 00031 -> 00031-A -> 00031-B
        """
        if "-" not in codigo_actual:
            # Primer duplicado agrega el sufijo '-A'
            return f"{codigo_actual}-A"

        # Separar la parte base del sufijo
        base, sufijo = codigo_actual.rsplit("-", 1)
        if len(sufijo) != 1 or sufijo not in ascii_uppercase:
            raise UserError(_("El formato del código '%s' es inválido." % codigo_actual))

        # Incrementar al siguiente sufijo alfabético
        next_sufijo = chr(ord(sufijo) + 1)
        if next_sufijo > "Z":
            raise UserError(_("Se ha alcanzado el límite de versiones para el certificado '%s'." % codigo_actual))

        return f"{base}-{next_sufijo}"

    #@api.model
    def copy(self, default=None):
        """
        Personalizamos la acción de duplicar para crear una nueva versión del certificado.
        """
        self.ensure_one()  # Aseguramos que la acción se realiza sobre un único registro

        # Validar que el estado permita duplicar
        if self.state not in ['impreso', 'enviado']:
            raise UserError(_("Solo se pueden duplicar certificados en los estados 'Impreso' o 'Enviado'."))

        # Generar el siguiente código de versión
        default = dict(default or {})
        default['certificado_analisis_nro'] = self._get_next_version_code(self.certificado_analisis_nro)

        # Cambiar el estado del duplicado a borrador
        default['state'] = 'draft'

        new_certificado = super(CertificadosLaboratorio, self).copy(default)
        for ro in self.resultados_obtenidos_ids:
            ro.copy(default={'certificados_id': new_certificado.id})

        for dp in self.detalle_pharma_line:
            dp.copy(default={'certificado_laboratorio_id': new_certificado.id})

        for ar in self.analisis_referencia_ids:
            ar.copy(default={'certificado_id': new_certificado.id})

        for es in self.estandar_ids:
            es.copy(default={'certificado_id': new_certificado.id})

        for pf in self.propiedades_fisicas_ids:
            pf.copy(default={'certificado_id': new_certificado.id})
            
        #new_certificado.resultado_alta_ids = [(6, 0, self.resultado_alta_ids.ids)]

        # Crear el duplicado
        return new_certificado

    #@api.model
    def action_send_email(self):
        for record in self:
            # Verificar que el estado es 'Publicado'
            if record.state != 'posted':
                raise UserError(_('El certificado no está en estado "Publicado"'))

            if record.tipo_grupo == 'farma':
                template = self.env.ref('modulo_pharma.email_template_certificado_pharma')
            elif record.tipo_grupo == 'alta_complejidad':
                template = self.env.ref('modulo_pharma.email_template_certificado_alta_complejidad')
            elif record.tipo_grupo == 'agroquimico':
                template = self.env.ref('modulo_pharma.email_template_certificado_agroquimico')
            elif record.tipo_grupo == 'toxicologico':
                template = self.env.ref('modulo_pharma.email_template_certificado_toxicologico')

            if template:
                 template.with_context(partner_email=record.cliente_id.email).send_mail(record.id, force_send=True)
            record.state = 'enviado'  # Actualizar el estado a 'Enviado a Recepción'

        return True

    #@api.model
    def action_send_to_reception(self):
        # Cambiar el estado a "Enviado a Recepción"
        for record in self:
            record.state = 'enviado'
        return True

    #@api.model
    def action_print_certificate(self):
        # Lógica para generar el reporte
        for rec in self:
            if rec.state == 'impreso':
                raise UserError(_("El certificado ya ha sido impreso."))
            # Generar el reporte
            if rec.tipo_grupo == 'farma':
                report_action = self.env.ref('modulo_pharma.reporte_certificado_laboratorio_action').report_action(rec)
            elif rec.tipo_grupo == 'alta_complejidad':
                report_action = self.env.ref('modulo_pharma.reporte_certificado_alta_complejidad_action').report_action(rec)
            elif rec.tipo_grupo == 'agroquimico':
                report_action = self.env.ref('modulo_pharma.reporte_certificado_agroquimico_action').report_action(rec)
            elif rec.tipo_grupo == 'toxicologico':
                report_action = self.env.ref('modulo_pharma.reporte_certificado_toxicologico_action').report_action(rec)
            # Cambiar estado a 'impreso'
            rec.state = 'impreso'
        return report_action

    def get_current_date(self):
        """
        Obtenemos la fecha actual en formato dd de MMMM del YYYY
        """
        # Establecemos el locale
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

        # Generamos la fecha actual y retornamos
        return fields.Date.today().strftime('%d de %B del %Y')

    @api.onchange('codigo_muestra')
    def _onchange_codigo_muestra(self):
        for rec in self:
            rec.resultados_obtenidos_ids = [(5, 0, 0)]  # Limpia los resultados actuales
            rec.detalle_pharma_line = [(5, 0, 0)]  # Limpia los resultados actuales
            rec.analisis_referencia_ids = [(5, 0, 0)]  # Limpia los resultados actuales
            rec.resultado_alta_ids = [(5, 0, 0)]
            rec.resultado_agro_ids = [(5, 0, 0)]
            rec.resultado_farma_ids = [(5, 0, 0)]
            rec.estandar_ids = [(5, 0, 0)]
            rec.propiedades_fisicas_ids = [(5, 0, 0)]
            if rec.codigo_muestra:
                if rec.codigo_muestra.codigo_muestra:
                    rec.certificado_analisis_nro = rec.codigo_muestra.codigo_muestra[-5:]
                else:
                    rec.certificado_analisis_nro = rec.codigo_muestra.name[-5:]
                if rec.tipo_grupo == "alta_complejidad":
                    op_alta = self.env['mrp.production'].search(
                        [('codigo_muestra', '=', rec.codigo_muestra.codigo_muestra)])
                    resultado_alta = op_alta.mapped('workorder_ids').filtered(lambda x:x.resultado_alta_ids)
                    rec.resultado_alta_ids = [(6, 0, resultado_alta.ids)]
                elif rec.tipo_grupo == "farma":
                    op_farma = self.env['mrp.production'].search(
                        [('codigo_muestra', '=', rec.codigo_muestra.codigo_muestra)])
                    resultado_farma = op_farma.mapped('workorder_ids').filtered(lambda x:x.resultado_farma_ids)
                    rec.resultado_farma_ids = [(6, 0, resultado_farma.resultado_famra_ids.ids)]
                elif rec.tipo_grupo == "agroquimico":
                    op_agro = self.env['mrp.production'].search([('codigo_muestra','=', rec.codigo_muestra.codigo_muestra)])
                    resultado_agro = op_agro.mapped('workorder_ids.resultado_agro_ids')
                    rec.resultado_agro_ids = [(6, 0, resultado_agro.ids)]
                resultado_toxi = rec.mapped('codigo_muestra.workorder_ids.resultado_toxi_ids')
                if resultado_toxi:
                    rec.resultado_toxi_ids = [(6, 0, resultado_toxi.ids)]
                rec.nro_solicitud = rec.certificado_analisis_nro
                order = self.env['sale.order'].search([('company_id','=', rec.company_id.id),
                                                        ('grupo_id.tipo_grupo','=',rec.tipo_grupo),
                                                        ('state','=','sale'),
                                                        ('name','=', rec.codigo_muestra.origin)], limit=1)
                if order:
                    rec.order_id = order
                    rec.metodologia_analisis_id = order.metodologia_analisis
                    rec.sale_line_id = order.mapped('order_line').filtered(lambda x: x.product_id == rec.codigo_muestra.product_id)
                    rec.stock_picking_id = order.stock_picking_id
                    if rec.tipo_grupo == 'agroquimico':
                        rec.tipo_solicitud = order.stock_picking_id.tipo_solicitud
                        rec.tipo_envase = order.stock_picking_id.tipo_envase
                        rec.concentracion = order.stock_picking_id.concentracion
                        rec.composicion = order.stock_picking_id.composicion
                        rec.tipo_formulacion =order.stock_picking_id.tipo_formulacion
                        rec.uso = order.stock_picking_id.uso
                        rec.importador = order.stock_picking_id.importador
                        rec.fecha_elaboracion = order.stock_picking_id.fecha_elaboracion
                        rec.lugar_muestreo = order.stock_picking_id.lugar_muestreo
                        pf_vals = {
                            'aspecto': rec.stock_picking_id.aspecto,
                            'color': rec.stock_picking_id.color,
                            'densidad': rec.stock_picking_id.densidad,
                        }
                        rec.write({'propiedades_fisicas_ids':[(0,0,pf_vals)]})
                    elif rec.tipo_grupo == 'toxicologico':
                        rec.paciente = order.stock_picking_id.paciente
                        rec.sexo = order.stock_picking_id.sexo
                        rec.edad = order.stock_picking_id.edad
                        rec.nro_orden = order.stock_picking_id.nro_orden
                        rec.medico = order.stock_picking_id.medico
                        rec.codigo_remision = order.stock_picking_id.codigo_remision
                        rec.almacenamiento = order.stock_picking_id.almacenamiento
                    stock_move = order.mapped('stock_picking_id.move_ids_without_package')
                    rec.stock_move_id = stock_move.filtered(lambda x:x.product_id == rec.codigo_muestra.muestra_id)
                    stock_move_line = self.env['stock.move.line'].search([('move_id', '=', rec.stock_move_id.id),
                                                                          ('product_id','=', rec.codigo_muestra.muestra_id.id)],
                                                          limit=1)
                    rec.stock_move_line_id = stock_move_line
                    #rec.product_id = order.mapped('muestras_ids.metodos_ids')[0] if len(order.mapped('muestras_ids.metodos_ids')) > 0 else False
                    principios_activos = order.mapped('muestras_ids.principios_activos_ids')
                    rec.principios_activos = principios_activos
                    for p in principios_activos:
                        if rec.tipo_grupo == "agroquimico":
                            values = {
                                'principio_activo_id': p.id
                            }
                            rec.estandar_ids = [(0, 0, values)]
                        values = {
                            'principios_activos': p.id
                        }
                        rec.detalle_pharma_line = [(0, 0,  values)]

                    rec.metodos_ids = order.mapped('muestras_ids').filtered(lambda x:x.muestra_id == rec.codigo_muestra.muestra_id).mapped('metodos_ids')
                    #rec.metodos_default_code = ", ".join(rec.mapped('metodos_ids.default_code'))
                    for m in rec.metodos_ids:
                        if rec.tipo_grupo == 'alta_complejidad':
                            values = {
                                'metodo_id': m.id
                            }
                            rec.analisis_referencia_ids = [(0, 0, values)]
                        elif rec.tipo_grupo == 'farma':
                            vals_resultados = {
                                'ensayos': m.id,
                                'principios_activos': m.principios_activos_ids.ids,
                                # 'resultados':quality_check.additional_note + quality_check.measure + quality_check.x_studio_resultado,
                                # 'especificacion': quality_check.x_comments,
                                # 'limite_deteccion': quality_check.x_studio_lmite_de_deteccin_1
                            }
                            rec.resultados_obtenidos_ids = [(0, 0, vals_resultados)]
                    quality_check = self.env['stock.picking'].search([('id', '=', order.stock_picking_id.id)],
                                                          limit=1)
                else:
                    raise UserError(_("No existe ningún presupuesto asociado al código de muestra"))
            else:
                rec.order_id = False
                rec.metodologia_analisis_id = False
                rec.sale_line_id = False
                rec.stock_picking_id = False
                rec.stock_move_id = False
                rec.stock_move_line_id = False
                rec.principios_activos = False

    @api.depends('grupo_id')
    @api.onchange('grupo_id')
    def _compute_version_formato(self):
        for rec in self:
            if rec.grupo_id:
                rec.version_formato = rec.grupo_id.nombre_iso