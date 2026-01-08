import json
import logging

import xmltodict
from odoo import _, exceptions, models

_logger = logging.getLogger(__name__)


class AccionesSIFEN(models.AbstractModel):
    _inherit = 'fe.de'
    _description = 'Acciones que se pueden realizar con SIFEN'

    def consultar_cdc_individual(self, de_logger, cdc=None):
        # Obtenemos el formato SOAP y enviamos la consulta
        soap_structure = self.factura_consulta_soap_xml(cdc)
        response = self.env['fe.wsdl'].consultaDe(soap_structure, de_logger)

        return response

    def enviar_lote_individual(self, lote, nro_lote=None):
        if nro_lote:
            lote = self.env['fe.lote'].search([('numero_lote', '=', nro_lote)])

        # Creamos un logger del lote
        lote_logger = self.env['fe.lote_loggers'].sudo().create({"lote": lote.id, "accion": "enviar lote"})

        # Guardamos el zip que se enviara a SIFEN
        if lote.remision_ids:
            zip_file = self.env['fe.de'].zip_file(lote.remision_ids)
        else:
            zip_file = self.env['fe.de'].zip_file(lote.invoice_ids)

        lote.sudo().write({"zipfile": zip_file, "zipfile_name": "lote.zip"})

        # Obtenemos el formato soap y enviamos el lote
        soap_structure = self.env['fe.de'].lote_recepcion_soap_xml(zip_file)
        response = self.env['fe.wsdl'].recepcionLoteDe(soap_structure, lote_logger)

        return response

    def consultar_lote_individual(self, lote, nro_lote=None):
        if nro_lote:
            lote = self.env['fe.lote'].search([('numero_lote', '=', nro_lote)])

        # Creamos un logger del lote
        lote_logger = self.env['fe.lote_loggers'].sudo().create({"lote": lote.id, "accion": "consultar lote"})

        # Obtenemos el formato soap y enviamos el lote
        soap_structure = self.env['fe.de'].lote_consulta_soap_xml(lote.numero_lote)
        response = self.env['fe.wsdl'].consultaResultadoLote(soap_structure, lote_logger)

        return response

    def consultar_ruc(self, ruc=None):
        soap_structure = self.ruc_consulta_soap_xml(ruc)
        response = self.env['fe.wsdl'].consultaRuc(soap_structure, None)

        return response

    def cancelar_factura(self, motivo):
        """
        Se puede cancelar cuando un DE es aprobado
        """

        # Creamos un logger del invoice
        if self.tipo_documento != 'nota_remision':
            de_logger = self.env['fe.de_loggers'].sudo().create({"invoice": self.id, "accion": "cancelar"})
        else:
            de_logger = self.env['fe.de_loggers'].sudo().create({"remision_id": self.id, "accion": "cancelar"})

        soap_structure = self.evento_cancelacion_soap_xml(self.cdc, motivo, de_logger)
        response = self.env['fe.wsdl'].recepcionEvento(soap_structure, de_logger)

        if not response:
            _logger.error('No se pudo consultar al servicio de Cancelar Factura de SIFEN')
            return False

        # Actualizamos el estado del invoice
        rResEnviConsLoteDe = response['env:Envelope']['env:Body']['ns2:rRetEnviEventoDe']
        dFecProc = rResEnviConsLoteDe.get('ns2:dFecProc', '')
        gResProcEVe = rResEnviConsLoteDe.get('ns2:gResProcEVe', '')
        dEstRes = gResProcEVe.get('ns2:dEstRes', '')
        id = gResProcEVe.get('ns2:id', '')

        gResProc = gResProcEVe.get('ns2:gResProc', '')
        dCodRes = gResProc.get('ns2:dCodRes', '')
        dMsgRes = gResProc.get('ns2:dMsgRes', '')

        # ======== Datos del Request ========
        if dCodRes == '0600':
            self.mensaje_anulacion = f'{dCodRes} - {dMsgRes}'
            self.mensaje_set = f"Cancelado: {motivo}"
            self.estado_anulacion = 'CANCELADO'
            self.estado_set = 'cancelado'
            return True
        else:
            self.mensaje_anulacion = f'{dCodRes} - {dMsgRes}'
            self.estado_anulacion = 'NO_CANCELADO'
            return False

    def inutilizar_factura(self, fact_inicio, fact_fin, motivo):
        """
        Anular por saltos de numeración
        Errores de llenado
        Rechazo del SIFEN
        Se inutiliza un solo nro de factura, los valores para el documento se tomarán del invoice
        """

        # Creamos un logger del invoice
        if self.tipo_documento != 'nota_remision':
            de_logger = self.env['fe.de_loggers'].sudo().create({"invoice": self.id, "accion": "inutilizar"})
        else:
            de_logger = self.env['fe.de_loggers'].sudo().create({"remision_id": self.id, "accion": "inutilizar"})

        soap_structure = self.evento_inutilizacion_soap_xml(fact_inicio, fact_fin, motivo)
        response = self.env['fe.wsdl'].recepcionEvento(soap_structure, de_logger)

        if not response:
            _logger.error('No se pudo consultar al servicio de Inutilizar Factura de SIFEN')
            return False

        # Actualizamos el estado del invoice
        rResEnviConsLoteDe = response['env:Envelope']['env:Body']['ns2:rRetEnviEventoDe']
        dFecProc = rResEnviConsLoteDe.get('ns2:dFecProc', '')
        gResProcEVe = rResEnviConsLoteDe.get('ns2:gResProcEVe', '')
        dEstRes = gResProcEVe.get('ns2:dEstRes', '')
        id = gResProcEVe.get('ns2:id', '')

        gResProc = gResProcEVe.get('ns2:gResProc', '')
        dCodRes = gResProc.get('ns2:dCodRes', '')
        dMsgRes = gResProc.get('ns2:dMsgRes', '')

        # ======== Datos del Request ========
        if dCodRes == '0600':
            self.mensaje_anulacion = f'{dCodRes} - {dMsgRes}'
            self.estado_anulacion = 'INUTILIZADO'
            self.estado_set = 'inutilizado'
            self.state = 'cancel'
            return True
        else:
            self.mensaje_anulacion = f'{dCodRes} - {dMsgRes}'
            self.estado_anulacion = 'NO_INUTILIZADO'

        return False

    def inutilizar_rango_facturas(self, data, fe_rango_object, fe_logger):
        """
        Anular por saltos de numeración
        Errores de llenado
        Rechazo del SIFEN
        Se inutilizará un rango de facturas
        """
        # TODO: Verificar que no haya factura aprobada en el rango y cambiar estado de ser necesario

        soap_structure = self.evento_inutilizacion_rango_soap_xml(data)
        response = self.env['fe.wsdl'].recepcionEvento(soap_structure, fe_logger)

        if not response:
            _logger.error('No se pudo consultar al servicio de Inutilizar Rango de Facturas de SIFEN')
            return False

        # Actualizamos el estado del invoice
        rResEnviConsLoteDe = response['env:Envelope']['env:Body']['ns2:rRetEnviEventoDe']
        dFecProc = rResEnviConsLoteDe.get('ns2:dFecProc', '')
        gResProcEVe = rResEnviConsLoteDe.get('ns2:gResProcEVe', '')
        dEstRes = gResProcEVe.get('ns2:dEstRes', '')
        id = gResProcEVe.get('ns2:id', '')

        gResProc = gResProcEVe.get('ns2:gResProc', '')
        dCodRes = gResProc.get('ns2:dCodRes', '')
        dMsgRes = gResProc.get('ns2:dMsgRes', '')

        # ======== Datos del Request ========
        fe_rango_object.fecha_procesamiento = self.env['fe.de'].convertir_fecha(dFecProc, True)
        fe_rango_object.codigo_resultado = dCodRes
        fe_rango_object.mensaje_resultado = dEstRes
        fe_rango_object.mensaje_resultado_detalle = f"{dCodRes} - {dMsgRes}"
        fe_rango_object.id_resultado = id

        inutilizado = dCodRes == '0600'

        if inutilizado:
            fe_rango_object.status = 'aprobado'
        else:
            fe_rango_object.status = 'rechazado'

        return inutilizado

    """
    PROCESAR LAS RESPUESTAS DE LOS SERVICIOS
    """

    def procesar_enviar_lote(self, lote, response):
        intento_envio = lote.intento_envio
        INTENTO_REENVIO = self.env.company.fe_intento_reenvio or 3

        # 3 - Si el response es del tipo diccionario es porque se procesó correctamente
        if isinstance(response, dict):
            # =============== Procesamos la respuesta =============
            rResEnviLoteDe = response['env:Envelope']['env:Body']['ns2:rResEnviLoteDe']
            dFecProc = rResEnviLoteDe.get('ns2:dFecProc', '')
            dCodRes = rResEnviLoteDe.get('ns2:dCodRes', '')
            dMsgRes = rResEnviLoteDe.get('ns2:dMsgRes', '')
            dProtConsLote = rResEnviLoteDe.get('ns2:dProtConsLote', '')
            dTpoProces = rResEnviLoteDe.get('ns2:dTpoProces', '')

            # Si el codigo es 0300, el lote ingreso correctamente
            if dCodRes == '0300':
                estado_set = 'en_proceso'
                invoice_estado = 'ingresado'
            else:
                estado_set = 'reenviar'
                if intento_envio == INTENTO_REENVIO:
                    invoice_estado = 'lote_rechazado'
                    estado_set = 'rechazado'
                else:
                    invoice_estado = 'lote_reenviando'
                    intento_envio += 1

            # Atualizamos los datos del lote
            lote.sudo().write(
                {
                    "codigo_resultado": dCodRes,
                    "fecha_procesamiento": self.convertir_fecha(dFecProc, True),
                    "mensaje_resultado": dMsgRes,
                    "numero_lote": dProtConsLote,
                    "tiempo_procesamiento": dTpoProces,
                    "estado_set": estado_set,
                    "estado_lote": "en_proceso",
                    "intento_envio": intento_envio,
                }
            )

            # Actualizamos los estados de las facturas
            for invoice in lote.invoice_ids:
                invoice.write({"estado_set": invoice_estado})

                # Agregamos un registro de logs para la factura
                self.env['fe.de_loggers'].sudo().create(
                    {
                        'invoice': invoice.id,
                        'request': f'Lote Nro: {lote.id}',
                        'response': dMsgRes,
                        'accion': "enviar lote",
                    }
                )

            # Actualizamos los estados de las notas de remision
            for nota_remision in lote.remision_ids:
                nota_remision.write({"estado_set": invoice_estado})

                # Agregamos un registro de logs para la factura
                self.env['fe.de_loggers'].sudo().create(
                    {
                        'remision_id': nota_remision.id,
                        'request': f'Lote Nro: {lote.id}',
                        'response': dMsgRes,
                        'accion': "enviar lote",
                    }
                )
        else:
            # Actualizamos el estado y el intento de envio del lote
            lote.sudo().write(
                {
                    "estado_set": "error",
                    "intento_envio": intento_envio,
                    "mensaje_resultado": "ERROR: Revisar el registro de log",
                }
            )

            # Actualizamos los estados de las facturas
            for invoice in lote.invoice_ids:
                invoice.write({"estado_set": "error_sifen"})

                # Agregamos un registro de logs para la factura
                self.env['fe.de_loggers'].sudo().create(
                    {
                        'invoice': invoice.id,
                        'request': f'Lote Nro: {lote.id}',
                        'response': "lote_rechazado",
                        'accion': "enviar",
                    }
                )

            # Actualizamos los estados de las notas de remision
            for nota_remision in lote.remision_ids:
                nota_remision.write({"estado_set": "error_sifen"})

                # Agregamos un registro de logs para la factura
                self.env['fe.de_loggers'].sudo().create(
                    {
                        'remision_id': nota_remision.id,
                        'request': f'Lote Nro: {lote.id}',
                        'response': "lote_rechazado",
                        'accion': "enviar",
                    }
                )

    def procesar_consultar_lote(self, lote, response):
        # 2 - Si el response es del tipo diccionario es porque se procesó correctamente
        if isinstance(response, dict):
            # =============== Procesamos la respuesta =============
            rResEnviConsLoteDe = response['env:Envelope']['env:Body']['ns2:rResEnviConsLoteDe']
            dFecProc = rResEnviConsLoteDe.get('ns2:dFecProc', '')
            dCodResLot = rResEnviConsLoteDe.get('ns2:dCodResLot', '')
            dMsgResLot = rResEnviConsLoteDe.get('ns2:dMsgResLot', '')
            fecha_procesamiento = self.env['fe.de'].convertir_fecha(dFecProc, True)

            # ======== Datos del lote ========
            lote.sudo().write(
                {
                    'mensaje_resultado': dMsgResLot,
                    'fecha_procesamiento': fecha_procesamiento,
                }
            )
            # Si el lote retorna 0361 sigue en procesamiento
            if dCodResLot == '0361':
                return
            elif dCodResLot == '0160':
                # Ingresa acá cuando hay error de SIFEN, pero con status 200. XML malformado
                # TODO: Verificar que estado se debe agregar en este caso
                # TODO: Aca es donde ingresa cuando el lote sigue consultando muchas veces
                return
            elif dCodResLot == '0362':
                estado = "aprobado"
            elif dCodResLot == '0363':
                estado = 'rechazado'
            elif dCodResLot == '0364':
                estado = 'expirado'
                lote.sudo().write({'estado_set': estado, 'estado_lote': 'finalizado'})
                return
            else:
                estado = "error"

            # Actualizamos el estado del lote
            lote.sudo().write({'estado_set': estado, 'estado_lote': 'finalizado'})

            # ======== Datos del cada DE dentro del lote ========
            gResProcLote = rResEnviConsLoteDe["ns2:gResProcLote"]
            if type(gResProcLote) == dict:
                gResProcLote = [gResProcLote]

            # Guardamos la info de SIFEN por cada factura dentro del lote
            for item_DE in gResProcLote:
                cdc = item_DE['ns2:id']
                dEstRes = item_DE['ns2:dEstRes']
                dProtAut = item_DE.get('ns2:dProtAut', '')

                # Mensajes del DE dentro del lote
                gResProc = item_DE['ns2:gResProc']
                if type(gResProc) == dict:
                    gResProc = [gResProc]
                gResProc_msg = ""
                for i in gResProc:
                    dCodRes = i['ns2:dCodRes']
                    dMsgRes = i['ns2:dMsgRes']
                    gResProc_msg += f"{dCodRes},{dMsgRes};"

                # Obtenemos la factura por el CDC
                invoice = self.env['account.move'].search([('cdc', '=', cdc)])
                if invoice:
                    # Si el invoice está en estado aprobado o cancelado, no hacemos nada
                    if invoice.estado_set not in ['aprobado', 'cancelado']:
                        invoice.fecha_procesamiento_set = fecha_procesamiento
                        invoice.mensaje_set = dEstRes
                        invoice.mensaje_set_detalle = gResProc_msg
                        invoice.nro_transaccion_set = dProtAut
                        # 0260 es el codigo de aprobado
                        if "0260" in gResProc_msg:
                            invoice.estado_set = "aprobado"
                        else:
                            invoice.estado_set = "rechazado"

                # Obtenemos la nota de remision por el CDC
                nota_remision = self.env['notas_remision_account.nota.remision'].search([('cdc', '=', cdc)])
                if nota_remision:
                    # Si la nota de remisión está en estado aprobado o cancelado, no hacemos nada
                    if nota_remision.estado_set not in ['aprobado', 'cancelado']:
                        nota_remision.fecha_procesamiento_set = fecha_procesamiento
                        nota_remision.mensaje_set = dEstRes
                        nota_remision.mensaje_set_detalle = gResProc_msg
                        nota_remision.nro_transaccion_set = dProtAut
                        # 0260 es el codigo de aprobado
                        if "0260" in gResProc_msg:
                            nota_remision.estado_set = "aprobado"
                        else:
                            nota_remision.estado_set = "rechazado"

                # Agregamos un registro de logs para la factura
                self.env['fe.de_loggers'].sudo().create(
                    {
                        'invoice': invoice.id if invoice else None,
                        'remision_id': nota_remision.id if nota_remision else None,
                        'request': f'Lote Nro: {lote.id}',
                        'response': json.dumps(item_DE),
                        'accion': "consultar lote",
                    }
                )
        else:
            # Actualizamos los estados cuando hay error
            lote.sudo().write(
                {
                    "estado_set": "error",
                    "mensaje_resultado": "ERROR: Revisar el registro de log",
                }
            )

            # Actualizamos los estados de las facturas
            for invoice in lote.invoice_ids:
                invoice.write({"estado_set": "error_sifen"})

                # Agregamos un registro de logs para la factura
                self.env['fe.de_loggers'].sudo().create(
                    {
                        'invoice': invoice.id,
                        'request': f'Lote Nro: {lote.id}',
                        'response': "error_sifen",
                        'accion': "consultar lote",
                    }
                )

            # Actualizamos los estados de las notas de remision
            for nota_remision in lote.remision_ids:
                nota_remision.write({"estado_set": "error_sifen"})

                # Agregamos un registro de logs para la nota de remision
                self.env['fe.de_loggers'].sudo().create(
                    {
                        'remision_id': nota_remision.id,
                        'request': f'Lote Nro: {lote.id}',
                        'response': "error_sifen",
                        'accion': "consultar lote",
                    }
                )

    def procesar_consultar_cdc(self, response):
        """
        Este metodo es una instancia del documento consultado, puede ser account.move o notas_remision_account.nota.remision
        """

        # 1 - Si el response es del tipo diccionario es porque se proceso correctamente
        if isinstance(response, dict):
            # =============== Procesamos la respuesta =============
            rEnviConsDeResponse = response['env:Envelope']['env:Body']['ns2:rEnviConsDeResponse']
            dCodRes = rEnviConsDeResponse.get('ns2:dCodRes', '')
            dMsgRes = rEnviConsDeResponse.get('ns2:dMsgRes', '')
            dFecProc = rEnviConsDeResponse.get('ns2:dFecProc', '')
            fecha_procesamiento = self.env['fe.de'].convertir_fecha(dFecProc, True)

            # RUC certificado sin permiso
            if dCodRes == '0421':
                raise exceptions.ValidationError(dMsgRes)

            # No existe DTE consultado
            if dCodRes == '0420':
                _logger.error(dMsgRes)

            # ======== Codigo 0422 = CDC encontrado ========
            xContenDE = rEnviConsDeResponse.get('ns2:xContenDE', '')
            # Convertimos el XML a JSON
            try:
                # Quitamos la declaracion
                xContenDE = xContenDE.replace('<?xml version="1.0" encoding="UTF-8"?>', '')
                # Agregamos el elemento raiz para que xmltodict pueda convertirlo a JSON
                xContenDE = '<?xml version="1.0" encoding="UTF-8"?><root>' + xContenDE.strip() + '</root>'
                xmldict = xmltodict.parse(xContenDE)

                # Obtenemos los elementos padres
                rDE = xmldict['root']['rDE']
                dProtAut = xmldict['root']['dProtAut']
                xContEv = xmldict['root']['xContEv']

                # Variables
                mensaje_set = "Aprobado. Consulta a través de CDC"
                mensaje_anulacion = ""
                estado_set = "aprobado"

                # Si hay un evento
                if xContEv:
                    rContEv = xContEv['rContEv']

                    # Obtenemos el evento
                    xEvento = rContEv['xEvento']
                    rGesEve = xEvento['rGesEve']
                    rEve = rGesEve['rEve']
                    gGroupTiEvt = rEve['gGroupTiEvt']

                    # Obtenemos el estado del evento
                    rResEnviEventoDe = rContEv['rResEnviEventoDe']
                    rRetEnviEventoDe = rResEnviEventoDe['rRetEnviEventoDe']
                    dFecProc = rRetEnviEventoDe['dFecProc']
                    gResProcEVe = rRetEnviEventoDe['gResProcEVe']
                    dEstRes = gResProcEVe['dEstRes']
                    dProtAut_ev = gResProcEVe['dProtAut']
                    gResProc = gResProcEVe['gResProc']
                    dCodRes_ev = gResProc['dCodRes']
                    dMsgRes_ev = gResProc['dMsgRes']

                    # Verificamos si el evento contiene el registro de cancelar
                    if 'rGeVeCan' in gGroupTiEvt:
                        mOtEve = gGroupTiEvt['rGeVeCan']['mOtEve']
                        mensaje_set = f"Cancelado: {mOtEve}"
                        mensaje_anulacion = f"{dProtAut_ev}: {dEstRes} - {dCodRes_ev}: {dMsgRes_ev}"
                        estado_set = "cancelado"

                    # TODO: Actualmente solo retorna el evento de cancelación, verificar si hay otros eventos

                self.write(
                    {
                        "fecha_procesamiento_set": fecha_procesamiento,
                        "mensaje_set": mensaje_set,
                        "mensaje_set_detalle": mensaje_set,
                        "mensaje_anulacion": mensaje_anulacion,
                        "nro_transaccion_set": dProtAut,
                        "estado_set": estado_set,
                    }
                )

                # Cancelamos la factura en el odoo si aun no está cancelada
                if estado_set == "cancelado" and self.state != "cancel":
                    self.button_cancel()

            except Exception as e:
                _logger.debug(e)
                return