from odoo import models, fields, api

import base64
import io

class InformeControl(models.AbstractModel):
    _name = "report.ventas_custom.informe_de_control"
    _description = "Reporte de control"

    @api.model
    def _get_report_values(self, docids, data=None):

        grupo_analisis_id = data.get("grupo_analisis", False)
        metodos_ids = data.get("metodos_ids", True)
        sale_order_ids = data.get("ordenes_ids", False)

        tipo_metodo = data.get("tipo_metodo", False)

        metodos_ids = True if tipo_metodo == "todos" or len(tipo_metodo) == 0 else metodos_ids

        if not all([grupo_analisis_id, metodos_ids, sale_order_ids]):
            return {
                "doc_ids": docids,
                "docs": {},
                "data": data,
            }

        grupo_analisis_id = self.env["ventas.grupo"].browse(grupo_analisis_id)
        sale_order_ids = self.env["sale.order"].search([("id", "in", sale_order_ids)])

        if tipo_metodo == "todos":
            metodos_ids = sale_order_ids.order_line.product_id.product_tmpl_id.mapped("id")
            metodos_ids = list(set(metodos_ids))
        
        metodos_ids = self.env["product.template"].search([("id", "in", metodos_ids)])
        
        cabecera = {}
        if grupo_analisis_id:
            titulo = "CONTROL DE SOLICITUD, INGRESO DE MUESTRA Y ENTREGA DE RESULTADOS DE "
            if grupo_analisis_id.tipo_grupo == "farma":
                titulo += "MEDICAMENTOS"
            elif grupo_analisis_id.tipo_grupo == "alta_complejidad":
                titulo += "ALTA COMPLEJIDAD"
            elif grupo_analisis_id.tipo_grupo == "agroquimico":
                titulo += "CONTROL DE CALIDAD"
            elif grupo_analisis_id.tipo_grupo == "toxicologico":
                titulo += "TOXICOLOGÍA"

            nombre_iso = grupo_analisis_id.nombre_iso

            codigo = nombre_iso[:len(nombre_iso)-2].rstrip("-")
            version = nombre_iso[-2:]
            vigencia = grupo_analisis_id.fecha_desde.strftime('%d/%m/%Y') if grupo_analisis_id.fecha_desde else ""

            cabecera = {
                "company_id": sale_order_ids[0].company_id,
                "titulo": titulo,
                "codigo":codigo,
                "version":version,
                "vigencia":vigencia,
            }

        detalle = []

        for sale_order_id in sale_order_ids:

            stock_picking_id = self.env["stock.picking"].search([
                ("id", "=", sale_order_id.stock_picking_id.id),
                ("state", "in", ["assigned", "done"]),
                ("picking_type_id.code", "=", "incoming"),
            ])

            for move_line_id in stock_picking_id.mapped("move_line_ids"):
                muestras = sale_order_id.muestras_ids.filtered(lambda i: i.muestra_id and i.muestra_id.id == move_line_id.product_id.id if move_line_id.product_id else False)
                
                if not muestras or not muestras.metodos_ids:
                    continue
                    
                for metodo in muestras.metodos_ids:
                    if not metodo or not metodo.id or metodo.id not in metodos_ids.mapped("id"):
                        continue
                        
                    vals = {}
                    
                    certificados = self.env['certificados.laboratorio'].search([
                        ("state", "not in", ["draft"]),
                        ("stock_move_line_id", "=", move_line_id.id),
                        ("codigo_muestra.product_id.product_tmpl_id", "=", metodo.id)
                    ])
                    
                    transferencias_lab = self.env["stock.picking"].search([
                        ("state", "=", "done"),
                        ("location_dest_id.id", "=", 27),
                        ("location_dest_id.usage", "=", "internal"),
                        ("move_line_ids.product_id", "=", move_line_id.product_id.id if move_line_id.product_id else False),
                        ("move_line_ids.lot_id", "=", move_line_id.lot_id.id if move_line_id.lot_id else False),
                    ], order="date_done DESC")
                    
                    ordenes_produccion = self.env["mrp.production"].search([
                        ("product_id.product_tmpl_id", "=", metodo.id),
                        ("muestra_id", "=", move_line_id.product_id.id if move_line_id.product_id else False),
                        ("muestra_lot_id", "=", move_line_id.lot_id.id if move_line_id.lot_id else False),
                        ("codigo_muestra", "=", move_line_id.codigo_muestra if move_line_id.codigo_muestra else False),
                    ], order="date_planned_start DESC")
                    
                    
                    codigo_muestra = move_line_id.codigo_muestra or ""
                    vals["nro_solicitud"] = codigo_muestra[-5:] if codigo_muestra and len(codigo_muestra) >= 5 else "Sin código de muestra"
                    vals["codigo_muestra"] = codigo_muestra or "Sin código de muestra"
                    vals["nro_informe"] = codigo_muestra[-5:] if codigo_muestra and len(codigo_muestra) >= 5 else "Sin número de informe"
                    
                    vals["cliente"] = sale_order_id.partner_id.name if sale_order_id.partner_id else "Cliente no especificado"
                    
                    vals["analisis_solicitado"] = metodo.name if metodo and metodo.name else "Sin método"
                    
                    fecha_done = move_line_id.picking_id.date_done if move_line_id.picking_id else False
                    vals["fecha_ingreso"] = fecha_done.strftime('%d/%m/%Y') if fecha_done else "Sin fecha de ingreso"
                    
                    if transferencias_lab:
                        transferencia = transferencias_lab[0]
                        vals["fecha_entraga_lab"] = transferencia.date_done.strftime('%d/%m/%Y') if transferencia.date_done else "Fecha no disponible"
                        vals["recibido_por"] = transferencia.user_id.name if transferencia.user_id else "Usuario no especificado"
                        
                        if len(transferencias_lab) > 1:
                            transferencias_info = []
                            for i, trans in enumerate(transferencias_lab, 1):
                                fecha = trans.date_done.strftime('%d/%m/%Y') if trans.date_done else "Fecha no disponible"
                                usuario = trans.user_id.name if trans.user_id else "Usuario no especificado"
                                transferencias_info.append(f"Transfer. {i}: {fecha} - {usuario}")
                            vals["transferencias_adicionales"] = "; ".join(transferencias_info)
                    else:
                        vals["fecha_entraga_lab"] = "Sin transferencia"
                        vals["recibido_por"] = "Sin transferencia"
                    
                    if certificados:
                        certificado = certificados[0]
                        vals["analizado_por"] = certificado.analizado_por.name if certificado.analizado_por else "Analista no especificado"
                        
                        if len(certificados) > 1:
                            certificados_info = []
                            for i, cert in enumerate(certificados, 1):
                                analista = cert.analizado_por.name if cert.analizado_por else "Analista no especificado"
                                estado = cert.state if cert.state else "Estado desconocido"
                                certificados_info.append(f"Cert. {i}: {analista} - {estado}")
                            vals["certificados_adicionales"] = "; ".join(certificados_info)
                    else:
                        vals["analizado_por"] = "Certificado pendiente"
                    
                    if ordenes_produccion:
                        orden = ordenes_produccion[0]
                        vals["fecha_inicio"] = orden.date_planned_start.strftime('%d/%m/%Y') if orden.date_planned_start else "Fecha no disponible"
                        vals["fecha_fin"] = orden.date_finished.strftime('%d/%m/%Y') if orden.date_finished else "Fecha no disponible"
                        
                        if len(ordenes_produccion) > 1:
                            ordenes_info = []
                            for i, ord in enumerate(ordenes_produccion, 1):
                                inicio = ord.date_planned_start.strftime('%d/%m/%Y') if ord.date_planned_start else "Inicio N/D"
                                fin = ord.date_finished.strftime('%d/%m/%Y') if ord.date_finished else "Fin N/D"
                                ordenes_info.append(f"Orden {i}: {inicio} - {fin}")
                            vals["ordenes_adicionales"] = "; ".join(ordenes_info)
                    else:
                        vals["fecha_inicio"] = "Sin orden de producción"
                        vals["fecha_fin"] = "Sin orden de producción"
                    
                    vals["fecha_entrega_recepcion"] = "N/A"
                    vals["fecha_entrega_cliente"] = "N/A"
                    vals["entregado_a"] = "N/A"
                    vals["observaciones"] = "N/A"
                    
                    detalle.append(vals)

        docs = {
            "cabecera": cabecera,
            "detalle": detalle
        }

        return {
            "doc_ids": docids,
            "docs": docs,
            "data": data,
        }
    
