from odoo import fields, api, models, exceptions
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    is_repartition_move = fields.Boolean(default=False)
    payment_amount_repartition = fields.Float(string="Monto a Pagar", default=0)
    origin_grupo_account_payment_id = fields.Many2one("grupo_account_payment.payment.group")
    origin_grupo_count = fields.Integer(compute="count_grupo_payments")

    active_payment_group_currency = fields.Many2one("res.currency")
    amount_residual_in_payment_group_currency = fields.Float()

    def _get_amount_residual_in_payment_group_currency(self, payment_type, active_payment_group_currency, fecha=fields.Date.today()):
        for this in self:
            amount_residual_in_payment_group_currency = this.amount_residual
            if not active_payment_group_currency:
                active_payment_group_currency = this.currency_id
            if this.currency_id != active_payment_group_currency:
                amount_residual_in_payment_group_currency = this.currency_id._convert(
                    this.amount_residual,
                    active_payment_group_currency,
                    this.company_id,
                    fecha,
                )
            if this.active_payment_group_currency != active_payment_group_currency:
                this.active_payment_group_currency = active_payment_group_currency
            if this.amount_residual_in_payment_group_currency != amount_residual_in_payment_group_currency:
                this.amount_residual_in_payment_group_currency = amount_residual_in_payment_group_currency

    def count_grupo_payments(self):
        for record in self:
            pay_group = self.env["grupo_account_payment.payment.group"].search(
                [
                    ("invoice_ids", "in", record.ids),
                    ("state", "not in", ["draft", "cancel"]),
                ]
            )
            record.origin_grupo_count = len(pay_group.ids)

    def action_view_group_payments(self):
        self.ensure_one()
        pay_group = self.env["grupo_account_payment.payment.group"].search([("invoice_ids", "in", self.ids)])
        return {
            "name": "Pagos",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "grupo_account_payment.payment.group",
            "domain": [("id", "in", pay_group.ids)],
        }

    @api.depends("amount_residual", "move_type", "state", "company_id")
    def _compute_payment_state(self):
        res = super(AccountMove, self)._compute_payment_state()
        for record in self.filtered(lambda x: x.state == "posted"):
            if record.move_type in ["in_invoice", "out_invoice"]:
                query = """
                    SELECT id FROM account_payment WHERE payment_group_id IN (
                    SELECT grupo_account_payment_payment_group_id FROM account_move_grupo_account_payment_payment_group_rel
                    WHERE account_move_id = %s)
                """
                self.env.cr.execute(query, (record.id,))
                payment_ids = self.env.cr.fetchall()
                if payment_ids:
                    obj_payment_ids = (
                        self.env["account.payment"].browse([x[0] for x in payment_ids]).filtered(lambda x: x.state == "posted")
                    )
                    ###
                    # si la cuenta es igual se marca como paid, de contrario se marca como en in_payment
                    # va con cuenta transitoria
                    check_pay_method = []
                    if record.move_type == "in_invoice":
                        # para clientes
                        # revisamos si las cuentas son iguales en los metodos de pagos
                        for payment in obj_payment_ids:
                            for method in payment.journal_id.outbound_payment_method_line_ids:
                                if method.payment_account_id == payment.journal_id.default_account_id:
                                    check_pay_method.append(payment)

                    if record.move_type == "out_invoice":
                        # para proveedores
                        # revisamos si las cuentas son iguales en los metodos de pagos
                        for payment in obj_payment_ids:
                            for method in payment.journal_id.inbound_payment_method_line_ids:
                                if method.payment_account_id == payment.journal_id.default_account_id:
                                    check_pay_method.append(payment)
                    ###
                    if not check_pay_method:  # si no son iguales se procede por cuenta transitoria
                        if all([x.reconciled_statement_line_ids for x in obj_payment_ids]):
                            if record.amount_residual == 0:
                                record.payment_state = "paid"
                        else:
                            if record.amount_residual == 0:
                                record.payment_state = "in_payment"

            # revisamos si la factura tiene un grupo de pagos asociado
            if record.origin_grupo_account_payment_id:
                rec_group = record.origin_grupo_account_payment_id
                for invoice in rec_group.invoice_ids:
                    query = """
                        SELECT id FROM account_payment WHERE payment_group_id IN (
                        SELECT grupo_account_payment_payment_group_id FROM account_move_grupo_account_payment_payment_group_rel
                        WHERE account_move_id = %s)
                    """
                    self.env.cr.execute(query, (invoice.id,))
                    payment_ids = self.env.cr.fetchall()
                    if payment_ids:
                        obj_payment_ids = (
                            self.env["account.payment"].browse([x[0] for x in payment_ids]).filtered(lambda x: x.state == "posted")
                        )

                        ###
                        # si la cuenta es igual se marca como paid, de contrario se marca como en in_payment
                        # va con cuenta transitoria
                        check_pay_method = []
                        if invoice.move_type == "in_invoice":
                            # para clientes
                            # revisamos si las cuentas son iguales en los metodos de pagos
                            for payment in obj_payment_ids:
                                for method in payment.journal_id.outbound_payment_method_line_ids:
                                    if method.payment_account_id == payment.journal_id.default_account_id:
                                        check_pay_method.append(payment)

                        if invoice.move_type == "out_invoice":
                            # para proveedores
                            # revisamos si las cuentas son iguales en los metodos de pagos
                            for payment in obj_payment_ids:
                                for method in payment.journal_id.inbound_payment_method_line_ids:
                                    if method.payment_account_id == payment.journal_id.default_account_id:
                                        check_pay_method.append(payment)
                        ###
                        if not check_pay_method:  # si no son iguales se procede por cuenta transitoria
                            if all([x.reconciled_statement_line_ids for x in obj_payment_ids]):
                                if invoice.amount_residual == 0:
                                    invoice.payment_state = "paid"
                            else:
                                if invoice.amount_residual == 0:
                                    invoice.payment_state = "in_payment"
        return res

    def button_pago(self):
        # Facturas del tipo out_invoice
        if self.type == "out_invoice":
            flag = self.env.user.has_group("grupo_account_payment.grupo_cobrador")

            if flag:
                view = self.env.ref("grupo_account_payment.grupo_account_payment_form_view")
                return {
                    "name": "Registrar pago",
                    "type": "ir.actions.act_window",
                    "view_type": "form",
                    "view_mode": "form",
                    "res_model": "grupo_account_payment.payment.group",
                    "views": [(view.id, "form")],
                    "view_id": view.id,
                    # 'target': 'new',
                    "context": {
                        "default_payment_type": "inbound",
                        "default_partner_id": self.partner_id.id,
                        "default_invoice_ids": self.ids,
                    },
                }
            else:
                raise UserError("Su usuario no cuenta con permisos para registrar pagos")

        # Facturas del tipo in_invoice
        elif self.type == "in_invoice":
            flag = self.env["res.users"].has_group("grupo_account_payment.grupo_orden_pago")
            if flag:
                view = self.env.ref("grupo_account_payment.grupo_account_payment_orden_form_view")
                return {
                    "name": "Registrar pago",
                    "type": "ir.actions.act_window",
                    "view_type": "form",
                    "view_mode": "form",
                    "res_model": "grupo_account_payment.payment.group",
                    "views": [(view.id, "form")],
                    "view_id": view.id,
                    # 'target': 'new',
                    "context": {
                        "default_payment_type": "outbound",
                        "default_partner_id": self.partner_id.id,
                        "default_invoice_ids": [(4, self.id, 0)],
                    },
                }
            else:
                raise UserError("Su usuario no cuenta con permisos para registrar órdenes de pago")

    @api.model
    def button_pago_multi(self, facturas):
        if facturas[0].type == "out_invoice":
            flag = self.env.user.has_group("grupo_account_payment.grupo_cobrador")
            if flag:
                view = self.env.ref("grupo_account_payment.grupo_account_payment_form_view")
                return {
                    "name": "Registrar pago",
                    "type": "ir.actions.act_window",
                    "view_type": "form",
                    "view_mode": "form",
                    "res_model": "grupo_account_payment.payment.group",
                    "views": [(view.id, "form")],
                    "view_id": view.id,
                    # 'target': 'new',
                    "context": {
                        "default_payment_type": "inbound",
                        "default_partner_id": facturas[0].partner_id.id,
                        "default_invoice_ids": [(6, 0, facturas.ids)],
                    },
                }
            else:
                raise UserError("Su usuario no cuenta con permisos para registrar pagos")

        elif facturas[0].type == "in_invoice":
            flag = self.env.user.has_group("grupo_account_payment.grupo_orden_pago")
            if flag:
                view = self.env.ref("grupo_account_payment.grupo_account_payment_orden_form_view")
                return {
                    "name": "Registrar pago",
                    "type": "ir.actions.act_window",
                    "view_type": "form",
                    "view_mode": "form",
                    "res_model": "grupo_account_payment.payment.group",
                    "views": [(view.id, "form")],
                    "view_id": view.id,
                    # 'target': 'new',
                    "context": {
                        "default_payment_type": "outbound",
                        "default_partner_id": self.partner_id.id,
                        "default_invoice_ids": [(6, 0, facturas.ids)],
                    },
                }
            else:
                raise UserError("Su usuario no cuenta con permisos para registrar ordenes de pago")

    def action_register_payment(self):
        if not self.ids:
            raise UserError("No se seleccionaron facturas.")

        partner_ids = self.mapped("partner_id")
        while True:
            break_loop = True
            for partner_id in partner_ids:
                if partner_id.parent_id and not partner_id.parent_id in partner_ids:
                    partner_ids |= partner_id.parent_id
                    break_loop = False
            if break_loop:
                break

        partner_ids = partner_ids.filtered(lambda x: not x.parent_id)

        if len(partner_ids) > 1:
            raise UserError("No puede seleccionar facturas de diferentes clientes.")

        invalid_state_invoices = self.filtered(lambda inv: inv.payment_state not in ("not_paid", "partial"))
        if invalid_state_invoices:
            raise UserError("Solo se pueden seleccionar facturas no pagadas o parcialmente pagadas.")

        invalid_state = self.filtered(lambda inv: inv.state not in ("posted"))
        if invalid_state:
            raise UserError("Solo se pueden seleccionar facturas en estado publicado.")

        move_type = list(set(self.mapped("move_type")))

        if len(move_type) > 1:
            raise UserError("Todas las facturas seleccionadas deben ser del mismo tipo.")

        move_type = move_type[0]

        context = {
            "default_payment_type": ("inbound" if move_type == "out_invoice" else "outbound"),
            "default_partner_type": ("customer" if move_type == "out_invoice" else "supplier"),
            "default_partner_id": partner_ids.id,
            # 'default_invoice_ids': [(6, 0, self.ids)],
            "default_invoice_ids": self.ids,
            "default_currency_id": self[0].currency_id.id,
            "default_move_journal_types": ("bank", "cash"),
            "search_default_company_id": self.env.user.company_id.id,
            "search_default_child_of_company_id": [self.env.user.company_id.id]
            + [child.id for child in self.env.user.company_id.child_ids],
        }
        if self[0].move_type == "out_invoice":
            context["search_default_inbound_filter"] = 1
        elif self[0].move_type == "in_invoice":
            context["search_default_outbound_filter"] = 1

        view_id = self.env.ref("grupo_account_payment.account_payment_form_view").id
        action = {
            "name": "Registrar Pago",
            "view_mode": "form",
            "view_id": view_id,
            "res_model": "grupo_account_payment.payment.group",
            "type": "ir.actions.act_window",
            "context": context,
            "target": "current",
        }

        return action
