from odoo import fields, api, models, exceptions
from datetime import date
import math
import locale


class PaymentGroup(models.Model):
    _name = "grupo_account_payment.payment.group"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Grupo de pago"
    _order = "name desc"

    name = fields.Char("Número", default="Borrador", track_visibility="onchange")
    partner_id = fields.Many2one("res.partner", string="Empresa", required=True, track_visibility="onchange")
    payment_ids = fields.One2many("account.payment", "payment_group_id", string="Lineas de pago", copy="False", track_visibility="onchange")
    fecha = fields.Date(string="Fecha", default=lambda x: date.today(), required=True, track_visibility="onchange")
    user_id = fields.Many2one("res.users", string="Usuario", default=lambda self: self.env.user)
    currency_id = fields.Many2one(
        "res.currency",
        string="Moneda",
        default=lambda self: self.env.user.company_id.currency_id,
        groups="base.group_multi_currency",
        track_visibility="onchange",
    )
    company_id = fields.Many2one(
        "res.company", string="Compañia", default=lambda self: self.env.user.company_id, track_visibility="onchange"
    )
    amount_total = fields.Monetary(string="Total de pagos", compute="compute_total", default=0, store=True, track_visibility="onchange")
    amount_total_company_signed = fields.Monetary(string="Total en moneda de la compañia", default=0, compute="compute_total", store=True)
    payment_type = fields.Selection(
        [
            ("inbound", "Inbound"),
            ("outbound", "Outbound"),
        ],
        string="Tipo de Pago",
        required=True,
    )
    memo = fields.Char(string="Referencia", track_visibility="onchange")
    state = fields.Selection(
        string="Estado",
        selection=[("draft", "Borrador"), ("done", "Confirmado"), ("cancel", "Cancelado")],
        default="draft",
        track_visibility="onchange",
    )
    invoice_ids = fields.Many2many("account.move", string="Facturas", copy="False", track_visibility="onchange")
    amount_total_selected = fields.Monetary(
        string="Total deudas seleccionadas", compute="compute_total", default=0, store=True, track_visibility="onchange"
    )
    cantRecibos = fields.Integer(compute="_cantRecibos")
    nro_recibo_fisico = fields.Char(string="Nro. recibo manual")
    diferenciaPagos = fields.Monetary(string="Diferencia", compute="compute_diferencia")
    sugerenciaPagos = fields.Monetary(string="Diferencia", compute="compute_diferencia")

    fecha_letras = fields.Char(compute="_fechaLetras")
    partner_type = fields.Selection(string="Tipo de Empresa", selection=[("customer", "cliente"), ("supplier", "proveedor")])
    invoice_type = fields.Char(compute="_compute_invoice_type")

    mantenerAbierto = fields.Selection(
        string="Contabilizar Diferencia",
        selection=[("mantener", "Mantener Abierto"), ("paid", "Marcar como completamente pagado")],
        default="mantener",
    )

    writeoff_account_id = fields.Many2one(
        string="Contabilizar Diferencia en:",
        comodel_name="account.account",
    )
    writeoff_label = fields.Char(string="Explicación")

    ocultar_mantenerAbierto = fields.Boolean(string="field_name", compute="compute_mantenerAbierto")
    ocultar_writeoff = fields.Boolean(string="field_name", compute="compute_ocultar_writeoff")
    writeOffMove_id = fields.Many2one("account.move", string="Asiento de conciliación", copy=False)

    invoice_group_ids = fields.Many2many("account.move", string="Facturas en otros grupos de pago", compute="_compute_invoice_group_ids")

    amount_total_assigned = fields.Monetary(string="Total Monto Asignado")

    repartition_move_ids = fields.One2many("account.move", "origin_grupo_account_payment_id")

    currency_changed = fields.Boolean(default=False)

    paid_invoices = fields.Many2many("grupo_account_am", string="Facturas pagadas")

    @api.onchange("currency_id")
    def _select_other_currency_id(self):
        """Limpia los valores de repartición y activa la bandera cuando cambia la moneda."""
        for this in self:
            for invoice in this.invoice_ids:
                this.currency_changed = True
                invoice.payment_amount_repartition = 0.0
                invoice._get_amount_residual_in_payment_group_currency(this.payment_type, this.currency_id, this.fecha)

    @api.onchange("invoice_ids")
    def _compute_invoice_payment_amount_repartition(self):
        for this in self:
            for invoice in this.invoice_ids:
                invoice._get_amount_residual_in_payment_group_currency(this.payment_type, this.currency_id, this.fecha)

                # Si se cambia la moneda se resetea
                if this.currency_changed:
                    invoice.payment_amount_repartition = 0.0
                    this.currency_changed = False

    @api.depends("invoice_ids")
    def _compute_invoice_group_ids(self):
        for group in self:
            draft_groups = self.env["grupo_account_payment.payment.group"].search([("state", "=", "draft")])
            invoices_in_draft_groups = draft_groups.mapped("invoice_ids")
            group.invoice_group_ids = invoices_in_draft_groups

    def crearAsientoConciliacion(self):
        for record in self:
            lines_ids = []
            if record.payment_type == "outbound":
                debit = {
                    "account_id": record.partner_id.property_account_payable_id.id,
                    "date": record.fecha,
                    "name": record.writeoff_label,
                    "currency_id": record.currency_id.id,
                    "amount_currency": record.diferenciaPagos,
                    "partner_id": record.partner_id.id,
                }
                lines_ids.append((0, 0, debit))
                credit = {
                    "account_id": record.writeoff_account_id.id,
                    "date": record.fecha,
                    "name": record.writeoff_label,
                    "currency_id": record.currency_id.id,
                    "amount_currency": record.diferenciaPagos * -1,
                }
                lines_ids.append((0, 0, credit))
            elif record.payment_type == "inbound":
                debit = {
                    "account_id": record.writeoff_account_id.id,
                    "date": record.fecha,
                    "name": record.writeoff_label,
                    "currency_id": record.currency_id.id,
                    "amount_currency": record.diferenciaPagos,
                }
                lines_ids.append((0, 0, debit))
                credit = {
                    "account_id": record.partner_id.property_account_receivable_id.id,
                    "date": record.fecha,
                    "name": record.writeoff_label,
                    "currency_id": record.currency_id.id,
                    "partner_id": record.partner_id.id,
                    "amount_currency": record.diferenciaPagos * -1,
                }
                lines_ids.append((0, 0, credit))

            move = {
                "journal_id": record.env["account.journal"].search([("type", "=", "general")])[0].id,
                "date": record.fecha,
                "partner_id": record.partner_id.id,
                "move_type": "entry",
                "ref": record.writeoff_label,
                "line_ids": lines_ids,
            }

            move_id = record.env["account.move"].create(move)
            if move_id:
                record.write({"writeOffMove_id": move_id.id})
                move_id.action_post()

    @api.depends("amount_total_selected", "amount_total", "payment_ids", "state")
    def compute_diferencia(self):
        for this in self:
            if not this.invoice_ids:
                this.diferenciaPagos = 0
            elif this.payment_ids:
                # Calcula la diferencia usando los pagos seleccionados y el total
                this.diferenciaPagos = this.amount_total_selected - this.amount_total
            else:
                # Si no hay pagos, usa el residual de las facturas
                total_residual_invoices = sum(invoice.payment_amount_repartition for invoice in this.invoice_ids)
                this.diferenciaPagos = total_residual_invoices - this.amount_total

            this.sugerenciaPagos = max(this.diferenciaPagos, 0)

    @api.depends("amount_total_selected", "amount_total", "diferenciaPagos")
    def compute_mantenerAbierto(self):
        if self.amount_total_selected != 0 and self.amount_total != 0 and self.diferenciaPagos != 0:
            self.ocultar_mantenerAbierto = False
        else:
            self.ocultar_mantenerAbierto = True

    @api.depends("mantenerAbierto")
    def compute_ocultar_writeoff(self):
        if not self.ocultar_mantenerAbierto and self.mantenerAbierto == "paid":
            self.ocultar_writeoff = False
        else:
            self.ocultar_writeoff = True

    def _fechaLetras(self):
        for this in self:
            this.fecha_letras = this.fecha.strftime("%d de %B de %Y")

    def _cantRecibos(self):
        for this in self:
            if len(this.invoice_ids) > 10:
                this.cantRecibos = math.ceil(len(this.invoice_ids) / 10)
            else:
                this.cantRecibos = 1

    @api.onchange("partner_id")
    @api.depends("payment_ids")
    def onchange_partner(self):
        for i in self:
            if i.payment_ids:
                for j in i.payment_ids:
                    j.update({"partner_id": i.partner_id.id})
            if i.invoice_ids and not i.invoice_ids.filtered(
                lambda x: x.partner_id == i.partner_id or x.partner_id.commercial_partner_id == i.partner_id
            ):
                i.update({"invoice_ids": [(5, 0, 0)]})

    @api.onchange("fecha")
    @api.depends("payment_ids")
    def onchange_fecha(self):
        for i in self:
            if i.payment_ids:
                for j in i.payment_ids:
                    j.update({"date": i.fecha})

    # @api.onchange('payment_ids','invoice_ids','currency_id')
    # @api.depends('payment_ids','invoice_ids','currency_id')
    # def compute_total(self):
    #     for i in self:
    #         i.amount_total = sum(i.payment_ids.mapped('amount') or [0])
    #         amount_total_selected = 0
    #         for invoice in i.invoice_ids :
    #             if invoice.currency_id == i.currency_id :
    #                 amount_total_selected += invoice.amount_residual
    #             else :
    #                 amount_total_selected += invoice.currency_id._convert(invoice.amount_residual,i.currency_id,self.env.company,i.fecha)

    #         i.amount_total_selected = amount_total_selected
    @api.onchange("payment_ids", "invoice_ids", "currency_id")
    @api.depends("payment_ids", "invoice_ids", "currency_id", "state")
    def compute_total(self):
        for i in self:
            i.payment_ids._compute_amount_company_currency_signed()
            i.amount_total = sum(i.payment_ids.mapped("amount") or [0])
            amount_total_selected = 0
            for invoice in i.invoice_ids:
                amount_total_selected += invoice.payment_amount_repartition

            i.amount_total_selected = amount_total_selected

    @api.depends("payment_type")
    def genera_secuencia(self):
        if self.payment_type == "inbound":
            seq = self.sudo().env["ir.sequence"].next_by_code("seq_recibo_gp")
        elif self.payment_type == "outbound":
            seq = self.sudo().env["ir.sequence"].next_by_code("seq_orden_pago_gp")
        return seq

    def confirmar(self):
        for i in self:
            for j in i.payment_ids:
                if not j.tipo_pago:
                    raise exceptions.ValidationError("El tipo de pago no puede estar vacío, por favor asigne el valor en la linea de pago.")
                j.action_post()
                if j.payment_type == "inbound":
                    movimiento = j.line_ids.filtered(lambda z: z.debit > 0)
                elif j.payment_type == "outbound":
                    movimiento = j.line_ids.filtered(lambda z: z.credit > 0)
                else:
                    movimiento = j.line_ids
                for x in movimiento:
                    referencia = j.tipo_pago.capitalize() + " "
                    if j.bank_id:
                        referencia += j.bank_id.name + " "
                    if j.nro_cheque:
                        referencia += j.nro_cheque + " "
                    if j.nro_documento:
                        referencia += j.nro_documento + " "
                    if self.nro_recibo_fisico:
                        j.nro_recibo = self.nro_recibo_fisico
                    x.write({"ref": referencia})
            i.write({"state": "done"})

    def button_confirmar(self):
        for this in self:
            # Se verifica que existan lineas de pago cargadas
            if not this.payment_ids:
                raise exceptions.ValidationError("Debe agregar líneas de pagos para poder confirmar la operación")
            # Se publica cada pago
            this.confirmar()

            # Si se seleccionaron facturas pero los montos a distribuir suman cero, es decir
            # que no se quieren aplicar montos específicos a las facturas, se utiliza el método convencional
            # de conciliación de Odoo
            if this.invoice_ids and sum(this.invoice_ids.mapped("payment_amount_repartition")) == 0:
                (
                    this.invoice_ids.mapped("line_ids").filtered(
                        lambda x: x.account_id.account_type in ["asset_receivable", "liability_payable"]
                    )
                    + this.payment_ids.mapped("line_ids").filtered(
                        lambda x: x.account_id.account_type in ["asset_receivable", "liability_payable"]
                    )
                ).reconcile()
            # Si no existen facturas asociadas pero si pagos, se confirman los pagos como pagos sueltos
            elif not this.invoice_ids and this.payment_ids:
                pass
            # Si se seleccionario facturas y se aplicaron montos concretos a distribuir:
            # Se generan los asientos contables con la distribución y estos se aplican a cada factura
            else:
                # Se publica cada account.payment actualizando en la referencia la información de los pagos

                # Crear asiento de pagos distribución de pagos parciales
                this.crear_asiento_distribucion()
                # Conciliar asiento de distribucion
                this.conciliar_asiento_distribucion()

            this.generar_historico()

    def crear_asiento_distribucion(self):

        # Se busca un diario que tenga habilitada la opción de Diario de pagos parciales
        journal_for_repartiton_operations = self.env["account.journal"].search([("diario_pagos_parciales", "=", True)], limit=1)
        account_id = (
            self.payment_ids[0].line_ids.filtered(lambda x: x.account_type in ["asset_receivable", "liability_payable"]).account_id.id
        )
        if not journal_for_repartiton_operations:
            raise exceptions.ValidationError("No existe un diario especificado para la distribución parcial de pagos")
        line_ids = []
        sign = 1 if self.payment_type == "inbound" else -1
        total_line = {
            "currency_id": self.currency_id.id,
            "amount_currency": sum(self.invoice_ids.mapped("payment_amount_repartition")) * sign,
            "partner_id": self.partner_id.id,
            "account_id": account_id,
            "name": "Aplicación de pagos parciales: %s" % self.name,
        }
        if not self.ocultar_mantenerAbierto and self.mantenerAbierto == "mantener":
            if sum(self.invoice_ids.mapped("payment_amount_repartition")) > sum(self.payment_ids.mapped("amount")):
                raise exceptions.ValidationError("El monto a pagar distribuido en las facturas es mayor al monto de los pagos")
        if not self.ocultar_writeoff and self.mantenerAbierto == "paid":
            total_line.update({"amount_currency": sum(self.payment_ids.mapped("amount")) * sign})
            line_ids.append(
                (
                    0,
                    0,
                    {
                        "currency_id": self.currency_id.id,
                        "amount_currency": self.diferenciaPagos * sign,
                        "partner_id": self.partner_id.id,
                        "account_id": self.writeoff_account_id.id,
                        "name": "%s - %s" % (self.name, self.writeoff_label),
                    },
                )
            )

        line_ids.append((0, 0, total_line))
        for invoice in self.invoice_ids:
            line = {
                "currency_id": self.currency_id.id,
                "amount_currency": invoice.payment_amount_repartition * sign * -1,
                "partner_id": self.partner_id.id,
                "account_id": account_id,
                "name": "Aplicación de pago parcial: %s a factura: %s" % (self.name, invoice.name),
                "payment_repartition_origin_invoice_id": invoice.id,
            }
            line_ids.append((0, 0, line))
        distribucion_move = {
            "journal_id": journal_for_repartiton_operations.id,
            "ref": "Aplicación de pagos parciales: %s" % self.name,
            "date": self.fecha,
            "move_type": "entry",
            "currency_id": self.currency_id.id,
            "line_ids": line_ids,
            "is_repartition_move": True,
        }
        for existing_repartition_move in self.repartition_move_ids:
            existing_repartition_move.button_draft()
            existing_repartition_move.unlink()

        distribution_move_id = self.env["account.move"].create(distribucion_move)
        self.write({"repartition_move_ids": [(4, distribution_move_id.id, 0)]})
        if distribution_move_id:
            distribution_move_id.action_post()

    def conciliar_asiento_distribucion(self):

        if self.repartition_move_ids:

            # Lo primero que se concilian son las lineas de cuentas por cobrar del pago contra la linea del total de pagos
            # del asiento de distribución.
            (
                self.payment_ids.line_ids.filtered(lambda x: x.account_type in ["asset_receivable", "liability_payable"])
                + self.repartition_move_ids.line_ids.filtered(
                    lambda x: not x.payment_repartition_origin_invoice_id and x.account_type in ["asset_receivable", "liability_payable"]
                )
            ).reconcile()
            # Luego se concilian la lineas individuales del asiento de distribución de cada factura contra la linea de deuda de las facturas
            repartition_lines = self.repartition_move_ids.line_ids.filtered(
                lambda x: x.payment_repartition_origin_invoice_id and x.account_type in ["asset_receivable", "liability_payable"]
            )
            for repartition_line in repartition_lines:
                payment_repartition_origin_invoice_lines = repartition_line.payment_repartition_origin_invoice_id.line_ids.filtered(
                    lambda x: x.account_type in ["asset_receivable", "liability_payable"]
                )
                if self.payment_type == "inbound":
                    payment_repartition_origin_invoice_lines = payment_repartition_origin_invoice_lines.filtered(
                        lambda x: x.amount_residual > 0
                    )
                elif self.payment_type == "outbound":
                    payment_repartition_origin_invoice_lines = payment_repartition_origin_invoice_lines.filtered(
                        lambda x: x.amount_residual < 0
                    )
                (repartition_line + payment_repartition_origin_invoice_lines).reconcile()

    def conciliar(self):
        for record in self:
            # Filtramos las líneas de deuda, pago y conciliación
            lineasDeuda = record.invoice_ids.line_ids.filtered(
                lambda x: x.account_id.account_type in ["asset_receivable", "liability_payable"]
            )
            lineasPago = record.payment_ids.line_ids.filtered(
                lambda x: x.account_id.account_type in ["asset_receivable", "liability_payable"]
            )
            lineasConciliacion = record.writeOffMove_id.line_ids.filtered(
                lambda x: x.account_id.account_type in ["asset_receivable", "liability_payable"]
            )

            # Proceso de conciliacion
            (lineasDeuda + lineasPago + lineasConciliacion).reconcile()

    def generar_historico(self):
        for record in self:
            # Iteramos por todas las facturas registradas en el recibo
            historico_facturas = []
            for invoice in record.invoice_ids:
                payment_amount_repartition = invoice.payment_amount_repartition
                if not payment_amount_repartition:
                    if invoice.invoice_payments_widget and invoice.invoice_payments_widget.get("content"):
                        for invoice_payment in invoice.invoice_payments_widget.get("content"):
                            payment_move_id = invoice.browse(invoice_payment.get("move_id"))
                            if payment_move_id in record.payment_ids.move_id:
                                payment_amount_repartition += invoice_payment.get("amount", 0)
                am = self.env["grupo_account_am"].create(
                    {
                        "account_move_id": invoice.id,
                        "payment_group_id": record.id,
                        "amount_residual_history": invoice.amount_residual,
                        "payment_amount_repartition": payment_amount_repartition,
                    }
                )
                historico_facturas.append(am.id)

                # A todas las facturas, le agregamos el payment_amount_repartition como amount_residual
                invoice.payment_amount_repartition = 0

            # Actualizamos el campo Many2many con los nuevos registros
            record.paid_invoices.unlink()
            record.paid_invoices = [(6, 0, historico_facturas)]

    def button_cancelar(self):
        """
        154821: Al cancelar un grupo de pago, se deben cancelar los pagos asociados y los asientos de repartición.
        """
        for payment in self.payment_ids:
            payment.move_id.button_draft()
            payment.move_id.button_cancel()

        repartition_move_ids = self.repartition_move_ids.search([("origin_grupo_account_payment_id", "=", self.id)])
        for repartition_move_id in repartition_move_ids:
            for repartition_move_line_id in repartition_move_id.line_ids:
                if repartition_move_line_id.payment_repartition_origin_invoice_id:
                    repartition_move_line_id.remove_move_reconcile()
            repartition_move_id.button_cancel()

        if self.writeOffMove_id:
            self.writeOffMove_id.button_draft()
            self.writeOffMove_id.unlink()

        self.write({"state": "cancel"})

    def button_draft(self):
        for i in self.payment_ids:
            i.action_draft()
        self.write({"state": "draft"})

    def asigna_nombre(self):
        for i in self:
            if (self.name and self.name == "Borrador") or not self.name:
                new_name = i.genera_secuencia()
                if i.name != new_name:
                    i.name = new_name

    def write(self, vals):
        # for i in self:
        #     if vals.get('state') and vals.get('state') == 'done':
        #         i.asigna_nombre()
        #     return super(PaymentGroup, i).write(vals)
        result = super(PaymentGroup, self).write(vals)
        for this in self:
            if this.state == "done":
                this.asigna_nombre()
        return result

    # @api.model
    # def create(self, vals):
    #     flag = True
    #     if vals.get('payment_type') == 'inbound':
    #         if not flag:
    #             raise exceptions.ValidationError(
    #                 ('No tiene permisos para registrar recibos'))
    #     if vals.get('payment_type') == 'outbound':
    #         if not flag:
    #             raise exceptions.ValidationError(
    #                 ('No tiene permisos para registrar ordenes de pago'))
    #     if not vals.get('payment_type'):
    #         raise exceptions.ValidationError(
    #             ('Tipo de pago no definido. Contacte con su administrador'))
    #     return super(PaymentGroup, self).create(vals)

    @api.model
    def create(self, vals):
        result = super(PaymentGroup, self).create(vals)
        for this in result:

            # TODO: Revisar este flag, tal vez debe ser una validación.
            flag = True

            if this.payment_type == "inbound":
                if not flag:
                    raise exceptions.ValidationError(("No tiene permisos para registrar recibos"))

            if this.payment_type == "outbound":
                if not flag:
                    raise exceptions.ValidationError(("No tiene permisos para registrar ordenes de pago"))

            if not this.payment_type:
                raise exceptions.ValidationError(("Tipo de pago no definido. Contacte con su administrador"))

        return result

    def amount_to_text_esp(self, amount):
        convert_amount_in_words = self.env["interfaces_tools.tools"].numero_a_letra(amount)
        return convert_amount_in_words

    # ------ condiciones
    @api.depends("payment_type")
    def _compute_invoice_type(self):
        for record in self:
            record.invoice_type = "out_invoice" if record.payment_type == "inbound" else "in_invoice"
