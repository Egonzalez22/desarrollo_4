import logging
import re

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DocumentoElectronico(models.AbstractModel):
    _name = 'fe.de'
    _description = 'Documento electrónico'

    # CDC, Codigo de seguridad, Dígito verificador
    cod_seguridad = fields.Char(string="Código de seguridad", copy=False)
    digito_verificador = fields.Integer(string="Dígito verificador", copy=False)
    cdc = fields.Char(string="CDC", copy=False, index=True)
    version_formato = fields.Char(string="Versión del documento", copy=False, default="150")
    validacion_esquema = fields.Char(string="Validación de esquema", copy=False)
    error_generacion = fields.Text(string="Error de generación", copy=False)

    # KUDE XML
    xml_file_name = fields.Char(string="Nombre Archivo XML", copy=False)
    xml_file = fields.Binary(string="Archivo XML", copy=False)
    fecha_hora_firma = fields.Datetime(string="Fecha de firma", copy=False)

    # KUDE QR
    dcarQR = fields.Char('URL Ekuatia', copy=False)
    fe_qr_code = fields.Binary(string="QR Code", compute="generate_qr_code_fe", copy=False)

    # SIFEN
    fe_valida = fields.Boolean(string="Factura electrónica válida", default=False, copy=False)
    sifen_requests = fields.One2many("fe.de_loggers", "invoice", string="Requests", copy=False)
    sifen_requests_nr = fields.One2many("fe.de_loggers", "remision_id", string="Requests", copy=False)
    lote_id = fields.Many2one("fe.lote", string="Lote", copy=False)
    lote_nr_id = fields.Many2one("fe.lote", string="Lote de remision", copy=False)
    estado_set = fields.Selection(
        string="Estado SET",
        selection=[
            ('borrador', 'Borrador'),  # Gestion local
            ('pendiente', 'Pendiente asociar a Lote'),  # Gestion local
            ('preparado', 'Asociado a Lote'),  # Gestion local
            ('ingresado', 'Lote Ingresado'),  # SIFEN Lote
            ('error_sifen', 'Error SIFEN'),  # SIFEN Lote
            ('lote_rechazado', 'Lote Rechazado'),  # SIFEN Lote
            ('lote_reenviando', 'Lote Intento de Reenvio'),  # SIFEN Lote
            ('aprobado', 'Aprobado'),  # SIFEN DE
            ('rechazado', 'Rechazado'),  # SIFEN DE
            ('cancelado', 'Cancelado'),  # SIFEN DE, Gestion local
            ('inutilizado', 'Inutilizado'),  # SIFEN DE, Gestion local
        ],
        copy=False,
        default="borrador",
        index=True,
    )
    mensaje_set = fields.Text(string="Mensaje SET", copy=False)
    mensaje_set_detalle = fields.Text(string="Mensaje SET Detalles", copy=False)
    fecha_procesamiento_set = fields.Datetime(string="Fecha de procesamiento", copy=False)
    nro_transaccion_set = fields.Char(string="Número de transacción", copy=False)
    mensaje_anulacion = fields.Text(string="Mensaje de error de Anulación", copy=False)
    estado_anulacion = fields.Selection(
        string="Estado de anulación",
        selection=[
            ('CANCELADO', 'Cancelado'),
            ('NO_CANCELADO', 'No Cancelado'),
            ('INUTILIZADO', 'Inutilizado'),
            ('NO_INUTILIZADO', 'No Inutilizado'),
        ],
        copy=False,
    )
    motivo_cancelacion = fields.Char(string='Motivo de cancelación')

    tipo_emision = fields.Selection(
        string="Tipo de emision",
        selection=[('1', 'Normal'), ('2', 'Contingencia')],
        default='1',
    )
    info_interes_fisco = fields.Char(string='Información de interés Fisco')
    tipo_operacion = fields.Selection(
        string="Tipo de Operación",
        selection=[('1', 'B2B'), ('2', 'B2C'), ('3', 'B2G'), ('4', 'B2F')],
        default="2",
        required=True,
        track_visibility="onchange",
    )
    tipo_documento = fields.Selection(
        string="Tipo de documento",
        selection=[
            ('out_invoice', 'Factura'),
            ('out_refund', 'Nota de credito'),
            ('nota_remision', 'Nota de remision'),
            ('autofactura', 'Autofactura'),
            ('nota_debito', 'Nota de débito'),
        ],
        default="out_invoice",
    )
    documento_electronico = fields.Boolean(string="Es documento electrónico", compute="_compute_documento_electronico")
    documento_procesado_mail = fields.Boolean(string="Documento procesado para envío por mail", copy=False, default=False)
    documento_enviado_mail = fields.Boolean(string="Documento enviado por mail", copy=False, default=False)

    # Este campo se debe usar para concatenar información extra que no se puede guardar en otros campos, Ej.: Observacion, comentarios para el cliente, etc
    # Se puede mostrar en el kude, pero no se agrega en el proceso de firmado del XML
    info_adicional = fields.Char(string="Información adicional", copy=False)

    # Campos para compras publicas
    dncp_cod_modalidad = fields.Char(string="Código de la modalidad", copy=False)
    dncp_cod_entidad = fields.Char(string="Código de la entidad", copy=False)
    dncp_cod_anho = fields.Char(string="Código del año", copy=False)
    dncp_cod_sec = fields.Char(string="Código de la secuencia", copy=False)
    dncp_fecha_emision = fields.Date(string="Fecha de emisión", copy=False)


    """ 
    Acciones para preparar, enviar y consultar DE
    """

    @api.onchange("journal_id")
    def _compute_documento_electronico(self):
        for rec in self:
            resultado = rec.es_documento_electronico()
            rec.documento_electronico = resultado

    def preparar_documento_electronico(self):
        """
        Método que se encarga de generar el XML para la factura electrónica.
        En este método solo pueden entrar facturas en borrador, pendiente, error_sifen, lote_rechazado, lote_reenviando y rechazado
        """
        # Cada vez que ingresa a este metodo estado_set se cambia a pendiente se regenera el XML
        self.verificar_nro_factura(self.tipo_documento)
        self.validar_documento_electronico()

        # Guardamos la fecha de emisión de la factura
        # La fecha de emisión solamente se obtiene cuando se confirma por primera vez el DE
        if not self.invoice_datetime:
            fecha = self.env["fe.de"].obtener_hora_actual_set()
            self.invoice_datetime = fecha

        # Creamos un logger según el tipo de documento
        fe_logger = (
            self.env['fe.de_loggers']
            .sudo()
            .create(
                {
                    "invoice": self.id if self.tipo_documento != 'nota_remision' else None,
                    "remision_id": self.id if self.tipo_documento == 'nota_remision' else None,
                    "accion": "preparar",
                    "tipo_documento_electronico": self.tipo_documento,
                },
            )
        )

        # Obtenemos todos los datos en formato XML
        xmldict = self.generar_json()
        if not xmldict:
            self.log_errors(None, "xmldict vacio", False)
            return

        # Obtenemos el CDC y el digito verificador del mismo
        cdc, cdc_cv = self.generar_cdc(xmldict)
        if not cdc:
            self.log_errors(None, "CDC vacio", False)
            return

        # Si el estado de la factura es rechazado, verificamos si cambio el CDC
        if self.estado_set == "rechazado" and cdc != self.cdc:
            msg = f"El CDC de la factura {self.name} ha cambiado. Si hay error con SIFEN favor esperar y consultar por CDC, caso contrario se debe inutilizar el documento y generar uno nuevo."
            exception = exceptions.ValidationError(msg)
            self.log_errors(exception, "generar documento", True, "CDC cambiado")
            return

        self.write(
            {
                "cdc": cdc,
                "digito_verificador": cdc_cv,
                "nro_transaccion_set": "",
                "mensaje_set": "",
                "mensaje_set_detalle": "",
                "fecha_procesamiento_set": "",
                "validacion_esquema": "",
            }
        )

        # Generamos el XML y firmamos
        xml = self.factura_generar_xml(xmldict, fe_logger)
        self.firmar_de_xml(xml, xmldict, fe_logger)

        # Si se generan todos los datos y archivos necesarios, ahi se convierte en una FE valida
        self.write({"fe_valida": True, 'estado_set': 'pendiente'})

    def accion_servidor_regenerar_xml(self):
        """
        Se encarga de regenerar los XML de forma masiva
        """
        for rec in self:
            # Verificamos si es documento electronico y sus tipos
            if rec.es_documento_electronico() and rec.tipo_documento in ['out_invoice', 'out_refund', 'autofactura', 'nota_debito']:
                # Verificamos que el documento este en estado error_sifen, lote_rechazado  o rechazado
                if rec.estado_set not in ['pendiente', 'error_sifen', 'lote_rechazado', 'lote_reenviando', 'rechazado', 'borrador']:
                    msg = "Para generar el XML, los documentos deben estar en los estados: Error SIFEN, Lote Rechazado o Rechazado"
                    raise UserError(_(msg))

                # Regeneramos el XML del documento
                rec.preparar_documento_electronico()

    def enviar_documento_electronico(self):
        """
        Se encarga de generar de forma individual un lote y enviar a SIFEN
        con los metodos que se utilizan en el cron
        """
        print("Not implemented yet")

    def consultar_cdc_documento_electronico(self):
        for documento in self:
            # Creamos un logger del invoice
            de_logger = (
                self.env['fe.de_loggers']
                .sudo()
                .create(
                    {
                        "invoice": documento.id if documento.tipo_documento != 'nota_remision' else False,
                        "remision_id": documento.id if documento.tipo_documento == 'nota_remision' else False,
                        "accion": "consultar CDC",
                    }
                )
            )

            response = documento.consultar_cdc_individual(de_logger, documento.cdc)
            documento.procesar_consultar_cdc(response)

    # Implementar en modelo hijo
    def es_documento_electronico(self):
        raise NotImplementedError

    def obtener_timbrado_de(self, move_type=False):
        """
        Retorna el timbrado activo, asociado al diario del invoice
        """
        if move_type:
            tipo_documento = move_type
        else:
            # Se cambia por tipo de documento porque nota de debito tiene un valor propio
            tipo_documento = self.tipo_documento

        timbrado = self.journal_id.timbrados_ids.filtered(lambda x: x.active is True and x.tipo_documento == tipo_documento)

        if timbrado:
            if len(timbrado) > 1:
                raise exceptions.ValidationError('El diario solo debe tener un timbrado asociado para el tipo de documento')

            return timbrado
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido para el diario')

    def getdDesTiDE(self):
        if self.getiTiDE() == 1:
            return "Factura electrónica"
        elif self.getiTiDE() == 2:
            return "Factura electrónica de exportación"
        elif self.getiTiDE() == 3:
            return "Factura electrónica de importación"
        elif self.getiTiDE() == 4:
            return "Autofactura electrónica"
        elif self.getiTiDE() == 5:
            return "Nota de crédito electrónica"
        elif self.getiTiDE() == 6:
            return "Nota de débito electrónica"
        elif self.getiTiDE() == 7:
            return "Nota de remisión electrónica"
        elif self.getiTiDE() == 8:
            return "Comprobante de retención electrónico"

    def getdVerFor(self):
        """
        Retorna la version del formato guardado en el invoice o la version por defecto
        """
        if self.version_formato:
            return self.version_formato

        return self.env["ir.config_parameter"].sudo().get_param("fe_version_formato")

    def getdFecFirma(self):
        fecha = self.env["fe.de"].obtener_hora_actual_set()
        self.fecha_hora_firma = fecha
        # Retornamos la hora local
        fecha_local = self.env["fe.de"].obtener_fecha_hora_local(fecha)
        fecha_str = self.convertir_fecha(fecha_local)
        return fecha_str

    def getdInfoEmi(self):
        # Sobreescribir este método en caso de que se necesite información adicional
        return None

    def getdInfoFisc(self):
        # Sobreescribir este método en caso de que se necesite información adicional
        return None

    # Sobreescribir en caso de notas de remision
    def getgOpeDE(self):
        """
        Campos inherentes a la operación de Documentos Electrónicos (B001-B099)
        """
        # gOpeDE = {
        #     'iTipEmi': 1,  # Normal
        #     'dDesTipEmi': 'Normal',
        #     'dCodSeg': self.cod_seguridad,
        #     'dInfoEmi': self.getdInfoEmi(),
        #     # "dInfoFisc": "Información de interés del Fisco respecto al DE"
        #     # 'dInfoFisc': EN CASO DE QUE SEA UNA NOTA DE REMISIÓN
        # }

        # Sobreescribimos el diccionaro para que las keys sean opcionales
        gOpeDE = {}

        # Campos obligatorios
        gOpeDE['iTipEmi'] = 1
        gOpeDE['dDesTipEmi'] = 'Normal'
        gOpeDE['dCodSeg'] = self.cod_seguridad

        # Campos opcionales
        if self.getdInfoEmi():
            gOpeDE['dInfoEmi'] = self.getdInfoEmi()

        if self.getdInfoFisc():
            gOpeDE['dInfoFisc'] = self.getdInfoFisc()

        return gOpeDE

    # Implementar en modelo hijo
    def getdNumTim(self):
        raise NotImplementedError

    # Implementar en modelo hijo
    def getdSerieNum(self):
        raise NotImplementedError

    # Implementar en modelo hijo
    def getdFeIniT(self):
        raise NotImplementedError

    def getgTimb(self):
        """
        C. Campos de datos del Timbrado (C001-C099)
        """
        gTimb = {}
        gTimb['iTiDE'] = self.getiTiDE()
        gTimb['dDesTiDE'] = self.getdDesTiDE()
        gTimb['dNumTim'] = self.getdNumTim()
        gTimb['dEst'] = self.getdEst()
        gTimb['dPunExp'] = self.getdPunExp()
        gTimb['dNumDoc'] = self.getdNumDoc()
        if self.getdSerieNum():
            gTimb['dSerieNum'] = self.getdSerieNum()
        gTimb['dFeIniT'] = self.getdFeIniT()

        return gTimb

    # Implementar en modelo hijo
    def cItems(self):
        return NotImplementedError

    # Implementar en modelo hijo
    def getdTotGralOpe(self):
        raise NotImplementedError

    # Implementar en modelo hijo
    def getdTotIVA(self):
        raise NotImplementedError

    ### GRUPO EMISOR ###

    def getdRucEm(self):
        for this in self:
            ruc_emisor = str(this.company_id.ruc_contribuyente).split("-")
            dRucEm = ruc_emisor[0]
            return dRucEm

    def getdDVEmi(self):
        for this in self:
            ruc_emisor = str(this.company_id.ruc_contribuyente).split("-")
            dDVEmi = ruc_emisor[1]
            return dDVEmi

    def getiTipCont(self):
        for this in self:
            return this.company_id.tipo_contribuyente

    def getdFeEmiDE(self):
        # Se mantiene la compatibilidad con documentos generados anteriormente
        # Si existe dato en self.invoice_datetime, usamos ese campo
        if self.invoice_datetime:
            fecha = self.invoice_datetime
        else:
            # Caso contrario obtenemos las fechas de los campos correspondientes
            if self.tipo_documento == 'nota_remision':
                fecha = self.dFecEm
            else:
                fecha = self.invoice_date

        # Convertimos la fecha al timezone de Paraguay
        fecha_local = self.env["fe.de"].obtener_fecha_hora_local(fecha)
        fecha_local = self.convertir_fecha(fecha_local)

        return fecha_local

    def getcTipReg(self):
        if self.company_id.tipo_regimen:
            return int(self.company_id.tipo_regimen)
        else:
            raise exceptions.ValidationError('Debe definir el tipo de regimen en la compañia')

    def getdNomEmi(self):
        if self.company_id.nombre_contribuyente:
            return self.company_id.nombre_contribuyente[0:255]
        else:
            raise exceptions.ValidationError('Debe definir el nombre del contribuyente en la compañia')

    def getdNomFanEmi(self):
        if self.company_id.nombre_fantasia:
            return self.company_id.nombre_fantasia[0:255]

        return None

    def getdDirEmi(self):
        if self.company_id.partner_id.street:
            return self.company_id.partner_id.street[0:255]
        else:
            raise exceptions.ValidationError('Debe definir la dirección de la compañia')

    def getdNumCas(self):
        return 0

    def getdCompDir1(self):
        if self.company_id.partner_id.street2:
            return self.company_id.partner_id.street[0:255]
        else:
            return ""

    def getdCompDir2(self):
        if self.company_id.partner_id.street2:
            return self.company_id.partner_id.street[0:255]
        else:
            return ""

    def getcDepEmi(self):
        if self.company_id.state_id:
            return self.company_id.state_id.code
        else:
            raise exceptions.ValidationError('Debe definir el Departamento del contribuyente')

    def getdDesDepEmi(self):
        if self.company_id.state_id:
            return self.company_id.state_id.name
        else:
            raise exceptions.ValidationError('Debe definir el Departamento del contribuyente')

    def getcDisEmi(self):
        if self.company_id.city_id:
            return self.company_id.city_id.district_id.code
        else:
            raise exceptions.ValidationError('Debe definir la Ciudad y Distrito del contribuyente')

    def getdDesDisEmi(self):
        if self.company_id.city_id:
            return self.company_id.city_id.district_id.name
        else:
            raise exceptions.ValidationError('Debe definir la Ciudad y Distrito del contribuyente')

    def getcCiuEmi(self):
        if self.company_id.city_id:
            return self.company_id.city_id.code
        else:
            raise exceptions.ValidationError('Debe definir la Ciudad y Distrito del contribuyente')

    def getdDesCiuEmi(self):
        if self.company_id.city_id:
            return self.company_id.city_id.name
        else:
            raise exceptions.ValidationError('Debe definir la Ciudad y Distrito del contribuyente')

    def getdTelEmi(self):
        if self.company_id.phone:
            return self.company_id.phone
        else:
            raise exceptions.ValidationError('Debe definir el teléfono del contribuyente')

    def getdEmailE(self):
        if self.company_id.email:
            return self.company_id.email
        else:
            raise exceptions.ValidationError('Debe definir el email del contribuyente')

    def getdDenSuc(self):
        return self.company_id.sucursal if self.company_id.sucursal else ""

    def getcActEco(self):
        if self.company_id.cod_actividad_economica:
            return self.company_id.cod_actividad_economica
        else:
            raise exceptions.ValidationError('Debe definir el código de la actividad económica del contribuyente')

    def getdDesActEco(self):
        if self.company_id.des_actividad_economica:
            return self.company_id.des_actividad_economica
        else:
            raise exceptions.ValidationError('Debe definir la descripción de la actividad económica del contribuyente')

    def getActividadEconomica(self):
        actividades = []

        # Si el diario tiene actividades económicas, las agregamos de ahi
        if self.journal_id.actividad_economica_ids:
            for actividad in self.journal_id.actividad_economica_ids:
                actividades.append(
                    {
                        'cActEco': actividad.code,
                        'dDesActEco': actividad.name,
                    }
                )
        else:
            # Si no tiene, agregamos desde la compañia
            actividades.append(
                {
                    'cActEco': self.getcActEco(),
                    'dDesActEco': self.getdDesActEco(),
                }
            )

        return actividades

    def getiTipIDRespDE(self):
        return self.invoice_user_id.partner_id.tipo_documento if self.invoice_user_id.partner_id.tipo_documento else 9

    def getdDTipIDRespDE(self):
        tipo_documento = int(self.getiTipIDRespDE())
        if tipo_documento:
            if tipo_documento == 1:
                return "Cédula paraguaya"
            elif tipo_documento == 2:
                return "Pasaporte"
            elif tipo_documento == 3:
                return "Cédula extranjera"
            elif tipo_documento == 4:
                return "Carnet de residencia"
            else:
                return "Otro"

    def getdNumIDRespDE(self):
        return self.invoice_user_id.partner_id.nro_documento if self.invoice_user_id.partner_id.nro_documento else self.invoice_user_id.id

    def getdNomRespDE(self):
        return self.invoice_user_id.name

    def getdCarRespDE(self):
        return self.invoice_user_id.cargo if self.invoice_user_id.cargo else "Cajero"

    def getgEmis(self):
        """
        D2. Campos que identifican al emisor del Documento Electrónico DE (D100-D129)
        """
        gEmis = {
            'dRucEm': self.getdRucEm(),
            'dDVEmi': self.get_digito_verificador(cdc=self.getdRucEm()),
            'iTipCont': self.getiTipCont(),
            'cTipReg': self.getcTipReg(),
            'dNomEmi': self.getdNomEmi(),
            # 'dNomFanEmi': self.getdNomFanEmi(),
            'dDirEmi': self.getdDirEmi(),
            'dNumCas': self.getdNumCas(),
            # 'dCompDir1': self.getdCompDir1(),
            # 'dCompDir2': self.getdCompDir2(),
            'cDepEmi': self.getcDepEmi(),
            'dDesDepEmi': self.getdDesDepEmi(),
            'cDisEmi': self.getcDisEmi(),
            'dDesDisEmi': self.getdDesDisEmi(),
            'cCiuEmi': self.getcCiuEmi(),
            'dDesCiuEmi': self.getdDesCiuEmi(),
            'dTelEmi': self.getdTelEmi(),
            'dEmailE': self.getdEmailE(),
            # 'dDenSuc': self.getdDenSuc(),
            'gActEco': self.getActividadEconomica(),
            # 'gRespDE': {
            #     'iTipIDRespDE': self.getiTipIDRespDE(),
            #     'dDTipIDRespDE': self.getdDTipIDRespDE(),
            #     'dNumIDRespDE': self.getdNumIDRespDE(),
            #     'dNomRespDE': self.getdNomRespDE(),
            #     'dCarRespDE': self.getdCarRespDE(),
            # },
        }

        return gEmis

    ## FIN GRUPO EMISOR ###

    ## GRUPO RECEPTOR ###
    def getiNatRec(self):
        # Si es autofactura, debe ser contribuyente
        if self.tipo_documento == 'autofactura':
            return 1

        # Para otros tipos de documentos, depende del partner receptor
        if self.partner_id.contribuyente:
            return 1
        else:
            return 2

    def getdDesNatRec(self):
        if self.partner_id.contribuyente:
            return 'Contribuyente'
        else:
            return 'No contribuyente'

    def getiTiOpe(self):
        if self.tipo_operacion:
            return self.tipo_operacion
        else:
            raise exceptions.ValidationError('Debe definir el tipo de operación del documento electrónico')

    def getcPaisRec(self):
        # Si no tiene Pais retornamos por defecto PRY, porque la mayoría de los contribuyentes son de Paraguay
        if not self.partner_id.country_id:
            return "PRY"

        # Si es de Paraguay y no tiene código ISO-3166, retornamos PRY
        if self.partner_id.country_id.code == 'PY' and not self.partner_id.country_id.code_alpha3:
            return "PRY"

        # Si tiene código ISO-3166, retornamos el código. Caso contrario, error
        if self.partner_id.country_id.code_alpha3:
            return self.partner_id.country_id.code_alpha3
        else:
            raise exceptions.ValidationError('Debe definir el código ISO-3166 en la configuración de paises, dentro de contactos.')

    def getdDesPaisRe(self):
        country_id = self.partner_id.country_id

        # Si es autofactura, retorna del company
        if self.tipo_documento == 'autofactura':
            country_id = self.company_id.partner_id.country_id
            return country_id.name

        if country_id:
            return self.partner_id.country_id.name
        else:
            return "Paraguay"

    def getiTiContRec(self):
        company_type = self.partner_id.company_type

        # Si es autofactura, retorna del company
        if self.tipo_documento == 'autofactura':
            company_type = self.company_id.partner_id.company_type

        if company_type == 'person':
            return 1
        else:
            return 2

    def getdRucRec(self):
        for this in self:
            ruc = this.partner_id.vat

            # Si es autofactura, retorna del company
            if this.tipo_documento == 'autofactura':
                ruc = this.company_id.partner_id.vat

            ruc_clean = ruc.replace(".", "").replace(" ", "")
            ruc_clean = str(ruc_clean).split("-")
            dRucRec = ruc_clean[0]

            return dRucRec

    def getdDVRec(self):
        for this in self:
            ruc = this.partner_id.vat

            # Si es autofactura, retorna del company
            if this.tipo_documento == 'autofactura':
                ruc = this.company_id.partner_id.vat

            ruc_clean = ruc.replace(".", "").replace(" ", "")
            ruc_clean = str(ruc_clean).split("-")

            dDVEmi = False
            if len(ruc_clean) == 2:
                dDVEmi = ruc_clean[1]
            if not dDVEmi:
                dDVEmi = self.get_digito_verificador(ruc)

            return dDVEmi

    def getiTipIDRec(self):
        return self.partner_id.tipo_documento

    def getdDTipIDRec(self):
        if self.getiTipIDRec() == '1':
            return 'Cédula paraguaya'
        elif self.getiTipIDRec() == '2':
            return 'Pasaporte'
        elif self.getiTipIDRec() == '3':
            return 'Cédula extranjera'
        elif self.getiTipIDRec() == '4':
            return 'Carnet de Residencia'
        elif self.getiTipIDRec() == '5':
            return 'Innominado'
        elif self.getiTipIDRec() == '6':
            return 'Tarjeta diplomática de exoneración fiscal'

    def getdNumIDRec(self):
        return self.partner_id.nro_documento if self.partner_id.nro_documento else False

    def getdNomRec(self):
        # Si es autofactura, retorna del company
        if self.tipo_documento == 'autofactura':
            return self.company_id.partner_id.name

        return self.partner_id.name

    def getdNomFanRec(self):
        return self.partner_id.nombre_fantasia if self.partner_id.nombre_fantasia else ""

    def getdNumCasRec(self):
        return 0

    def getdDirRec(self):
        if self.partner_id.street:
            return self.partner_id.street[0:255]
        else:
            # raise exceptions.ValidationError('Debe definir la dirección del receptor')
            return "Asuncion"

    def getcDepRec(self):
        if self.partner_id.state_id:
            return self.partner_id.state_id.code
        else:
            return "1"
            # raise exceptions.ValidationError('Debe definir el Departamento del receptor')

    def getdDesDepRec(self):
        if self.partner_id.state_id:
            return self.partner_id.state_id.name
        else:
            # raise exceptions.ValidationError('Debe definir el Departamento del receptor')
            return "CAPITAL"

    def getcDisRec(self):
        if self.partner_id.city_id:
            return self.partner_id.city_id.district_id.code
        else:
            # raise exceptions.ValidationError('Debe definir la Ciudad y Distrito del receptor')
            return "1"

    def getdDesDisRec(self):
        if self.partner_id.city_id:
            return self.partner_id.city_id.district_id.name
        else:
            # raise exceptions.ValidationError('Debe definir la Ciudad y Distrito del receptor')
            return "ASUNCION (DISTRITO)"

    def getcCiuRec(self):
        if self.partner_id.city_id:
            return self.partner_id.city_id.code
        else:
            # raise exceptions.ValidationError('Debe definir la Ciudad y Distrito del receptor')
            return "1"

    def getdDesCiuRec(self):
        if self.partner_id.city_id:
            return self.partner_id.city_id.name
        else:
            # raise exceptions.ValidationError('Debe definir la Ciudad y Distrito del receptor')
            return "ASUNCION"

    def getdTelRec(self):
        """
        D214
        Número de teléfono del receptor (6-15 caracteres)
        Debe incluir el prefijo de la ciudad si D203 = PRY
        """
        phone = self.partner_id.phone

        # Si es autofactura, retorna del company
        if self.tipo_documento == 'autofactura':
            phone = self.company_id.partner_id.phone

        if phone:
            # Eliminamos los caracteres no numericos
            phone = re.sub('[^0-9]', '', phone)

            # Si el nro empieza con 0, lo convertimos a internacional
            if phone.startswith('0'):
                phone = f'+595{phone[1:]}'

            # Si el nro empieza con 9, lo convertimos a internacional
            if phone.startswith('9'):
                phone = f'+595{phone}'

            # Si el nro empieza con 5, agregamos un signo +
            if phone.startswith('5'):
                phone = f'+{phone}'

            # El nro debe tener entre 6 y 15 caracteres
            if len(phone) < 6 or len(phone) > 15:
                _logger.info("Formato incorrecto de teléfono %s. Ignorando telefono" % phone)
                return None

            return phone

        return None

    def getdCelRec(self):
        """
        D215
        Número de celular del receptor (10-20 length)
        """
        mobile = self.partner_id.mobile

        # Si es autofactura, retorna del company
        if self.tipo_documento == 'autofactura':
            mobile = self.company_id.partner_id.mobile

        if mobile:
            # Eliminamos los caracteres no numericos
            mobile = re.sub('[^0-9]', '', mobile)

            # Si el nro empieza con 0, lo convertimos a internacional
            if mobile.startswith('0'):
                mobile = f'+595{mobile[1:]}'

            # Si el nro empieza con 9, lo convertimos a internacional
            if mobile.startswith('9'):
                mobile = f'+595{mobile}'

            # Si el nro empieza con 5, agregamos un signo +
            if mobile.startswith('5'):
                mobile = f'+{mobile}'

            # El nro debe tener entre 10 y 20 caracteres
            if len(mobile) < 10 or len(mobile) > 20:
                _logger.info("Formato incorrecto de teléfono móvil %s. Ignorando móvil" % mobile)
                return None

            return mobile

        return None

    def getdEmailRec(self):
        email = self.partner_id.email

        # Si es autofactura, retorna del company
        if self.tipo_documento == 'autofactura':
            email = self.company_id.partner_id.email

        if email:
            regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
            if email and re.fullmatch(regex, email):
                return email
            else:
                _logger.info("Formato incorrecto de email %s. Ignorando email" % email)
                return None
        return None

    def getdCodCliente(self):
        partner_id = self.partner_id.id

        # Si es autofactura, retorna del company
        if self.tipo_documento == 'autofactura':
            partner_id = self.company_id.partner_id.id

        return str(partner_id).zfill(15)

    def getgDatRec(self):
        """
        D3. Campos que identifican al receptor del Documento Electrónico DE (D200-D299)
        """
        # Si el tipo de documento es autofactura, el receptor es el company
        if self.tipo_documento == 'autofactura':
            return self.getgDatRec_autofactura()

        gDatRec = {}

        # D201: Naturaleza del receptor
        gDatRec['iNatRec'] = self.getiNatRec()

        # D202: Tipo de operación
        gDatRec['iTiOpe'] = self.getiTiOpe()

        # D203: Código de país del receptor
        gDatRec['cPaisRec'] = self.getcPaisRec()

        # D204: Descripción del país del receptor
        gDatRec['dDesPaisRe'] = self.getdDesPaisRe()

        # Si el receptor es contribuyente
        if self.getiNatRec() == 1:
            # D205: Tipo de contribuyente (1: Física, 2: Jurídica)
            gDatRec['iTiContRec'] = self.getiTiContRec()
            # D206: RUC del receptor
            gDatRec['dRucRec'] = self.getdRucRec()
            # D207: Dígito verificador del RUC del receptor
            gDatRec['dDVRec'] = self.getdDVRec()
        else:
            # D208: Tipo de identificación del receptor
            gDatRec['iTipIDRec'] = self.getiTipIDRec()
            # D209: Descripción del tipo de identificación del receptor
            gDatRec['dDTipIDRec'] = self.getdDTipIDRec()
            # D210: Número de identificación del receptor
            gDatRec['dNumIDRec'] = self.getdNumIDRec()

        # D211: Nombre o Razón Social del receptor
        gDatRec['dNomRec'] = self.getdNomRec()
        
        # D212: Nombre Fantasía del receptor
        if self.getdNomFanRec():
            gDatRec['dNomFanRec'] = self.getdNomFanRec()

        if self.getdDirRec():
            # D213: Número de casa del receptor
            gDatRec['dDirRec'] = self.getdDirRec()
            
            # D218: Número de casa del receptor
            gDatRec['dNumCasRec'] = self.getdNumCasRec()

        # Enviar los datos de ubicación (departamento, distrito, ciudad) si se activa el parametro de sistema
        if self.env['ir.config_parameter'].sudo().get_param('fe_de.enviar_datos_ubicacion_receptor'):
            if self.tipo_operacion != '4':
                # D219: Codigo del departamento del receptor
                gDatRec['cDepRec'] = self.getcDepRec()
                # D220: Descripción del departamento del receptor
                gDatRec['dDesDepRec'] = self.getdDesDepRec()
                # D221: Codigo del distrito del receptor
                gDatRec['cDisRec'] = self.getcDisRec()
                # D222: Descripción del distrito del receptor
                gDatRec['dDesDisRec'] = self.getdDesDisRec()
                # D223: Codigo de la ciudad del receptor
                gDatRec['cCiuRec'] = self.getcCiuRec()
                # D224: Descripción de la ciudad del receptor
                gDatRec['dDesCiuRec'] = self.getdDesCiuRec()

        if self.getdTelRec():
            # D214: Teléfono del receptor
            gDatRec['dTelRec'] = self.getdTelRec()

        if self.getdCelRec():
            # D215: Celular del receptor
            gDatRec['dCelRec'] = self.getdCelRec()

        if self.getdEmailRec():
            # D216: Email del receptor
            gDatRec['dEmailRec'] = self.getdEmailRec()

        gDatRec['dCodCliente'] = self.getdCodCliente()

        return gDatRec

    def getgDatRec_autofactura(self):
        """
        D3. Campos que identifican al receptor del Documento Electrónico DE (D200-D299)
        """

        gDatRec = {}

        gDatRec['iNatRec'] = self.getiNatRec()
        gDatRec['iTiOpe'] = self.getiTiOpe()
        gDatRec['cPaisRec'] = self.getcPaisRec()
        gDatRec['dDesPaisRe'] = self.getdDesPaisRe()
        # INFORMAR SOLO SI EL CLIENTE ES CONTRIBUYENTE
        if self.getiNatRec() == 1:
            gDatRec['iTiContRec'] = self.getiTiContRec()
            gDatRec['dRucRec'] = self.getdRucRec()
            gDatRec['dDVRec'] = self.getdDVRec()
        else:
            gDatRec['iTipIDRec'] = self.getiTipIDRec()
            gDatRec['dDTipIDRec'] = self.getdDTipIDRec()
            gDatRec['dNumIDRec'] = self.getdNumIDRec()
        gDatRec['dNomRec'] = self.getdNomRec()
        if self.getdCelRec():
            gDatRec['dCelRec'] = self.getdCelRec()
        if self.getdEmailRec():
            gDatRec['dEmailRec'] = self.getdEmailRec()
        gDatRec['dCodCliente'] = self.getdCodCliente()

        return gDatRec

    ## FIN GRUPO RECEPTOR ###

    def getgDtipDE(self):
        """
        Según el tipo de documento, se llama al metodo especifico para generar el grupo de datos
        """

        if self.tipo_documento == "out_invoice":
            return self.getgDtipDE_factura()

        elif self.tipo_documento in ["out_refund", "nota_debito"]:
            return self.getgDtipDE_nota_credito()

        elif self.tipo_documento in ["autofactura"]:
            return self.getgDtipDE_autofactura()

    def get_lineas_facturables(self):
        """
        Obtenemos las lineas facturables
        - Lineas con valor 0 o superior que no sean descuentos ni anticipos
        """

        lines = self.invoice_line_ids.filtered(lambda line: line.display_type == 'product' and line.price_total >= 0)
        return lines

    def get_lineas_anticipo(self):
        """
        Obtenemos las lineas facturables
        - Lineas con valor 0 o superior que no sean descuentos ni anticipos
        """

        # TODO: De esta forma se puede implementar cuando al asociar una factura de anticipo ya genere la linea de downpayment
        # lines = self.invoice_line_ids.filtered(lambda line: line.display_type == 'product' and line.is_downpayment)
        # return lines

        # Solucion temporal para que funcione
        lines = self.invoice_line_ids.filtered(
            lambda line: line.display_type == 'product' and line.price_total < 0 and line.move_id.facturas_anticipo_asociadas
        )
        return lines

    def get_lineas_descuentos_globales(self):
        """
        Obtenemos las lineas que son del tipo producto, no son anticipo y tienen valores negativos
        """

        # TODO: De esta forma se puede implementar cuando al asociar una factura de anticipo ya genere la linea de downpayment
        # lines = self.invoice_line_ids.filtered(lambda line: line.display_type == 'product' and not line.is_downpayment and line.price_total < 0)
        # return lines

        # Solucion temporal para que funcione
        lines = self.invoice_line_ids.filtered(
            lambda line: line.display_type == 'product' and line.price_total < 0 and not line.move_id.facturas_anticipo_asociadas
        )
        return lines

    def get_amount_total(self):
        """
        A SIFEN se envia los montos linea por linea y con decimales
        Entonces debemos calcular el monto total sumando linea por linea porque odoo redondea el price_total y por ende amount_total sale diferente
        """
        lines = self.get_lineas_facturables()
        total = 0
        for i in lines:
            total = total + i.getdTotOpeItem()

        # Limitamos los decimales a 8
        total = round(total, 8)
        return total