class InformeControlXLSX(models.TransientModel):
    _name = 'report.ventas_custom.informe_de_control_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, sale_order_ids=None):
        global sheet
        global bold
        global num_format
        global position_x
        global position_y
        sheet = workbook.add_worksheet('Resumen por Concepto')
    
        position_x = 0
        position_y = 0

        styles = {
            'bold': {
                'bold': True
            },
            'orange': {
                'bg_color': '#FFA500'
            },
            'light_grey': {
                'bg_color': '#F5F4F0'
            },
            'grey': {
                'bg_color': '#CEC5BE'
            },
            'white': {
                'bg_color': '#FFFFFF'
            },
            'right': {
                'align': 'right'
            },
            'center': {
                'align': 'center'
            },
            'border': {
                'border': 1
            },
            'numerico': {
                'num_format': '#,##0',
                'align': 'right'
            },
            'numerico_total': {
                'num_format': '#,##0',
                'align': 'right',
                'bold': True
            },
            'center': {
                'align': 'center'
            },
            'vcenter': {
                'valign': 'vcenter'
            },
            'text_wrap': {
                'text_wrap': True
            },
        }

        def combine_styles(workbook, style_names):
            combined_props = {}
            if isinstance(style_names, str):
                style_names = [style_names]
                
            for style_name in style_names:
                if style_name in styles:
                    combined_props.update(styles[style_name])
            
            return workbook.add_format(combined_props)

        def down():
            global position_y
            position_y += 1

        def left():
            global position_x
            position_x -= 1

        def addSalto():
            global position_x
            global position_y
            position_x = 0
            position_y += 1

        def addRight():
            global position_x
            position_x += 1

        def simpleWrite(to_write, format=None):
            global sheet

            if format and isinstance(format, list):
                format = combine_styles(workbook, format)

            if isinstance(to_write, int) or isinstance(to_write, float):
                to_write = int(to_write)
            sheet.write(position_y, position_x, to_write or ('' if type(to_write) != int else 0), format)

        def breakAndWrite(to_write, format=None):
            global sheet

            if format:
                format = combine_styles(workbook, format)

            addSalto()
            simpleWrite(to_write, format)

        def rightAndWrite(to_write, format=None):
            global sheet

            if format:
                format = combine_styles(workbook, format)

            addRight()
            simpleWrite(to_write, format)

        def simpleMergeAndWrite(to_write, num_cells, format=None):
            global sheet
            global position_x
            global position_y

            if format:
                format = combine_styles(workbook, format)

            sheet.merge_range(position_y, position_x, position_y, position_x + num_cells - 1, 
                            to_write or ('' if type(to_write) != int else 0), format)
            position_x += (num_cells - 1)

        def mergeAndWrite(to_write, num_cells, format=None):
            global sheet
            global position_x
            global position_y

            if format:
                format = combine_styles(workbook, format)

            addRight()
            sheet.merge_range(position_y, position_x, position_y, position_x + num_cells - 1, 
                            to_write or ('' if type(to_write) != int else 0), format)
            position_x += (num_cells - 1)

        grupo_analisis_id = data.get("grupo_analisis", False)
        metodos_ids = data.get("metodos_ids", True)
        sale_order_ids = data.get("ordenes_ids", False)

        tipo_metodo = data.get("tipo_metodo", False)

        metodos_ids = True if tipo_metodo == "todos" or len(tipo_metodo) == 0 else metodos_ids

        if not all([grupo_analisis_id, metodos_ids, sale_order_ids]):
            return

        grupo_analisis_id = self.env["ventas.grupo"].browse(grupo_analisis_id)
        sale_order_ids = self.env["sale.order"].search([("id", "in", sale_order_ids)])

        if tipo_metodo == "todos":
            metodos_ids = sale_order_ids.order_line.product_id.product_tmpl_id.mapped("id")
            metodos_ids = list(set(metodos_ids))
        
        metodos_ids = self.env["product.template"].search([("id", "in", metodos_ids)])
        
        if grupo_analisis_id:
            titulo = "CONTROL DE SOLICITUD, INGRESO DE MUESTRA Y ENTREGA DE RESULTADOS DE "
            if grupo_analisis_id.tipo_grupo == "farma":
                titulo += "MEDICAMENTOS"
            elif grupo_analisis_id.tipo_grupo == "alta_complejidad":
                titulo += "ALTA COMPLEJIDAD"
            elif grupo_analisis_id.tipo_grupo == "agroquimico":
                titulo += "CONTROL DE CALIDAD"
            elif grupo_analisis_id.tipo_grupo == "toxicologico":
                titulo += "TOXICOLOGÍA"

            sheet.merge_range(position_y, position_x, position_y + 2, position_x + 3, '', None)
            
            if sale_order_ids[0].company_id:
                image_data = base64.b64decode(sale_order_ids[0].company_id.logo)
    
                image_stream = io.BytesIO(image_data)
                
                sheet.insert_image(position_y, position_x, 'company_logo.png', {
                    'image_data': image_stream,
                    'x_scale': 0.2,  
                    'y_scale': 0.2,  
                    'x_offset': 5,   
                    'y_offset': 5    
                })

            temp_x = position_x + 4
            sheet.merge_range(position_y, temp_x, position_y + 2, temp_x + 8, titulo, 
                            combine_styles(workbook, ["bold", "light_grey", "border", "text_wrap", "center", "vcenter"]))

            position_y = 0
            position_x = 13

            nombre_iso = grupo_analisis_id.nombre_iso

            codigo = nombre_iso[:len(nombre_iso)-2].rstrip("-")
            version = nombre_iso[-2:]
            vigencia = grupo_analisis_id.fecha_desde.strftime('%d/%m/%Y') if grupo_analisis_id.fecha_desde else ""

            simpleWrite(f"Código:", ["bold", "light_grey", "border"])
            rightAndWrite(codigo, ["border"])
            down()
            left()
            simpleWrite(f"Versión:", ["bold", "light_grey", "border"])
            rightAndWrite(version, ["border"])
            down()
            left()
            simpleWrite(f"Vigencia:", ["bold", "light_grey", "border"])
            rightAndWrite(vigencia, ["border"])

        breakAndWrite("N° DE SOLICITUD", ["bold", "light_grey", "border"])
        rightAndWrite("EMPRESA / CLIENTE", ["bold", "light_grey", "border"])
        rightAndWrite("ANÁLISIS SOLICITADO", ["bold", "light_grey", "border"])
        rightAndWrite("FECHA DE INGRESO", ["bold", "light_grey", "border"])
        rightAndWrite("CÓDIGO DE MUESTRAS", ["bold", "light_grey", "border"])
        rightAndWrite("FECHA ENTREGA A LAB", ["bold", "light_grey", "border"])
        rightAndWrite("RECIBIDO EN LAB. POR", ["bold", "light_grey", "border"])
        rightAndWrite("ANALIZADO POR", ["bold", "light_grey", "border"])
        rightAndWrite("FECHA DE INICIO", ["bold", "light_grey", "border"])
        rightAndWrite("FECHA DE FIN", ["bold", "light_grey", "border"])
        rightAndWrite("N° DE INFORME", ["bold", "light_grey", "border"])
        rightAndWrite("FECHA DE ENTREGA RECEPCIÓN", ["bold", "light_grey", "border"])
        rightAndWrite("FECHA DE ENTREGA AL CLIENTE", ["bold", "light_grey", "border"])
        rightAndWrite("ENTREGADO A", ["bold", "light_grey", "border"])
        rightAndWrite("OBS", ["bold", "light_grey", "border"])

        for sale_order_id in sale_order_ids:

            stock_picking_id = self.env["stock.picking"].search([
                ("id", "=", sale_order_id.stock_picking_id.id),
                ("state", "in", ["assigned", "done"]),
                ("picking_type_id.code", "=", "incoming"),
            ])

            for move_line_id in stock_picking_id.mapped("move_line_ids"):
                muestra = sale_order_id.muestras_ids.filtered(lambda i: i.muestra_id and i.muestra_id.id == move_line_id.product_id.id if move_line_id.product_id else False)
                if not muestra or not muestra.metodos_ids:
                    continue
                    
                for metodo in muestra.metodos_ids:
                    if not metodo or not metodo.id or metodo.id not in metodos_ids.mapped("id"):
                        continue
                        
                    certificados = self.env['certificados.laboratorio'].search([
                        ("state", "not in", ["draft"]),
                        ("stock_move_line_id", "=", move_line_id.id),
                        ("codigo_muestra.product_id.product_tmpl_id", "=", metodo.id)
                    ])
                    
                    certificado = certificados[0] if certificados else False

                    transferencias_lab = self.env["stock.picking"].search([
                        ("state", "=", "done"),
                        ("location_dest_id.id", "=", 27),
                        ("location_dest_id.usage", "=", "internal"),
                        ("move_line_ids.product_id", "=", move_line_id.product_id.id if move_line_id.product_id else False),
                        ("move_line_ids.lot_id", "=", move_line_id.lot_id.id if move_line_id.lot_id else False),
                    ], order="date_done DESC")

                    transferencia_lab = transferencias_lab[0] if transferencias_lab else False

                    ordenes_produccion = self.env["mrp.production"].search([
                        ("product_id.product_tmpl_id", "=", metodo.id),
                        ("muestra_id", "=", move_line_id.product_id.id if move_line_id.product_id else False),
                        ("muestra_lot_id", "=", move_line_id.lot_id.id if move_line_id.lot_id else False),
                        ("codigo_muestra", "=", move_line_id.codigo_muestra if move_line_id.codigo_muestra else False),
                    ], order="date_planned_start DESC")

                    orden_produccion = ordenes_produccion[0] if ordenes_produccion else False
                    
                    codigo_muestra = move_line_id.codigo_muestra or ""
                    nro_solicitud = codigo_muestra[-5:] if codigo_muestra and len(codigo_muestra) >= 5 else "Sin código de muestra"
                    breakAndWrite(nro_solicitud, [])
                    
                    cliente = sale_order_id.partner_id.name if sale_order_id.partner_id else "Cliente no especificado"
                    rightAndWrite(cliente, [])
                    
                    analisis = metodo.name if metodo and metodo.name else "Sin método"
                    rightAndWrite(analisis, [])
                    
                    fecha_ingreso = move_line_id.picking_id.date_done.strftime('%d/%m/%Y') if move_line_id.picking_id and move_line_id.picking_id.date_done else "Sin fecha de ingreso"
                    rightAndWrite(fecha_ingreso, [])
                    
                    rightAndWrite(codigo_muestra or "Sin código de muestra", [])

                    fecha_entrega_lab = transferencia_lab.date_done.strftime('%d/%m/%Y') if transferencia_lab and transferencia_lab.date_done else "Sin transferencia"
                    rightAndWrite(fecha_entrega_lab, [])
                    
                    recibido_por = transferencia_lab.user_id.name if transferencia_lab and transferencia_lab.user_id else "Sin transferencia"
                    rightAndWrite(recibido_por, [])
                    
                    analizado_por = certificado.analizado_por.name if certificado and certificado.analizado_por else "Certificado pendiente"
                    rightAndWrite(analizado_por, [])
                    
                    fecha_inicio = orden_produccion.date_planned_start.strftime('%d/%m/%Y') if orden_produccion and orden_produccion.date_planned_start else "Sin orden de producción"
                    rightAndWrite(fecha_inicio, [])
                    
                    fecha_fin = orden_produccion.date_finished.strftime('%d/%m/%Y') if orden_produccion and orden_produccion.date_finished else "Sin orden de producción"
                    rightAndWrite(fecha_fin, [])
                    
                    nro_informe = codigo_muestra[-5:] if codigo_muestra and len(codigo_muestra) >= 5 else "Sin número de informe"
                    rightAndWrite(nro_informe, [])
                    
                    rightAndWrite("N/A", [])
                    rightAndWrite("N/A", [])
                    rightAndWrite("N/A", [])
                    rightAndWrite("N/A", [])