import base64
import hashlib
import logging
import random
import re
import socket
import struct
import traceback
import zipfile
from collections import OrderedDict
import datetime
from io import BytesIO
from socket import AF_INET, SOCK_DGRAM
import pytz
import qrcode
import signxml
import xmlschema
from lxml import etree as lxml_ET
from odoo import _, exceptions, models, release, fields
from signxml import XMLSigner, XMLVerifier

_logger = logging.getLogger(__name__)


class DocumentoElectronicoTools(models.AbstractModel):
    _inherit = 'fe.de'
    _description = 'Metodos comunes que se utilizan en los documentos electronicos'

    def verificar_nro_factura(self, tipo_documento):
        # Verificamos que la factura tenga formato (xxx-xxx-xxxxxxx)
        patron = re.compile(r'((^\d{3})[-](\d{3})[-](\d{7}$)){1}')
        if self.name and patron.match(self.name):
            nro_establecimiento = self.name.split('-')[0]
            nro_pto_expedicion = self.name.split('-')[1]
            nro_factura = int(self.name.split('-')[-1])

            # Verificamos si el nro de factura está dentro del rango inutilizado
            domain = [
                ('establecimiento', '=', nro_establecimiento),
                ('punto_expedicion', '=', nro_pto_expedicion),
                ('fact_inicio', '<=', nro_factura),
                ('fact_fin', '>=', nro_factura),
                ('status', '=', 'aprobado'),
                ('tipo_documento_electronico', '=', tipo_documento),
            ]
            rango = self.env['fe.inutilizar_rango'].search(domain)

            if rango:
                nro_fact_nuevo = str(int(rango.fact_fin) + 1).zfill(7)
                self.name = f"{nro_establecimiento}-{nro_pto_expedicion}-{nro_fact_nuevo}"
                # TODO: Ver si es necesario dejar algun mensaje del motivo del cambio

    def validar_documento_electronico(self):
        """
        Se valida que todos los campos necesarios para generar la factura electronica esten completos
        """

        # 1 - Validamos el RUC del cliente
        self.partner_id.validar_ruc_sifen()

        # 2 - Verificamos que se hayan completado los campos relacionados a FE
        if self.tipo_documento in ['out_invoice', 'autofactura']:
            if not self.iTipTra or not self.iTImp or not self.indicador_presencia:
                raise exceptions.ValidationError(_('Debe completar todos los campos relacionados a Factura Electronica'))

        # 3 - Para autofactura, verificar que el partner tenga CI cargado
        if self.tipo_documento in ['autofactura']:
            if not self.partner_id.nro_documento:
                raise exceptions.ValidationError(_('El proveedor debe tener cargado el número de documento'))

            # Verificamos que las lineas de factura todos sean exentos
            for line in self.get_lineas_facturables():
                if line.tax_ids.amount != 0:
                    raise exceptions.ValidationError(_('Todas las líneas de la factura debe ser exento'))

        # Agregar mas validaciones del manual
        # D3. Datos que identifican al receptor del Documento Electrónico DE (D200 - D299)

    def get_nombre_archivo(self, detalle, extension):
        """
        Retornamos el nombre del archivo para guardar:
        Ej.: nro_factura + cdc + detalle
        001-001-000001_12344564545433_firmado.xml
        """

        nro_factura = self.name
        cdc = self.cdc

        if detalle:
            name = f"{nro_factura}_{cdc}_{detalle}.{extension}"
        else:
            name = f"{nro_factura}_{cdc}.{extension}"

        return name

    def obtener_cotizacion(self):
        """
        Se utiliza el metodo _convert de odoo para obtener la cotizacion mas cercana
        a la fecha. Pasandole como parametro la fecha de la factura y una unidad de la
        moneda a convertir.
        """
        # Obtenemos la primera linea de la factura
        lineas = self.get_lineas_facturables()
        if not lineas:
            return 1

        line = lineas[0]

        # Obtenemos la moneda PYG
        currency_pyg = self.env.ref('base.PYG')

        # Verificamos si la moneda base de la compañia es PYG
        is_company_currency_pyg = self.env.company.currency_id == currency_pyg

        # Si la linea tiene amount_currency, retornamos el valor. Caso contrario obtenemos de currency
        if is_company_currency_pyg and line.amount_currency:
            tipo_cambio = abs(line.balance) / abs(line.amount_currency)
            return round(tipo_cambio, 2)

        # Obtenemos la fecha de la factura, para obtener la cotizacion mas cercana
        date = self.invoice_date
        cotizacion = self.currency_id._convert(1, currency_pyg, self.env.company, date)
        return round(cotizacion, 2)

    def obtener_fecha_hora_utc(self, date):
        """
        Convertimos la fecha y hora local a UTC
        """
        tz = pytz.timezone("America/Asuncion")
        utc_date = tz.localize(date).astimezone(pytz.utc)
        return utc_date

    def obtener_fecha_hora_local(self, date):
        """
        Convierte la fecha y hora UTC a local
        """
        tz = pytz.timezone("America/Asuncion")
        user_time = pytz.utc.localize(date).astimezone(tz)

        return user_time

    def convertir_fecha(self, date, odoo_format=False):
        """
        Recibe fecha en formato objeto y retorna en formato string

        Si el formato requerido es ODOO, retornamos:
        %Y-%m-%d %H:%M:%S

        Si el formato requerido es SET, retornamos:
        %Y-%m-%dT%H:%M:%S

        Notar la dichosa T en el medio
        """

        if not date:
            return ""

        # Si la fecha es del tipo string, convertimos a objeto
        if isinstance(date, str):
            try:
                date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                # convertimos ±HH:MM a ±HHMM
                date = date[:-3] + date[-2:]
                date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")

        if odoo_format:
            date = date.replace(tzinfo=None)
            date_utc = self.obtener_fecha_hora_utc(date)
            date_utc = date_utc.replace(tzinfo=None)
            return date_utc
        else:
            date_str = date.strftime("%Y-%m-%dT%H:%M:%S")

        return date_str

    def obtener_hora_actual_set(self):
        """
        Obtiene la hora actual del servidor de la SET, convertido en UTC
        Se retorna la fecha/hora en UTC 0 para mejor manejo de las conversiones
        """
        try:
            port = 123
            buf = 1024
            address = ("aravo1.set.gov.py", port)
            msg = '\x1b' + 47 * '\0'

            # reference time (in seconds since 1900-01-01 00:00:00)
            TIME1970 = 2208988800  # 1970-01-01 00:00:00

            # connect to server
            client = socket.socket(AF_INET, SOCK_DGRAM)
            client.sendto(msg.encode('utf-8'), address)
            msg, address = client.recvfrom(buf)

            t = struct.unpack("!12I", msg)[10]

            t -= TIME1970

            # Obtenemos la fecha/hora en UTC
            fecha = datetime.datetime.fromtimestamp(t, datetime.timezone.utc)
            fecha = fecha.replace(tzinfo=None)

            return fecha
        except Exception as e:
            self.log_errors(e, "hora_actual_set", False)
            fecha = fields.Datetime.now()
            fecha = fecha.replace(tzinfo=None)
            return fecha

    def get_digito_verificador(self, cdc):
        """
        Obtiene el digito verificador del CDC
        """
        ruc_asd = str(cdc).replace(".", "").replace(" ", "")
        ruc_asd = ruc_asd.split("-")
        ruc_ci = ruc_asd[0]
        ruc_str = str(ruc_ci)[::-1]
        v_total = 0
        basemax = 11
        k = 2
        for i in range(0, len(ruc_str)):
            if k > basemax:
                k = 2
            v_total += int(ruc_str[i]) * k
            k += 1
            resto = v_total % basemax
        if resto > 1:
            return basemax - resto
        else:
            return 0

    def get_cod_seguridad(self):
        """
        Generar un código de seguridad aleatorio de 9 digitos que no se puede repetir.
        En caso de no tener 0 digitos, completar con ceros.
        """
        cod = random.randint(1, 999999999)
        codigo_seguridad = str(cod).zfill(9)
        return codigo_seguridad

    def generate_qr_code_fe(self):
        """
        Genera el codigo QR de la factura
        """
        for i in self:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(i.dcarQR)
            qr.make(fit=True)
            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())
            i.fe_qr_code = qr_image

    def generar_CarQR(self, digest, xmldict):
        """
        Genera el link del codigo QR de la factura
        """
        idCSC, CSC, url_set = self.obtener_datos_CSC()

        qpd = OrderedDict()
        gdatgralope = xmldict['rDE']['DE']['gDatGralOpe']
        if self.tipo_documento == 'nota_remision':
            gtotsub = 0
        else:
            gtotsub = xmldict['rDE']['DE']['gTotSub']

        qpd['nVersion'] = self.version_formato
        qpd['Id'] = self.cdc
        qpd['dFeEmiDE'] = gdatgralope['dFeEmiDE'].encode('utf-8').hex()

        # 1 = Contribuyente
        if xmldict["rDE"]["DE"]["gDatGralOpe"]["gDatRec"]["iNatRec"] == 1:
            qpd['dRucRec'] = str(gdatgralope['gDatRec']['dRucRec'])

        # 2 = No Contribuyente
        if xmldict["rDE"]["DE"]["gDatGralOpe"]["gDatRec"]["iNatRec"] == 2:
            if not gdatgralope.get('gDatRec').get('dNumIDRec'):
                qpd['dNumIDRec'] = '0'
            else:
                qpd['dNumIDRec'] = str(gdatgralope['gDatRec']['dNumIDRec'])

        if self.tipo_documento == 'nota_remision':
            qpd['dTotGralOpe'] = str(0)
            qpd['dTotIVA'] = str(0)
        else:
            qpd['dTotGralOpe'] = str(gtotsub['dTotGralOpe'])

            if self.tipo_documento == "autofactura":
                qpd['dTotIVA'] = str(0)
            else:
                qpd['dTotIVA'] = str(gtotsub['dTotIVA'])

        qpd['cItems'] = str(self.cItems())
        qpd['DigestValue'] = digest.encode('utf-8').hex()
        qpd['IdCSC'] = idCSC

        qpar = '&'.join(list(map(lambda x: '='.join(x), qpd.items())))
        qparsec = qpar + CSC
        qpar = qpar + '&' + 'cHashQR={}'.format(hashlib.sha256(qparsec.encode('utf-8')).hexdigest())
        qpar = f"{url_set}{qpar}".strip()

        return {'qpar': qpar}

    def obtener_datos_CSC(self):
        """
        Obtiene los datos del idCSC y CSC
        """

        url_set = None

        # TODO: Acá se puede comprobar que el ambiente donde se está probando realmente corresponde a un ambiente de test o producción

        # OBtenemos la URL del QR
        ambiente = self.env.company.fe_ambiente
        if ambiente:
            url_set = self.env['ir.config_parameter'].sudo().get_param(f"fe_qrlink_{ambiente}")
        else:
            raise exceptions.ValidationError(_("No se configuró la url del qr para el ambiente de facturación"))

        # Obtenemos el idcsc y csc
        if self.tipo_documento == 'nota_remision':
            timbrado = self.obtener_timbrado_de(move_type='nota_remision')
        else:
            timbrado = self.obtener_timbrado_de()

        if timbrado:
            if not timbrado.idcsc:
                raise exceptions.ValidationError('Debe definir un idcsc válido en el timbrado')
            if not timbrado.csc:
                raise exceptions.ValidationError('Debe definir un csc válido en el timbrado')

            idcsc = timbrado.idcsc.zfill(4)
            csc = timbrado.csc

            return (idcsc, csc, url_set)
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido')

    def firmar_de_xml(self, xml, xmljson, de_logger):
        """
        Se firma el XML y se agrega el dCarQR
        """
        try:
            cert, key = [open(f, "rb").read() for f in (self.env.company.cert, self.env.company.private_key)]

            # Se prepara para firmar
            signer = XMLSigner(c14n_algorithm='http://www.w3.org/2001/10/xml-exc-c14n#')
            signer.namespaces = {None: signxml.namespaces.ds}
            signed_root = signer.sign(xml, cert=cert, key=key, reference_uri=self.cdc)

            gcamfufd = lxml_ET.Element('gCamFuFD')

            # Generamos el dCarQR y lo agregamos al xml
            digest = signed_root.getchildren()[2].getchildren()[0].getchildren()[-1].getchildren()[-1].text
            qpar = self.generar_CarQR(digest, xmljson)
            dcar_link = qpar.get('qpar').encode('utf-8')

            # Agregamos el nodo de dCarQR al XML
            dcarqr = lxml_ET.SubElement(gcamfufd, 'dCarQR')
            dcarqr.text = dcar_link

            # Agregamos la información adicional
            if self.info_adicional:
                dInfAdic = lxml_ET.SubElement(gcamfufd, 'dInfAdic')
                dInfAdic.text = self.info_adicional

            # Agregamos al XML el nuevo grupo
            signed_root.append(gcamfufd)

            # Verificamos la firma
            XMLVerifier().verify(signed_root, x509_cert=cert)

            # Validar Schema
            if self.env.company.fe_validar_schema:
                self.validar_schema(signed_root)

            # Guardamos en la BD
            filename = self.get_nombre_archivo("firmado", "xml")
            data_b64 = base64.b64encode(self.to_string_xml(signed_root))
            de_logger.sudo().write({'xml_firmado': data_b64, 'xml_firmado_name': filename})

            name = f"{self.name}.xml"
            self.write({'xml_file': data_b64, 'xml_file_name': name, 'dcarQR': dcar_link})

            return signed_root
        except Exception as ex:
            self.log_errors(ex, "firmar_de_xml", False)

    def firmar_xml_evento(self, xml, identificador, de_logger):
        """
        Se firma el XML y se agrega el dCarQR
        """
        try:
            cert, key = [open(f, "rb").read() for f in (self.env.company.cert, self.env.company.private_key)]

            signer = XMLSigner(c14n_algorithm='http://www.w3.org/2001/10/xml-exc-c14n#')
            signer.namespaces = {None: signxml.namespaces.ds}
            signed_root = signer.sign(xml, reference_uri=identificador, key=key, cert=cert)

            verified_data = XMLVerifier().verify(signed_root, x509_cert=cert).signed_xml
            signature = signed_root.getchildren()[-1]

            return signature
        except Exception as ex:
            self.log_errors(ex, "firmar_xml_evento", False)

    def validar_schema(self, xml):
        try:
            DE_v150 = xmlschema.XMLSchema('https://ekuatia.set.gov.py/sifen/xsd/siRecepDE_v150.xsd')
            prueba = DE_v150.validate(xml)
            print(prueba)
        except Exception as e:
            _logger.error("Validacion de esquema")
            _logger.error(e)
            self.validacion_esquema = e.message

    def zip_file(self, invoices):
        try:
            zip_content = None
            zip_data = BytesIO()

            # Creamos una estructura XML para agregar todos los XML
            nodo_raiz = lxml_ET.Element('rLoteDE', xmlns="http://ekuatia.set.gov.py/sifen/xsd")

            # Creamos todos los XML dentro de un archivo
            for invoice in invoices:
                # Obtenemos de la BD, convertimos a XML y agregamos a la raiz
                if invoice.xml_file:
                    xml_str = base64.b64decode(invoice.xml_file).decode("utf-8")
                    xml = lxml_ET.fromstring(xml_str)
                    nodo_raiz.append(xml)

            # Archivo SOAP a ser enviado
            soap_structure = self.clean_up_string(self.to_string_xml(nodo_raiz, xml_declaration=True))

            # Guardamos en un archivo zip
            with zipfile.ZipFile(zip_data, 'w', zipfile.ZIP_DEFLATED) as zip:
                zip.writestr("facturas.xml", soap_structure)

            zip_content = zip_data.getvalue()

            # Retornamos en formato base64 bytes
            zip_base64 = base64.b64encode(zip_content)

            return zip_base64

        except Exception as ex:
            self.log_errors(ex, "zip_file", False)

    def to_string_xml(self, node, pretty_print=False, xml_declaration=False):
        return lxml_ET.tostring(node, pretty_print=pretty_print, encoding='UTF-8', xml_declaration=xml_declaration)

    def clean_up_string(self, sele):
        sele = b''.join(sele.split(b'\r\n'))
        sele = b''.join(sele.split(b'\n'))
        sele = b''.join(sele.split(b'\t'))
        sele = b''.join(sele.split(b'    '))
        sele = b''.join(sele.split(b'>    <'))
        sele = b''.join(sele.split(b'>  <'))
        sele = re.sub(b'\r?\n|\r', b'', sele)
        return sele

    def separar_cdc(self, cdc):
        """
        En la representación gráfica (KuDE) deberá ser visible, por lo tanto, debe ser expuesto en grupos de cuatro caracteres, tal como sigue:
        Separamos codigo CDC en grupos de 4 digitos
        """
        if not cdc:
            return ""

        cdc = str(cdc)
        grupos = [cdc[i: i + 4] for i in range(0, len(cdc), 4)]
        grupos = ' '.join(grupos)
        return grupos

    def log_errors(self, ex, method, raise_exception=True, msg=None):
        """
        Metodo para manejar los errores que vienen por un raise Exception
        Args:
            ex (exceptions): Contiene el error del raise Exception
            method (str): Nombre del metodo donde se produjo el error
            raise_exception (bool): Si es True realiza un raise con el error del raise Exception
        Raises:
            exceptions.ValidationError: Realiza un raise con el error del raise Exception
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        _logger.error(f"=============== {method} ==============")
        _logger.error(timestamp)
        _logger.error(ex)
        err = traceback.format_exc()
        _logger.error(err)
        _logger.error(f"=============== FIN: {method} ==============")

        _msg = f"Error en el método {method}. Favor consultar con un administrador."
        if not msg:
            msg = ex.args[0] if ex and ex.args else _msg

        # Guardamos el error para debug
        _error = self.error_generacion or ""
        error = _error + f"{timestamp}\n{msg};\n\n"
        self.write({'error_generacion': error})

        # No todos los errores deben romper el proceso
        if raise_exception:
            raise exceptions.ValidationError(_(msg))

    def send_email_de(self):
        try:
            for de in self:
                # Envio de mail testeado en version 15 y 16
                odoo_version = release.version_info[0]
                if odoo_version not in [14, 15, 16]:
                    return

                # Si no esta activo el envio de mail no se envia, pero se establece como enviado (para control en el ambiente de test)
                if not self.env.company.fe_send_email:
                    de.documento_enviado_mail = True
                    return

                regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
                # childs = list(de.partner_id.child_ids.filtered(lambda x: x.recibe_de))
                # partners = [de.partner_id]
                # if childs:
                #     partners = partners + childs
                # for partner in partners:
                #     if not re.search(regex, partner.email):
                #         partners.remove(partner)

                message_partner_ids = de.partner_id
                message_partner_ids += message_partner_ids.child_ids
                message_partner_ids = message_partner_ids.filtered(lambda x: x.recibe_de and x.email and re.fullmatch(regex, x.email))

                if message_partner_ids:
                    body = """
                    <html>
                        <strong>%s.</strong>
                        <br/>
                        <br/>
                        <span> Adjuntamos su Documento electrónico Nro: %s</span>
                        <br/>
                        <span>Atentamente.</span>
                        <br/>
                        <br/>
                    </html>
                    """ % (
                        de.partner_id.name,
                        de.name,
                    )

                    subject = "Documento electrónico %s" % de.name

                    # Obtenemos el reporte (PDF) para los diferentes tipos de documentos y versiones de odoo
                    generated_report = None
                    if de.tipo_documento != 'nota_remision':
                        if odoo_version in [14, 15]:
                            generated_report = self.env.ref('facturacion_electronica_py.factura_report_action')._render_qweb_pdf(de.id)[0]
                        elif odoo_version == 16:
                            generated_report = (
                                self.env['ir.actions.report']
                                .sudo()
                                .with_context(force_report_rendering=True)
                                ._render_qweb_pdf('facturacion_electronica_py.facturas_template', res_ids=de.id)[0]
                            )
                    else:
                        if odoo_version in [14, 15]:
                            generated_report = self.env.ref('facturacion_electronica_py.remision_report_action')._render_qweb_pdf(de.id)[0]
                        elif odoo_version == 16:
                            generated_report = (
                                self.env['ir.actions.report']
                                .sudo()
                                .with_context(force_report_rendering=True)
                                ._render_qweb_pdf('facturacion_electronica_py.kude_remision_template', res_ids=de.id)[0]
                            )

                    if not generated_report:
                        return

                    # Agregamos como adjunto el pdf y el xml del documento
                    attachments = [
                        (de.xml_file_name, base64.b64decode(de.xml_file)),
                        (de.xml_file_name.replace('.xml', ('.pdf')), generated_report),
                    ]

                    # TODO: Para multicompañia ver si se puede seleccionar el mail de la compañia
                    de.message_post(body=body, subject=subject, message_type='email', attachments=attachments, partner_ids=message_partner_ids.ids)

                    # Actualizamos el estado del documento
                    de.documento_enviado_mail = True
        except Exception as e:
            print(e)
            self.log_errors(e, "send_email_de", False)
