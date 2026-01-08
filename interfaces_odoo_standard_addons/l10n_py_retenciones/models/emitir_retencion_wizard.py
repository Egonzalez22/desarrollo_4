from odoo import _, api, fields, models, exceptions

import re


class EmitirRetencionWizard(models.TransientModel):
    _name = "emitir.retencion.wizard"
    _description = "EmitirRetencionWizard"

    fecha_retencion = fields.Date(string="Fecha de retencion", required=True)
    journal_id = fields.Many2one("account.journal", string="Diario de retenciones", required=True)
    invoice_ids = fields.Many2many("account.move", string="Facturas")
    line_ids = fields.One2many("emitir.retencion.wizard.line", "retencion_wizard_id", string="Lineas de retencion")

    @api.onchange("invoice_ids")
    def populate_invoices(self):
        lines = []
        for invoice in self.invoice_ids:
            for group_by_subtotal in invoice.tax_totals["groups_by_subtotal"]:
                for tax in invoice.tax_totals["groups_by_subtotal"][group_by_subtotal]:
                    l = {
                        "move_id": invoice.id,
                        "tipo_retencion": "IVA",
                        "ret_concepto_iva": "IVA.1",
                        "tipo_importe": "total",
                        "tax_id": invoice.line_ids.tax_ids.filtered(lambda x: x.tax_group_id.id == tax["tax_group_id"])[0].id,
                    }
                    lines.append((0, 0, l))

        self.write({"line_ids": lines})

    def generar_retenciones(self):
        payment_ids = []
        for line in self.line_ids:
            payment_id = self.env["account.payment"].with_context(avoid_payment_group=True).create(self.create_payment_values(line))
            if payment_id:
                payment_ids.append(payment_id.id)
                payment_id.action_post()
                (
                    line.move_id.mapped("line_ids").filtered(
                        lambda x: x.account_id.account_type in ["asset_receivable", "liability_payable"]
                    )
                    + payment_id.mapped("line_ids").filtered(
                        lambda x: x.account_id.account_type in ["asset_receivable", "liability_payable"]
                    )
                ).reconcile()
        return {
            "name": "Retenciones emitidas",
            "view_mode": "list,form",
            "res_model": "account.payment",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", payment_ids)],
        }

    def create_payment_values(self, record):
        payment_values = {
            "payment_type": "outbound",
            "partner_id": record.move_id.partner_id.id,
            "date": self.fecha_retencion,
            "journal_id": self.journal_id.id,
            "currency_id": record.currency_id.id,
            "reconciled_invoice_ids": [(6, 0, record.move_id.ids)],
        }

        if record.move_id.partner_id:
            payment_values["ret_nombre"] = record.move_id.partner_id.name
        if record.move_id.partner_id.email:
            payment_values["ret_correo_electronico"] = record.move_id.partner_id.email
        if record.move_id.partner_id.phone:
            payment_values["ret_telefono"] = record.move_id.partner_id.phone
        if record.move_id.partner_id.street:
            payment_values["ret_domicilio"] = record.move_id.partner_id.street
            payment_values["ret_direccion"] = record.move_id.partner_id.street
        if record.move_id.partner_id.vat:
            pattern = "^[0-9]+-[0-9]$"
            if re.match(pattern, record.move_id.partner_id.vat) and record.move_id.partner_id.vat.split("-")[1] == str(
                record.move_id.partner_id.digito_verificador(record.move_id.partner_id.vat)
            ):
                payment_values["ret_ruc"] = record.move_id.partner_id.vat.split("-")[0]
                payment_values["ret_dv"] = record.move_id.partner_id.vat.split("-")[1]
                payment_values["ret_situacion"] = "CONTRIBUYENTE"
                payment_values["ret_tipo_identificacion"] = ""
            elif (
                not re.match(pattern, record.move_id.partner_id.vat)
                and record.move_id.partner_id.country_id
                and record.move_id.partner_id.country_id.code == "PY"
            ):
                payment_values["ret_situacion"] = "NO_CONTRIBUYENTE"
                payment_values["ret_tipo_identificacion"] = "CEDULA"
            elif not re.match(pattern, record.move_id.partner_id.vat) and (
                (record.move_id.partner_id.country_id and record.move_id.partner_id.country_id.code != "PY")
                or not record.move_id.partner_id.country_id
            ):
                payment_values["ret_situacion"] = "NO_RESIDENTE"
                payment_values["ret_tipo_identificacion"] = "PASAPORTE"
        else:
            payment_values["ret_situacion"] = "NO_CONTRIBUYENTE"
            payment_values["ret_tipo_identificacion"] = "CEDULA"

        if record.move_id and len(record.move_id) == 1:
            payment_values["ret_nro_comprobante"] = record.move_id.ref
            payment_values["ret_tipo_comprobante"] = "1"
            payment_values["ret_nro_timbrado"] = record.move_id.timbrado_id.name
            payment_values["ret_fecha_comprobante"] = record.move_id.invoice_date
            if record.move_id.invoice_date == record.move_id.invoice_date_due:
                payment_values["ret_condicion_compra"] = "CONTADO"
                payment_values["ret_cuotas"] = 1
            else:
                payment_values["ret_condicion_compra"] = "CREDITO"
                payment_values["ret_cuotas"] = len(
                    record.move_id.line_ids.filtered(lambda x: x.account_id and x.account_id.account_type == "liability_payable")
                )
            detalle = []
            for r in record.move_id.invoice_line_ids:
                aplicable_tax_ids = r.tax_ids.filtered(lambda x: "IVA" in x.name)
                if aplicable_tax_ids and aplicable_tax_ids[0].amount:
                    l = {
                        "ret_cantidad": r.quantity,
                        "ret_precio_unitario": r.price_unit,
                        "ret_descripcion": r.name,
                        "ret_tasa_aplica": int(aplicable_tax_ids[0].amount),
                    }
                    detalle.append((0, 0, l))
            payment_values["ret_line_ids"] = detalle
            payment_values["ret_retencion_iva"] = True if record.tipo_retencion == "IVA" else False
            payment_values["ret_concepto_iva"] = record.ret_concepto_iva if record.ret_concepto_iva else ""
            payment_values["ret_retencion_renta"] = True if record.tipo_retencion == "RENTA" else False
            payment_values["ret_concepto_renta"] = record.ret_concepto_renta if record.ret_concepto_renta else ""
            payment_values["ret_iva_porcentaje10"] = (
                record.porcentaje if record.tipo_retencion == "IVA" and record.tax_id.amount == 10 else 0
            )
            payment_values["ret_iva_porcentaje5"] = record.porcentaje if record.tipo_retencion == "IVA" and record.tax_id.amount == 5 else 0
            payment_values["ret_renta_porcentaje"] = record.porcentaje if record.tipo_retencion == "RENTA" else 0
            payment_values["amount"] = record.retencion_amount
            payment_values["currency_id"] = record.currency_id.id
            payment_values["ret_moneda"] = record.currency_id.id
            payment_values["ref"] = record.move_id.ref
            payment_values["partner_type"] = "supplier"
            payment_values["ret_fecha"] = self.fecha_retencion

        return payment_values


