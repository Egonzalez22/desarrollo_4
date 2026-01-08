import base64
import json
import logging
import traceback
from datetime import datetime

import dicttoxml
from lxml import etree as lxml_ET
from odoo import _, exceptions, models

_logger = logging.getLogger(__name__)

dicttoxml.LOG.setLevel(logging.ERROR)


class GenerarDocumentos(models.AbstractModel):
    _inherit = 'fe.de'
    _description = 'Generar documentos electronicos para cada accion que se puede realizar con la SIFEN'

    def debug_mode(self, xmldict):
        DE = xmldict['rDE']['DE']
        DE['gOpeDE']["dInfoFisc"] = "Información de interés del Fisco respecto al DE"
        DE['gDatGralOpe']['gEmis']['dNomEmi'] = 'DE generado en ambiente de prueba - sin valor comercial ni fiscal'

        items = DE['gDtipDE']["gCamItem"]
        for item in items:
            item["dDesProSer"] = 'DE generado en ambiente de prueba - sin valor comercial ni fiscal'

    def generar_cdc(self, xmldict):
        """
        Genera el codigo de control del documento electronico
        """
        try:
            # Codigo de seguridad
            if not self.cod_seguridad:
                self.cod_seguridad = self.get_cod_seguridad()

            DE = xmldict['rDE']['DE']
            gtimb = DE['gTimb']
            gdatgralope = DE['gDatGralOpe']
            gopede = DE['gOpeDE']
            gemis = DE['gDatGralOpe']['gEmis']
            cdc = [
                str(gtimb['iTiDE']).zfill(2),
                str(gemis['dRucEm']).zfill(8),
                str(gemis['dDVEmi']),
                str(gtimb['dEst']).zfill(3),
                str(gtimb['dPunExp']).zfill(3),
                str(gtimb['dNumDoc']).zfill(7),
                str(gemis['iTipCont']),
                gdatgralope['dFeEmiDE'].split('T')[0].replace('-', ''),
                gopede['iTipEmi'],
                self.cod_seguridad,
            ]
            cdc = map(lambda x: str(x), cdc)
            cdc = ''.join(cdc)
            cdc_dv = self.get_digito_verificador(cdc)
            cdc = "{}{}".format(cdc, cdc_dv)

            return cdc, cdc_dv
        except Exception as ex:
            self.log_errors(ex, "generar_cdc", False)

    def generar_json(self):
        try:
            xmldict = {
                # AA. Campos que identifican el formato electrónico XML (AA001-AA009)
                'rDE': {
                    'dVerFor': self.getdVerFor(),
                    # A. Campos firmados del Documento Electrónico (A001-A099)
                    'DE': {
                        # A003: Dígito verificador del identificador del DE
                        'dDVId': "",
                        # A004: Fecha y hora de firma del DE
                        'dFecFirma': self.getdFecFirma(),
                        # A005: Sistema facturador del Cliente
                        'dSisFact': 1,
                        # B. Campos inherentes a la operación de Documentos Electrónicos (B001-B099)
                        'gOpeDE': self.getgOpeDE(),
                        # C. Campos de datos del Timbrado (C001-C099)
                        'gTimb': self.getgTimb(),
                        # D. Campos Generales del Documento Electrónico DE (D001-D299)
                        'gDatGralOpe': {
                            # D002: Fecha y hora de emisión del DE
                            'dFeEmiDE': self.getdFeEmiDE(),
                            # D1. Campos inherentes a la operación comercial (D010-D099)
                            'gOpeCom': self.getgOpeCom(),
                            # D2. Campos que identifican al emisor del Documento Electrónico DE (D100-D129)
                            'gEmis': self.getgEmis(),
                            # D3. Campos que identifican al receptor del Documento Electrónico DE (D200-D299)
                            'gDatRec': self.getgDatRec(),
                        },
                        # E. Campos específicos por tipo de Documento Electrónico (E001-E009)
                        'gDtipDE': self.getgDtipDE(),
                    },
                }
            }
            # Campos que no corresponden a la nota de remision
            if xmldict.get('rDE').get('DE').get('gTimb').get('iTiDE') == 7:
                xmldict.get('rDE').get('DE').get('gDatGralOpe').pop('gOpeCom')

            if xmldict.get('rDE').get('DE').get('gTimb').get('iTiDE') != 7:
                if self.getgTotSub():
                    xmldict['rDE']['DE']['gTotSub'] = self.getgTotSub()

                if self.getgCamDEAsoc():
                    xmldict['rDE']['DE']['gCamDEAsoc'] = self.getgCamDEAsoc()

            # En debug mode, cambiamos las descripciones de los campos
            if self.env.company.fe_ambiente == "test":
                self.debug_mode(xmldict)

            return xmldict
        except Exception as ex:
            self.log_errors(ex, "generar_json", False)

    def factura_generar_xml(self, xmldict, de_logger):
        try:
            # Agregamos el CDC y el DV al diccionario
            xmldict['rDE']['DE']['dDVId'] = self.digito_verificador
            xmldict['rDE']['DE']['gOpeDE']['dCodSeg'] = self.cod_seguridad

            # Guardamos el JSON generado
            filename = self.get_nombre_archivo("json", "json")
            data_b64 = base64.b64encode(json.dumps(xmldict).encode('utf-8'))
            de_logger.sudo().write({'json_file': data_b64, 'json_file_name': filename})

            # Del json quitamos el array de gCamItem para generar por separado en el XML
            gCamItem = xmldict['rDE']['DE']['gDtipDE']['gCamItem']
            del xmldict['rDE']['DE']['gDtipDE']['gCamItem']

            # Del json quitamos los documentos asociados, para generar por separado en el XML
            gCamDEAsoc = False
            if xmldict['rDE']['DE'].get('gCamDEAsoc'):
                gCamDEAsoc = xmldict['rDE']['DE']['gCamDEAsoc']
                del xmldict['rDE']['DE']['gCamDEAsoc']

            # Si es nota de remision quitamos el gTransp para ubicar al final del grupo en el xml
            if self.tipo_documento == 'nota_remision':
                gTransp = xmldict['rDE']['DE']['gDtipDE']['gTransp']
                del xmldict['rDE']['DE']['gDtipDE']['gTransp']

            # Del Json quitamos la actividad economica para generar de la forma que se necesita gActEco
            gActEco = False
            if xmldict['rDE']['DE']['gDatGralOpe']['gEmis'].get('gActEco'):
                gActEco = xmldict['rDE']['DE']['gDatGralOpe']['gEmis']['gActEco']
                del xmldict['rDE']['DE']['gDatGralOpe']['gEmis']['gActEco']

            # ========================== ========================== ========================== =====
            # ========================== Convertimos el diccionario a xml ========================== 
            # ========================== ========================== ========================== =====
            dexml = dicttoxml.dicttoxml(xmldict, custom_root='rDE', attr_type=False, root=False)
            rde = lxml_ET.fromstring(dexml, parser=lxml_ET.XMLParser(encoding='utf-8'))
            # ========================== ========================== ========================== =====
            # ========================== ========================== ========================== =====
            # ========================== ========================== ========================== =====

            # Al final de gEmis, agregamos los campos de actividad economica
            if gActEco:
                dEmailE = rde.find('.//gEmis')
                for acteco in gActEco:
                    acteco_xml = dicttoxml.dicttoxml(acteco, attr_type=False, custom_root='gActEco')
                    acteco_elemento = lxml_ET.fromstring(acteco_xml)
                    dEmailE.append(acteco_elemento)

            # Agregamos las lineas de detalle de factura
            gDtipDE = rde.find('.//gDtipDE')
            for linea in gCamItem:
                linea_xml = dicttoxml.dicttoxml(linea, attr_type=False, custom_root='gCamItem')
                linea_elemento = lxml_ET.fromstring(linea_xml)
                gDtipDE.append(linea_elemento)
            
            # Si es nota de remision, agregamos el gTransp al final del grupo
            if self.tipo_documento == 'nota_remision':
                gtransp_xml = dicttoxml.dicttoxml(gTransp, attr_type=False, custom_root='gTransp')
                linea_gtransp = lxml_ET.fromstring(gtransp_xml)
                gDtipDE.append(linea_gtransp)

            # Agregamos los documentos asociados
            if gCamDEAsoc:
                Nodo_DE = rde.find('.//DE')
                for doc_asoc in gCamDEAsoc:
                    doc_asoc_xml = dicttoxml.dicttoxml(doc_asoc, attr_type=False, custom_root='gCamDEAsoc')
                    doc_asoc_elemento = lxml_ET.fromstring(doc_asoc_xml)
                    Nodo_DE.append(doc_asoc_elemento)

            # Agregamos los atributos
            rde.set("xmlns", "http://ekuatia.set.gov.py/sifen/xsd")
            rde.set(
                "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
                "http://ekuatia.set.gov.py/sifen/xsd siRecepDE_v150.xsd",
            )
            de = rde.find("DE")
            de.set("Id", self.cdc)

            return rde
        except Exception as ex:
            self.log_errors(ex, "factura_generar_xml", False)

    def factura_soap_xml(self, xde, fe_logger):
        try:
            SOAP_NAME_SPACE = '{http://www.w3.org/2003/05/soap-envelope}'
            xmlns = {'env': SOAP_NAME_SPACE.strip('{}')}

            if isinstance(xde, str):
                xde = lxml_ET.parse(xde).getroot()

            nodo_raiz = lxml_ET.Element(SOAP_NAME_SPACE + 'Envelope', nsmap=xmlns)
            lxml_ET.SubElement(nodo_raiz, SOAP_NAME_SPACE + 'Header')
            body = lxml_ET.SubElement(nodo_raiz, SOAP_NAME_SPACE + 'Body')

            renvide = lxml_ET.SubElement(body, 'rEnviDe', xmlns="http://ekuatia.set.gov.py/sifen/xsd")

            did_el = lxml_ET.SubElement(renvide, 'dId')
            did_el.text = str(self.env['ir.sequence'].sudo().next_by_code('id_mensaje'))

            dxde_el = lxml_ET.SubElement(renvide, 'xDE')
            dxde_el.append(xde)

            # Archivo SOAP a ser enviado
            soap_structure = self.clean_up_string(self.to_string_xml(nodo_raiz, xml_declaration=True))

            # Guardamos en la BD
            filename = self.get_nombre_archivo("soap", "xml")
            data_b64 = base64.b64encode(soap_structure)
            fe_logger.write({'xml_soap': data_b64, 'xml_soap_name': filename})

            return soap_structure
        except Exception as ex:
            self.log_errors(ex, "factura_soap_xml", False)

    def factura_consulta_soap_xml(self, cdc):
        try:
            SOAP_NAME_SPACE = '{http://www.w3.org/2003/05/soap-envelope}'
            xmlns = {'env': SOAP_NAME_SPACE.strip('{}')}

            nodo_raiz = lxml_ET.Element(SOAP_NAME_SPACE + 'Envelope', nsmap=xmlns)
            lxml_ET.SubElement(nodo_raiz, SOAP_NAME_SPACE + 'Header')
            body = lxml_ET.SubElement(nodo_raiz, SOAP_NAME_SPACE + 'Body')

            rEnviConsDe = lxml_ET.SubElement(body, 'rEnviConsDeRequest', xmlns="http://ekuatia.set.gov.py/sifen/xsd")

            did_el = lxml_ET.SubElement(rEnviConsDe, 'dId')
            did_el.text = str(self.env['ir.sequence'].sudo().next_by_code('id_mensaje'))

            dcdc_el = lxml_ET.SubElement(rEnviConsDe, 'dCDC')
            dcdc_el.text = str(cdc)

            # Archivo SOAP a ser enviado
            soap_structure = self.clean_up_string(self.to_string_xml(nodo_raiz, xml_declaration=True))

            return soap_structure
        except Exception as ex:
            self.log_errors(ex, "factura_consulta_soap_xml", False)

    def lote_recepcion_soap_xml(self, zip_file):
        try:
            SOAP_NAME_SPACE = '{http://www.w3.org/2003/05/soap-envelope}'
            xmlns = {'env': SOAP_NAME_SPACE.strip('{}')}

            nodo_raiz = lxml_ET.Element(SOAP_NAME_SPACE + 'Envelope', nsmap=xmlns)
            lxml_ET.SubElement(nodo_raiz, SOAP_NAME_SPACE + 'Header')
            body = lxml_ET.SubElement(nodo_raiz, SOAP_NAME_SPACE + 'Body')

            rEnvioLote = lxml_ET.SubElement(body, 'rEnvioLote', xmlns="http://ekuatia.set.gov.py/sifen/xsd")

            did_el = lxml_ET.SubElement(rEnvioLote, 'dId')
            did_el.text = str(self.env['ir.sequence'].sudo().next_by_code('id_mensaje'))

            xde_el = lxml_ET.SubElement(rEnvioLote, 'xDE')
            xde_el.text = zip_file

            # Archivo SOAP a ser enviado
            soap_structure = self.clean_up_string(self.to_string_xml(nodo_raiz, xml_declaration=True))

            return soap_structure
        except Exception as ex:
            self.log_errors(ex, "lote_recepcion_soap_xml", False)

    def lote_consulta_soap_xml(self, nro_lote):
        try:
            SOAP_NAME_SPACE = '{http://www.w3.org/2003/05/soap-envelope}'

            xmlns = {'env': SOAP_NAME_SPACE.strip('{}')}

            nodo_raiz = lxml_ET.Element(SOAP_NAME_SPACE + 'Envelope', nsmap=xmlns)
            lxml_ET.SubElement(nodo_raiz, SOAP_NAME_SPACE + 'Header')
            body = lxml_ET.SubElement(nodo_raiz, SOAP_NAME_SPACE + 'Body')

            rEnviConsLoteDe = lxml_ET.SubElement(body, 'rEnviConsLoteDe', xmlns="http://ekuatia.set.gov.py/sifen/xsd")

            did_el = lxml_ET.SubElement(rEnviConsLoteDe, 'dId')
            did_el.text = str(self.env['ir.sequence'].sudo().next_by_code('id_mensaje'))

            conslote_el = lxml_ET.SubElement(rEnviConsLoteDe, 'dProtConsLote')
            conslote_el.text = str(nro_lote)

            # Archivo SOAP a ser enviado
            soap_structure = self.clean_up_string(self.to_string_xml(nodo_raiz, xml_declaration=True))

            return soap_structure
        except Exception as ex:
            self.log_errors(ex, "lote_consulta_soap_xml", False)

    def ruc_consulta_soap_xml(self, nro_ruc):
        try:
            SOAP_NAME_SPACE = '{http://www.w3.org/2003/05/soap-envelope}'

            xmlns = {'env': SOAP_NAME_SPACE.strip('{}')}

            nodo_raiz = lxml_ET.Element(SOAP_NAME_SPACE + 'Envelope', nsmap=xmlns)
            lxml_ET.SubElement(nodo_raiz, SOAP_NAME_SPACE + 'Header')
            body = lxml_ET.SubElement(nodo_raiz, SOAP_NAME_SPACE + 'Body')

            rEnviConsRUC = lxml_ET.SubElement(body, 'rEnviConsRUC', xmlns="http://ekuatia.set.gov.py/sifen/xsd")

            did_el = lxml_ET.SubElement(rEnviConsRUC, 'dId')
            did_el.text = str(self.env['ir.sequence'].sudo().next_by_code('id_mensaje'))

            ruccons_el = lxml_ET.SubElement(rEnviConsRUC, 'dRUCCons')
            ruccons_el.text = str(nro_ruc)

            # Archivo SOAP a ser enviado
            soap_structure = self.clean_up_string(self.to_string_xml(nodo_raiz, xml_declaration=True))

            return soap_structure
        except Exception as ex:
            self.log_errors(ex, "ruc_consulta_soap_xml", False)

    def evento_cancelacion_soap_xml(self, cdc, motivo, de_logger):
        try:
            SOAP_NAME_SPACE = '{http://www.w3.org/2003/05/soap-envelope}'
            XSI_NAME_SPACE = '{http://www.w3.org/2001/XMLSchema-instance}'
            SIFEN_NAME_SPACE = '{http://ekuatia.set.gov.py/sifen/xsd}'
            
            # Obtenemos la fecha/hora del servidor de la set
            now_utc = self.obtener_hora_actual_set()
            now = self.obtener_fecha_hora_local(now_utc)
            tnow = self.convertir_fecha(now)

            gdid = self.get_cod_seguridad()

            attr_qname = lxml_ET.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
            xmlns = {'env': SOAP_NAME_SPACE.strip('{}'), 'xsi': XSI_NAME_SPACE.strip('{}')}

            ele = lxml_ET.Element(SOAP_NAME_SPACE + 'Envelope', nsmap=xmlns)
            lxml_ET.SubElement(ele, SOAP_NAME_SPACE + 'Header')
            sbody = lxml_ET.SubElement(ele, SOAP_NAME_SPACE + 'Body')
            rEnviEventoDe = lxml_ET.SubElement(sbody, 'rEnviEventoDe', xmlns=SIFEN_NAME_SPACE.strip('{}'))
            did = lxml_ET.SubElement(rEnviEventoDe, 'dId')
            did.text = str(gdid)
            dEvReg = lxml_ET.SubElement(rEnviEventoDe, 'dEvReg')
            gGroupGesEve = lxml_ET.SubElement(
                dEvReg,
                'gGroupGesEve',
                {attr_qname: 'http://ekuatia.set.gov.py/sifen/xsd siRecepEvento_v150.xsd'},
                xmlns=SIFEN_NAME_SPACE.strip('{}'),
                nsmap={'xsi': XSI_NAME_SPACE.strip('{}')},
            )
            rGesEve = lxml_ET.SubElement(gGroupGesEve, 'rGesEve')
            reve = lxml_ET.SubElement(rGesEve, 'rEve')
            reve.attrib['Id'] = str(gdid)
            dFecFirma = lxml_ET.SubElement(reve, 'dFecFirma')
            dFecFirma.text = tnow
            dVerFor = lxml_ET.SubElement(reve, 'dVerFor')
            dVerFor.text = self.getdVerFor()
            gGroupTiEvt = lxml_ET.SubElement(reve, 'gGroupTiEvt')
            rGeVeCan = lxml_ET.SubElement(gGroupTiEvt, 'rGeVeCan')

            GId = lxml_ET.SubElement(rGeVeCan, 'Id')
            GId.text = cdc

            mOtEve = lxml_ET.SubElement(rGeVeCan, 'mOtEve')
            mOtEve.text = str(motivo)

            signature = self.firmar_xml_evento(rEnviEventoDe, str(gdid), None)
            rGesEve.append(signature)

            # Guardamos en la BD
            filename = self.get_nombre_archivo("firmado", "xml")
            data_b64 = base64.b64encode(self.to_string_xml(ele))
            de_logger.sudo().write({'xml_firmado': data_b64, 'xml_firmado_name': filename})

            sele = self.clean_up_string(self.to_string_xml(ele, xml_declaration=True))
            return sele

        except Exception as ex:
            self.log_errors(ex, "evento_cancelacion_soap_xml", False)

    def evento_inutilizacion_soap_xml(self, fact_inicio, fact_fin, motivo):
        try:
            SOAP_NAME_SPACE = '{http://www.w3.org/2003/05/soap-envelope}'
            XSI_NAME_SPACE = '{http://www.w3.org/2001/XMLSchema-instance}'
            SIFEN_NAME_SPACE = '{http://ekuatia.set.gov.py/sifen/xsd}'

            # Obtenemos la fecha/hora del servidor de la set
            now_utc = self.obtener_hora_actual_set()
            now = self.obtener_fecha_hora_local(now_utc)
            tnow = self.convertir_fecha(now)

            gdid = self.get_cod_seguridad()

            attr_qname = lxml_ET.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
            xmlns = {'env': SOAP_NAME_SPACE.strip('{}'), 'xsi': XSI_NAME_SPACE.strip('{}')}

            ele = lxml_ET.Element(SOAP_NAME_SPACE + 'Envelope', nsmap=xmlns)
            lxml_ET.SubElement(ele, SOAP_NAME_SPACE + 'Header')
            sbody = lxml_ET.SubElement(ele, SOAP_NAME_SPACE + 'Body')
            rEnviEventoDe = lxml_ET.SubElement(sbody, 'rEnviEventoDe', xmlns=SIFEN_NAME_SPACE.strip('{}'))
            did = lxml_ET.SubElement(rEnviEventoDe, 'dId')
            did.text = str(gdid)
            dEvReg = lxml_ET.SubElement(rEnviEventoDe, 'dEvReg')
            gGroupGesEve = lxml_ET.SubElement(
                dEvReg,
                'gGroupGesEve',
                {attr_qname: 'http://ekuatia.set.gov.py/sifen/xsd siRecepEvento_v150.xsd'},
                xmlns=SIFEN_NAME_SPACE.strip('{}'),
                nsmap={'xsi': XSI_NAME_SPACE.strip('{}')},
            )
            rGesEve = lxml_ET.SubElement(gGroupGesEve, 'rGesEve')
            reve = lxml_ET.SubElement(rGesEve, 'rEve')
            reve.attrib['Id'] = str(gdid)
            dFecFirma = lxml_ET.SubElement(reve, 'dFecFirma')
            dFecFirma.text = tnow
            dVerFor = lxml_ET.SubElement(reve, 'dVerFor')
            dVerFor.text = self.getdVerFor()
            gGroupTiEvt = lxml_ET.SubElement(reve, 'gGroupTiEvt')
            rGeVeInu = lxml_ET.SubElement(gGroupTiEvt, 'rGeVeInu')

            # Nro de Timbrado
            dNumTim = lxml_ET.SubElement(rGeVeInu, 'dNumTim')
            dNumTim.text = str(self.getdNumTim())

            # Establecimiento
            dEst = lxml_ET.SubElement(rGeVeInu, 'dEst')
            dEst.text = str(self.getdEst())

            # Punto de Expedicion
            dPunExp = lxml_ET.SubElement(rGeVeInu, 'dPunExp')
            dPunExp.text = str(self.getdPunExp())

            # Nro inicio de Factura
            dNumIn = lxml_ET.SubElement(rGeVeInu, 'dNumIn')
            dNumIn.text = fact_inicio.zfill(7)

            # Nro fin de Factura
            dNumFin = lxml_ET.SubElement(rGeVeInu, 'dNumFin')
            dNumFin.text = fact_fin.zfill(7)

            # Tipo de documento, por el momento es factura electronica
            iTiDE = lxml_ET.SubElement(rGeVeInu, 'iTiDE')
            if self.tipo_documento == 'out_invoice':
                iTiDE.text = "1"
            if self.tipo_documento == 'out_refund':
                iTiDE.text = "5"
            if self.tipo_documento == 'nota_remision':
                iTiDE.text = "7"
            if self.tipo_documento == 'autofactura':
                iTiDE.text = "4"
            if self.tipo_documento == 'nota_debito':
                iTiDE.text = "6"

            mOtEve = lxml_ET.SubElement(rGeVeInu, 'mOtEve')
            mOtEve.text = str(motivo)

            signature = self.firmar_xml_evento(rEnviEventoDe, str(gdid), None)
            rGesEve.append(signature)

            sele = self.clean_up_string(self.to_string_xml(ele, xml_declaration=True))
            return sele

        except Exception as ex:
            self.log_errors(ex, "evento_inutilizacion_soap_xml", False)

    def evento_inutilizacion_rango_soap_xml(self, data):
        try:
            SOAP_NAME_SPACE = '{http://www.w3.org/2003/05/soap-envelope}'
            XSI_NAME_SPACE = '{http://www.w3.org/2001/XMLSchema-instance}'
            SIFEN_NAME_SPACE = '{http://ekuatia.set.gov.py/sifen/xsd}'

            # Obtenemos la fecha/hora del servidor de la set
            now_utc = self.obtener_hora_actual_set()
            now = self.obtener_fecha_hora_local(now_utc)
            tnow = self.convertir_fecha(now)

            gdid = self.get_cod_seguridad()

            attr_qname = lxml_ET.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
            xmlns = {'env': SOAP_NAME_SPACE.strip('{}'), 'xsi': XSI_NAME_SPACE.strip('{}')}

            ele = lxml_ET.Element(SOAP_NAME_SPACE + 'Envelope', nsmap=xmlns)
            lxml_ET.SubElement(ele, SOAP_NAME_SPACE + 'Header')
            sbody = lxml_ET.SubElement(ele, SOAP_NAME_SPACE + 'Body')
            rEnviEventoDe = lxml_ET.SubElement(sbody, 'rEnviEventoDe', xmlns=SIFEN_NAME_SPACE.strip('{}'))
            did = lxml_ET.SubElement(rEnviEventoDe, 'dId')
            did.text = str(gdid)
            dEvReg = lxml_ET.SubElement(rEnviEventoDe, 'dEvReg')
            gGroupGesEve = lxml_ET.SubElement(
                dEvReg,
                'gGroupGesEve',
                {attr_qname: 'http://ekuatia.set.gov.py/sifen/xsd siRecepEvento_v150.xsd'},
                xmlns=SIFEN_NAME_SPACE.strip('{}'),
                nsmap={'xsi': XSI_NAME_SPACE.strip('{}')},
            )
            rGesEve = lxml_ET.SubElement(gGroupGesEve, 'rGesEve')
            reve = lxml_ET.SubElement(rGesEve, 'rEve')
            reve.attrib['Id'] = str(gdid)
            dFecFirma = lxml_ET.SubElement(reve, 'dFecFirma')
            dFecFirma.text = tnow
            dVerFor = lxml_ET.SubElement(reve, 'dVerFor')
            dVerFor.text = self.getdVerFor()
            gGroupTiEvt = lxml_ET.SubElement(reve, 'gGroupTiEvt')
            rGeVeInu = lxml_ET.SubElement(gGroupTiEvt, 'rGeVeInu')

            # Nro de Timbrado
            dNumTim = lxml_ET.SubElement(rGeVeInu, 'dNumTim')
            dNumTim.text = str(data.get("nro_timbrado"))

            # Establecimiento
            dEst = lxml_ET.SubElement(rGeVeInu, 'dEst')
            dEst.text = str(data.get("establecimiento"))

            # Punto de Expedicion
            dPunExp = lxml_ET.SubElement(rGeVeInu, 'dPunExp')
            dPunExp.text = str(data.get("punto_expedicion"))

            # Nro inicio de Factura
            dNumIn = lxml_ET.SubElement(rGeVeInu, 'dNumIn')
            dNumIn.text = data.get("fact_inicio").zfill(7)

            # Nro fin de Factura
            dNumFin = lxml_ET.SubElement(rGeVeInu, 'dNumFin')
            dNumFin.text = data.get("fact_fin").zfill(7)

            # Tipo de documento, por el momento es factura electronica
            iTiDE = lxml_ET.SubElement(rGeVeInu, 'iTiDE')
            tipo_documento_electronico = data.get("tipo_documento_electronico")
            if tipo_documento_electronico == 'out_invoice':
                iTiDE.text = "1"
            if tipo_documento_electronico == 'out_refund':
                iTiDE.text = "5"
            if tipo_documento_electronico == 'nota_remision':
                iTiDE.text = "7"
            if tipo_documento_electronico == 'autofactura':
                iTiDE.text = "4"
            if tipo_documento_electronico == 'nota_debito':
                iTiDE.text = "6"

            mOtEve = lxml_ET.SubElement(rGeVeInu, 'mOtEve')
            mOtEve.text = str(data.get("motivo"))

            signature = self.firmar_xml_evento(rEnviEventoDe, str(gdid), None)
            rGesEve.append(signature)

            sele = self.clean_up_string(self.to_string_xml(ele, xml_declaration=True))
            return sele

        except Exception as ex:
            self.log_errors(ex, "evento_inutilizacion_rango_soap_xml", False)
