from odoo import _, api, fields, models, exceptions
import base64, json, re


class AccountPayment(models.Model):
    _inherit = "account.payment"

    ret_fecha_creacion = fields.Date(string="Fecha de creación")
    ret_fecha_hora_creacion = fields.Datetime(string="Fecha/hora de creación")
    ret_situacion = fields.Selection(
        string="Situación",
        selection=[("CONTRIBUYENTE", "CONTRIBUYENTE"), ("NO_CONTRIBUYENTE", "NO_CONTRIBUYENTE"), ("NO_RESIDENTE", "NO_RESIDENTE")],
    )
    ret_ruc = fields.Char(string="RUC")
    ret_dv = fields.Char(string="DV")
    ret_tipo_identificacion = fields.Selection(
        string="Tipo identificación",
        selection=[
            ("CEDULA", "CEDULA"),
            ("CARNE_RESIDENCIA", "CARNE_RESIDENCIA"),
            ("PASAPORTE", "PASAPORTE"),
            ("IDENTIFICACION_TRIBUTARIA", "IDENTIFICACION_TRIBUTARIA"),
            ("INNOMINADO_COOPERATIVA", "INNOMINADO_COOPERATIVA"),
            ("INNOMINADOS_JUEGOS_DE_AZAR", "INNOMINADOS_JUEGOS_DE_AZAR"),
        ],
    )
    ret_identificacion = fields.Char(string="Identificación")
    ret_nombre = fields.Char(string="Nombre")
    ret_domicilio = fields.Char("Domicilio")
    ret_direccion = fields.Char("Dirección")
    ret_correo_electronico = fields.Char(string="Correo electrónico")
    ret_pais = fields.Many2one("res.country", string="País")
    ret_telefono = fields.Char(string="Teléfono")
    ret_tiene_representante = fields.Boolean(string="Tiene representante legal")
    ret_tipo_ident_representante = fields.Selection(
        string="Tipo de identificación del representante",
        selection=[
            ("RUC", "RUC"),
            ("CEDULA DE IDENTIDAD", "CEDULA DE IDENTIDAD"),
            ("PASAPORTE", "PASAPORTE"),
            ("IDENTIFICACION_TRIBUTARIA", "IDENTIFICACION_TRIBUTARIA"),
        ],
    )
    ret_identificacion_representante = fields.Char(string="Identificación del representante")
    ret_nombre_representante = fields.Char(string="Nombre del representante")
    ret_tiene_beneficiario = fields.Boolean(string="Tiene beneficiario", default=False)
    ret_tipo_ident_beneficiario = fields.Selection(
        string="Tipo de identificación del beneficiario",
        selection=[
            ("RUC", "RUC"),
            ("CEDULA DE IDENTIDAD", "CEDULA DE IDENTIDAD"),
            ("PASAPORTE", "PASAPORTE"),
            ("IDENTIFICACION_TRIBUTARIA", "IDENTIFICACION_TRIBUTARIA"),
        ],
    )
    ret_identificacion_beneficiario = fields.Char(string="Identificación del beneficiario")
    ret_nombre_beneficiario = fields.Char(string="Nombre del beneficiario")
    ret_condicion_compra = fields.Selection(string="Condición de compra", selection=[("CONTADO", "CONTADO"), ("CREDITO", "CREDITO")])
    ret_cuotas = fields.Integer(string="Cuotas")
    ret_tipo_comprobante = fields.Selection(
        string="Tipo de comprobante",
        selection=[
            ("1", "Factura"),
            ("5", "Auto facturas"),
            ("11", "Entrada a espectáculos públicos"),
            ("17", "Escritura Pública"),
            ("18", "Otros"),
            ("19", "Planilla de pagos"),
            ("20", "Liquidación de salarios"),
        ],
    )
    ret_nro_comprobante = fields.Char(string="Nro. de comprobante")
    ret_fecha_comprobante = fields.Date(string="Fecha del comprobante")
    ret_nro_timbrado = fields.Char(string="Nro. de timbrado")
    ret_fecha = fields.Date(string="Fecha")
    ret_moneda = fields.Many2one("res.currency", string="Moneda de la retención")
    ret_tipo_cambio = fields.Integer(string="Tipo de cambio")
    ret_retencion_renta = fields.Boolean(string="Retención de renta", default=False)
    ret_concepto_renta = fields.Selection(
        string="Concepto renta",
        selection=[
            ("COMERCIAL_INDUSTRIAL_SERVICIO_REGISTRADO.1", "COMERCIAL_INDUSTRIAL_SERVICIO_REGISTRADO.1"),
            ("AGROPECUARIAS_REGISTRADO.1", "AGROPECUARIAS_REGISTRADO.1"),
            ("RENTA_EMPRESARIAL_REGISTRADO.1", "RENTA_EMPRESARIAL_REGISTRADO.1"),
            ("IMPUESTO_RENTA_PERSONAL_REGISTRADO.1", "IMPUESTO_RENTA_PERSONAL_REGISTRADO.1"),
            ("IMPUESTO_RENTA_PERSONAL.1", "IMPUESTO_RENTA_PERSONAL.1"),
            ("IMPUESTO_RENTA_PERSONAL.2", "IMPUESTO_RENTA_PERSONAL.2"),
            ("IMPUESTO_RENTA_PERSONAL.3", "IMPUESTO_RENTA_PERSONAL.3"),
            ("IMPUESTO_RENTA_PERSONAL.4", "IMPUESTO_RENTA_PERSONAL.4"),
            ("IMPUESTO_RENTA_PERSONAL.5", "IMPUESTO_RENTA_PERSONAL.5"),
            ("IMPUESTO_RENTA_PERSONAL.6", "IMPUESTO_RENTA_PERSONAL.6"),
            ("IMPUESTO_RENTA_PERSONAL.7", "IMPUESTO_RENTA_PERSONAL.7"),
            ("COMERCIAL_INDUSTRIAL_SERVICIOS.1", "COMERCIAL_INDUSTRIAL_SERVICIOS.1"),
            ("COMERCIAL_INDUSTRIAL_SERVICIOS.2", "COMERCIAL_INDUSTRIAL_SERVICIOS.2"),
            ("COMERCIAL_INDUSTRIAL_SERVICIOS.3", "COMERCIAL_INDUSTRIAL_SERVICIOS.3"),
            ("COMERCIAL_INDUSTRIAL_SERVICIOS.4", "COMERCIAL_INDUSTRIAL_SERVICIOS.4"),
            ("COMERCIAL_INDUSTRIAL_SERVICIOS.5", "COMERCIAL_INDUSTRIAL_SERVICIOS.5"),
            ("COMERCIAL_INDUSTRIAL_SERVICIOS.6", "COMERCIAL_INDUSTRIAL_SERVICIOS.6"),
            ("RENTA_EMPRESARIAL.1", "RENTA_EMPRESARIAL.1"),
            ("RENTA_EMPRESARIAL.2", "RENTA_EMPRESARIAL.2"),
            ("SERVICIO_PERSONAL.1", "SERVICIO_PERSONAL.1"),
            ("RENTA_NO_RESIDENTE.1", "RENTA_NO_RESIDENTE.1"),
            ("RENTA_NO_RESIDENTE.2", "RENTA_NO_RESIDENTE.2"),
            ("RENTA_NO_RESIDENTE.3", "RENTA_NO_RESIDENTE.3"),
            ("RENTA_NO_RESIDENTE.4", "RENTA_NO_RESIDENTE.4"),
            ("RENTA_NO_RESIDENTE.5", "RENTA_NO_RESIDENTE.5"),
            ("RENTA_NO_RESIDENTE.6", "RENTA_NO_RESIDENTE.6"),
            ("RENTA_NO_RESIDENTE.7", "RENTA_NO_RESIDENTE.7"),
            ("RENTA_NO_RESIDENTE.8", "RENTA_NO_RESIDENTE.8"),
            ("RENTA_NO_RESIDENTE.9", "RENTA_NO_RESIDENTE.9"),
            ("RENTA_NO_RESIDENTE.10", "RENTA_NO_RESIDENTE.10"),
            ("RENTA_NO_RESIDENTE.11", "RENTA_NO_RESIDENTE.11"),
            ("RENTA_NO_RESIDENTE.12", "RENTA_NO_RESIDENTE.12"),
            ("RENTA_NO_RESIDENTE.13", "RENTA_NO_RESIDENTE.13"),
            ("RENTA_NO_RESIDENTE.14", "RENTA_NO_RESIDENTE.14"),
            ("RENTA_NO_RESIDENTE.15", "RENTA_NO_RESIDENTE.15"),
            ("RENTA_NO_RESIDENTE.16", "RENTA_NO_RESIDENTE.16"),
            ("RENTA_NO_RESIDENTE_EXONERADO.1", "RENTA_NO_RESIDENTE_EXONERADO.1"),
            ("RENTA_NO_RESIDENTE_EXONERADO.2", "RENTA_NO_RESIDENTE_EXONERADO.2"),
            ("RENTA_NO_RESIDENTE_EXONERADO.3", "RENTA_NO_RESIDENTE_EXONERADO.3"),
        ],
    )
    ret_retencion_iva = fields.Boolean(string="Retención IVA", default=False)
    ret_concepto_iva = fields.Selection(
        string="Concepto IVA", selection=[("IVA.1", "IVA.1"), ("IVA.2", "IVA.2"), ("IVA.3", "IVA.3"), ("IVA.4", "IVA.4")]
    )
    ret_renta_porcentaje = fields.Float(string="Porcentaje renta", digits=(2, 1))
    ret_renta_cabezas_base = fields.Integer(string="Retención por cabeza")
    ret_renta_cabezas_cantidad = fields.Integer(string="Cantidad de cabezas")
    ret_renta_toneladas_base = fields.Integer(string="Retención por tonelada")
    ret_renta_toneladas_cantidad = fields.Integer(string="Cantidad de toneladas")
    ret_iva_porcentaje5 = fields.Float(string="Porc. sobre IVA 5")
    ret_iva_porcentaje10 = fields.Float(string="Porc. sobre IVA 10")
    ret_line_ids = fields.One2many("account.payment.retencion.line", "payment_id", string="Lineas de retencion")
    json_file = fields.Binary(string="JSON file")

    def desbloquear_json(self):
        self.write({"json_file": False})

    def genera_json(self):
        result = []
        for record in self:
            if record.state not in ["posted"]:
                raise exceptions.ValidationError("Sólo se pueden descargar retenciones en estado Publicado")
            if record.payment_method_code != "retencion_emitida":
                raise exceptions.ValidationError("Sólo se pueden descargar registros con el método Retención Emitida")
            if record.json_file:
                raise exceptions.ValidationError(
                    f"La retención {record.name} de la factura {record.ret_nro_comprobante} ya fué descargada anteriormente. Si desea volver a descargarla por favor utilice el botón Desbloquear descarga de JSON en el formulario del registro"
                )

            detalle = []
            for line in record.ret_line_ids:
                l = {
                    "cantidad": line.ret_cantidad or 0,
                    "tasaAplica": str(line.ret_tasa_aplica) or "0",
                    "precioUnitario": line.ret_precio_unitario or 0,
                    "descripcion": line.ret_descripcion or "",
                }
                detalle.append(l)
            res = {
                "detalle": detalle,
                "retencion": {
                    "moneda": record.ret_moneda.name if record.ret_moneda else "",
                    "fecha": record.ret_fecha.strftime("%Y-%m-%d") if record.ret_fecha else record.date.strftime("%Y-%m-%d"),
                    "retencionRenta": record.ret_retencion_renta,
                    "conceptoRenta": record.ret_concepto_renta or "",
                    "ivaPorcentaje5": record.ret_iva_porcentaje5 or 0,
                    "ivaPorcentaje10": record.ret_iva_porcentaje10 or 0,
                    "rentaCabezasBase": record.ret_renta_cabezas_base or 0,
                    "rentaCabezasCantidad": record.ret_renta_cabezas_cantidad or 0,
                    "rentaToneladasBase": record.ret_renta_toneladas_base or 0,
                    "rentaToneladasCantidad": record.ret_renta_toneladas_cantidad or 0,
                    "rentaPorcentaje": record.ret_renta_porcentaje or 0,
                    "retencionIva": record.ret_retencion_iva,
                    "conceptoIva": record.ret_concepto_iva or "",
                },
                "informado": {
                    "ruc": record.ret_ruc or "",
                    "dv": record.ret_dv or "",
                    "nombre": record.ret_nombre or "",
                    "identificacion": record.ret_identificacion or "",
                    "situacion": record.ret_situacion or "",
                    "tipoIdentificacion": record.ret_tipo_identificacion or "",
                    # 'correoElectronico':record.ret_correo_electronico or "",
                    "correoElectronico": "",  # Se envía este dato vacío por errores generados en la plataforma Tesaka
                    "direccion": record.ret_direccion if record.ret_situacion != "CONTRIBUYENTE" else "",
                    # 'telefono':record.ret_telefono or "",
                    "telefono": "",  # Se envía este dato vacío por errores generados en la plataforma Tesaka
                    "pais": record.ret_pais.name if record.ret_pais else "",
                    #'nombreFantasia':None,
                    "domicilio": record.ret_domicilio or "",
                    "tieneRepresentante": record.ret_tiene_representante,
                    "tieneBeneficiario": record.ret_tiene_beneficiario,
                    # 'representante':{
                    #     'tipoIdentificacion':record.ret_tipo_ident_representante or "",
                    #     'identificacion':record.ret_identificacion_representante or "",
                    #     'nombre':record.ret_nombre_representante or ""
                    # },
                    # 'beneficiario':{
                    #     'tipoIdentificacion':record.ret_tipo_ident_beneficiario or "",
                    #     'identificacion':record.ret_identificacion_beneficiario or "",
                    #     'nombre':record.ret_nombre_beneficiario or ""
                    # }
                },
                "transaccion": {
                    "numeroComprobanteVenta": record.ret_nro_comprobante or "",
                    "condicionCompra": record.ret_condicion_compra or "",
                    "cuotas": record.ret_cuotas,
                    "tipoComprobante": int(record.ret_tipo_comprobante) if record.ret_tipo_comprobante else None,
                    "fecha": record.ret_fecha_comprobante.strftime("%Y-%m-%d") if record.ret_fecha_comprobante else None,
                    "numeroTimbrado": record.ret_nro_timbrado or "",
                },
                "atributos": {
                    "fechaCreacion": record.ret_fecha_creacion.strftime("%Y-%m-%d") if record.ret_fecha_creacion else None,
                    "fechaHoraCreacion": record.ret_fecha_hora_creacion.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
            if record.currency_id != record.company_id.currency_id and record.move_id.line_ids:
                total_balance = 0
                total_amount_currency = 0
                move_lines = record.move_id.line_ids.filtered(lambda x: x.currency_id == record.currency_id)
                for move_line in move_lines:
                    total_balance += abs(move_line.balance)
                    total_amount_currency += abs(move_line.amount_currency)
                if total_balance and total_amount_currency:
                    res["retencion"]["tipoCambio"] = int(total_balance / total_amount_currency)
            result.append(res)
        return json.dumps(result, indent=4)

    def button_genera_json(self):
        data = self.genera_json()
        self.json_file = base64.b64encode(data.encode())
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/account.payment/%s/json_file/%s?download=true"
            % (self[0].id, f"Odoo_RET_{int(sum(self.mapped('amount')))}.txt"),
            "target": "new",
        }

    @api.onchange("partner_id", "payment_type", "payment_method_code")
    @api.depends("partner_id", "partner_id.vat", "partner_id.phone", "partner_id.country_id", "payment_type", "payment_method_code")
    def onchange_proveedor(self):
        for record in self:
            if record.payment_type != "outbound" or record.payment_method_code != "retencion_emitida" or record.state != "draft":
                return
            if record.partner_id:
                record.ret_nombre = record.partner_id.name
            if record.partner_id.email:
                record.ret_correo_electronico = record.partner_id.email
            if record.partner_id.phone:
                record.ret_telefono = record.partner_id.phone
            if record.partner_id.street:
                record.ret_domicilio = record.partner_id.street
                record.ret_direccion = record.partner_id.street
            if record.partner_id.vat:
                pattern = "^[0-9]+-[0-9]$"

                if re.match(pattern, record.partner_id.vat) and record.partner_id.vat.split("-")[1] == str(
                    record.partner_id.digito_verificador(record.partner_id.vat)
                ):
                    record.ret_ruc = record.partner_id.vat.split("-")[0]
                    record.ret_dv = record.partner_id.vat.split("-")[1]
                    record.ret_situacion = "CONTRIBUYENTE"
                    record.ret_tipo_identificacion = ""
                elif (
                    not re.match(pattern, record.partner_id.vat)
                    and record.partner_id.country_id
                    and record.partner_id.country_id.code == "PY"
                ):
                    record.ret_situacion = "NO_CONTRIBUYENTE"
                    record.ret_tipo_identificacion = "CEDULA"
                elif not re.match(pattern, record.partner_id.vat) and (
                    (record.partner_id.country_id and record.partner_id.country_id.code != "PY") or not record.partner_id.country_id
                ):
                    record.ret_situacion = "NO_RESIDENTE"
                    record.ret_tipo_identificacion = "PASAPORTE"
            else:
                record.ret_situacion = "NO_CONTRIBUYENTE"
                record.ret_tipo_identificacion = "CEDULA"
            record.onchange_facturas()

    @api.onchange("reconciled_invoice_ids")
    def onchange_facturas(self):
        for record in self:
            if (
                record.reconciled_invoice_ids.filtered(lambda x: x.state == "posted")
                and len(record.reconciled_invoice_ids.filtered(lambda x: x.state == "posted")) == 1
            ):
                record.ret_nro_comprobante = record.reconciled_invoice_ids.filtered(lambda x: x.state == "posted").ref
                record.ret_tipo_comprobante = "1"
                record.ret_nro_timbrado = record.reconciled_invoice_ids.filtered(lambda x: x.state == "posted").timbrado_id.name
                record.ret_fecha_comprobante = record.reconciled_invoice_ids.filtered(lambda x: x.state == "posted").invoice_date
                if (
                    record.reconciled_invoice_ids.filtered(lambda x: x.state == "posted").invoice_date
                    == record.reconciled_invoice_ids.filtered(lambda x: x.state == "posted").invoice_date_due
                ):
                    record.ret_condicion_compra = "CONTADO"
                    record.ret_cuotas = 1
                else:
                    record.ret_condicion_compra = "CREDITO"
                    record.ret_cuotas = len(
                        record.reconciled_invoice_ids.filtered(lambda x: x.state == "posted").line_ids.filtered(
                            lambda x: x.account_id == "liability_payable"
                        )
                    )
                detalle = []
                record.write({"ret_line_ids": [(5, 0, 0)]})
                for r in record.reconciled_invoice_ids.filtered(lambda x: x.state == "posted").invoice_line_ids:
                    l = {
                        "ret_cantidad": r.quantity,
                        "ret_precio_unitario": r.price_unit,
                        "ret_descripcion": r.name,
                        "ret_tasa_aplica": int(r.tax_ids.filtered(lambda x: "IVA" in x.name)[0].amount),
                    }
                    detalle.append((0, 0, l))
                record.ret_line_ids = detalle

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        self.ret_fecha_creacion = fields.Date.today()
        self.ret_fecha_hora_creacion = fields.Datetime.now()
        return res


class AccountPaymentRetencionLine(models.Model):
    _name = "account.payment.retencion.line"
    _description = "Linea de retencion"

    payment_id = fields.Many2one("account.payment")
    ret_cantidad = fields.Float(string="Cantidad", digits=(14, 2))
    ret_tasa_aplica = fields.Integer(string="Tasa aplicada")
    ret_precio_unitario = fields.Float(string="Precio unitario", digits=(14, 2))
    ret_descripcion = fields.Char(string="Descripción")