class EmitirRetencionWizardLine(models.TransientModel):
    _name = "emitir.retencion.wizard.line"
    _description = "EmitirRetencionWizardLine"

    retencion_wizard_id = fields.Many2one("emitir.retencion.wizard")
    move_id = fields.Many2one("account.move", string="Factura")
    tipo_retencion = fields.Selection(string="Tipo de retencion", selection=[("IVA", "IVA"), ("RENTA", "RENTA")])
    ret_concepto_iva = fields.Selection(
        string="Concepto IVA", selection=[("IVA.1", "IVA.1"), ("IVA.2", "IVA.2"), ("IVA.3", "IVA.3"), ("IVA.4", "IVA.4")]
    )
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
    tax_id = fields.Many2one("account.tax", string="Impuesto", domain=[("type_tax_use", "=", "purchase")])
    move_currency_id = fields.Many2one("res.currency", string="Moneda de la factura", related="move_id.currency_id")
    tipo_importe = fields.Selection(string="Tipo de importe", selection=[("cuota", "Cuota"), ("total", "Total")])
    invoice_amount = fields.Monetary(string="Monto cuota", currency_field="move_currency_id", compute="compute_invoice_amount")
    porcentaje = fields.Float(string="Porcentaje de retención", compute="compute_porcentaje")
    currency_id = fields.Many2one("res.currency", string="Moneda de la retención", default=lambda self: self.move_currency_id)
    retencion_amount = fields.Monetary(string="Monto de la retención", currency_field="currency_id", compute="compute_retencion_amount")

    @api.onchange("tipo_importe")
    @api.depends("tipo_importe", "move_id")
    def compute_invoice_amount(self):
        for this in self:
            invoice_amount = 0
            if this.tipo_importe and this.move_id:
                move_id = this.move_id
                if this.tipo_importe and this.tipo_importe == "total":
                    invoice_amount = move_id.amount_residual
                if this.tipo_importe and this.tipo_importe == "cuota":
                    invoice_amount = abs(
                        move_id.line_ids.filtered(
                            lambda x: x.account_id and x.account_id.account_type == "liability_payable" and not x.reconciled
                        )
                        .sorted(key=lambda z: z.date_maturity)[0]
                        .amount_currency
                    )
            if this.invoice_amount != invoice_amount:
                this.invoice_amount = invoice_amount

    @api.depends("move_id", "tipo_retencion", "tax_id")
    @api.onchange("move_id", "tipo_retencion", "tax_id")
    def compute_porcentaje(self):
        for this in self:
            if this.tipo_retencion and this.tax_id:
                rule_id = this.env["retencion.rule"].search(
                    [
                        ("company_id", "=", self.env.company.id),
                        ("tipo_agente", "=", self.env.company.tipo_agente_retencion),
                        ("tipo_retencion", "=", this.tipo_retencion),
                        ("tax_id", "=", this.tax_id.ids[0]),
                    ]
                )
                if rule_id:
                    this.porcentaje = rule_id.porcentaje
                else:
                    this.porcentaje = 0
            else:
                this.porcentaje = 0

    @api.onchange("move_id", "tipo_retencion", "tax_id", "tipo_importe", "porcentaje")
    def compute_retencion_amount(self):
        for this in self:
            retencion_amount = 0
            if this.tipo_importe and this.tipo_retencion and this.porcentaje:
                tax_total = 0
                for group_by_subtotal in this.move_id.tax_totals["groups_by_subtotal"]:
                    for tax in this.move_id.tax_totals["groups_by_subtotal"][group_by_subtotal]:
                        if this.tax_id.tax_group_id.id == tax["tax_group_id"]:
                            tax_total += tax["tax_group_amount"]
                if this.move_id.invoice_payments_widget and this.move_id.invoice_payments_widget.get("content"):
                    for invoice_payment in this.move_id.invoice_payments_widget.get("content"):
                        payment_move_id = this.move_id.browse(invoice_payment.get("move_id"))
                        if payment_move_id.move_type in ["in_refund"]:
                            for payment_move_tax_subtotal in payment_move_id.tax_totals.get("subtotals"):
                                for payment_move_tax_group in payment_move_tax_subtotal.get("tax_groups"):
                                    if this.tax_id.id in payment_move_tax_group.get("involved_tax_ids"):
                                        tax_total -= payment_move_tax_group.get("tax_amount_currency")
                retencion_amount = tax_total * (this.porcentaje / 100)
            this.retencion_amount = retencion_amount
