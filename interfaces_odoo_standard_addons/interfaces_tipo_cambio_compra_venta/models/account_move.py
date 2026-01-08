from odoo import api, fields, models, _, exceptions, release


class AccountMove(models.Model):
    _inherit = "account.move"

    currency_rate = fields.Float(string="Tipo de Cambio")
    freeze_currency_rate = fields.Boolean(string="Congelar Tipo de Cambio", default=False)
    count_invoice_line_ids = fields.Integer(compute="_get_count_invoice_line_ids")

    @api.onchange("invoice_line_ids", "line_ids")
    def _get_count_invoice_line_ids(self):
        # interfaces_tipo_cambio_compra_venta/models/account_move.py
        for this in self:
            this.count_invoice_line_ids = len(this.invoice_line_ids)

    @api.onchange("currency_id", "invoice_date", "date")
    def get_tipo_cambio_default(self):
        # interfaces_tipo_cambio_compra_venta/models/account_move.py
        for this in self:
            if this.freeze_currency_rate:
                continue
            currency_rate = 1
            if this.currency_id:
                _get_conversion_rate = this.currency_id._get_conversion_rate
                if this.move_type in ["out_invoice", "out_refund", "in_invoice", "in_refund"]:
                    if this.move_type in ["out_invoice", "out_refund"]:
                        _get_conversion_rate = this.currency_id._get_conversion_rate_tipo_cambio_comprador
                    elif this.move_type in ["in_invoice", "in_refund"]:
                        _get_conversion_rate = this.currency_id._get_conversion_rate_tipo_cambio_vendedor
                currency_rate = _get_conversion_rate(
                    this.currency_id, this.company_id.currency_id, this.company_id, (this.invoice_date or this.date or fields.date.today())
                )
            if this.currency_rate != currency_rate:
                this.currency_rate = currency_rate

    @api.onchange("date", "currency_id", "currency_rate")
    def _onchange_currency(self):
        # interfaces_tipo_cambio_compra_venta/models/account_move.py
        self.get_tipo_cambio_default()
        if release.major_version in ["16.0"]:
            for this in self:
                for line in this.invoice_line_ids:
                    if this.currency_rate and line.currency_rate != 1 / this.currency_rate:
                        line.with_context(check_move_validity=False).currency_rate = 1 / this.currency_rate
                    line.with_context(check_move_validity=False).balance = line.company_id.currency_id.round(
                        line.amount_currency / line.currency_rate
                    )
        if release.major_version in ["15.0"]:
            result = True
            for this in self.filtered(lambda x: x.state not in ["posted", "cancel"]):
                result = super(AccountMove, this)._onchange_currency()
            return result

    @api.onchange("currency_id")
    def _onchange_currency_with_invoice_lines(self):
        # interfaces_tipo_cambio_compra_venta/models/account_move.py
        if self.invoice_line_ids:
            raise exceptions.ValidationError(_("No es posible cambiar de moneda cuando la factura contiene líneas"))

    @api.onchange("freeze_currency_rate")
    def _onchange_freeze_currency_rate(self):
        # interfaces_tipo_cambio_compra_venta/models/account_move.py
        if not self.freeze_currency_rate:
            self._onchange_currency()

    def action_register_payment(self):
        # interfaces_tipo_cambio_compra_venta/models/account_move.py
        result = super(AccountMove, self).action_register_payment()
        context = result.get("context") or {}

        # Si hay mas de un pago seleccionado, omitimos el currency
        if context and context.get("active_ids") and len(context.get("active_ids")) == 1:
            context.update(
                {
                    "default_freeze_currency_rate": self.freeze_currency_rate,
                    "default_currency_rate": self.currency_rate,
                }
            )
            result["context"] = context

        return result

    def _autopost_draft_entries(self):
        # interfaces_tipo_cambio_compra_venta/models/account_move.py
        moves = self.search(
            [
                ("state", "=", "draft"),
                ("date", "<=", fields.Date.context_today(self)),
                ("auto_post", "!=", "no"),
                ("to_check", "=", False),
            ],
            limit=100,
        )
        for move in moves:
            move._onchange_currency()
        return super(AccountMove, self)._autopost_draft_entries()

    @api.model
    def create(self, vals):
        result = super(AccountMove, self).create(vals)
        for this in result:
            if (
                (this.sale_order_count or this.purchase_order_count)
                and this.state in ["draft"]
                and this.line_ids
                and this.move_type in ["out_invoice", "in_invoice"]
            ):
                this._onchange_currency()
        return result

    def _compute_payments_widget_to_reconcile_info(self):
        # interfaces_tipo_cambio_compra_venta/models/account_move.py
        super(AccountMove, self)._compute_payments_widget_to_reconcile_info()
        for move in self:
            move.invoice_outstanding_credits_debits_widget = False
            move.invoice_has_outstanding = False

            if move.state != "posted" or move.payment_state not in ("not_paid", "partial") or not move.is_invoice(include_receipts=True):
                continue

            pay_term_lines = move.line_ids.filtered(lambda line: line.account_id.account_type in ("asset_receivable", "liability_payable"))

            domain = [
                ("account_id", "in", pay_term_lines.account_id.ids),
                ("parent_state", "=", "posted"),
                ("partner_id", "=", move.commercial_partner_id.id),
                ("reconciled", "=", False),
                "|",
                ("amount_residual", "!=", 0.0),
                ("amount_residual_currency", "!=", 0.0),
            ]

            payments_widget_vals = {"outstanding": True, "content": [], "move_id": move.id}

            if move.is_inbound():
                domain.append(("balance", "<", 0.0))
                payments_widget_vals["title"] = _("Outstanding credits")
            else:
                domain.append(("balance", ">", 0.0))
                payments_widget_vals["title"] = _("Outstanding debits")

            for line in self.env["account.move.line"].search(domain):

                if line.currency_id == move.currency_id:
                    # Same foreign currency.
                    amount = abs(line.amount_residual_currency)
                else:
                    # Different foreign currencies.

                    if line.move_id.payment_id:
                        if line.move_id.payment_id.freeze_currency_rate:
                            amount = line.company_currency_id._convert_tipo_cambio_vendedor(
                                abs(line.amount_residual),
                                move.currency_id,
                                move.company_id,
                                line.date,
                                force_rate=line.move_id.payment_id.currency_rate,
                            )
                        elif line.move_id.payment_id.payment_type == "inbound":
                            amount = line.company_currency_id._convert_tipo_cambio_comprador(
                                abs(line.amount_residual),
                                move.currency_id,
                                move.company_id,
                                line.date,
                            )
                        elif line.move_id.payment_id.payment_type == "outbound":
                            amount = line.company_currency_id._convert_tipo_cambio_vendedor(
                                abs(line.amount_residual),
                                move.currency_id,
                                move.company_id,
                                line.date,
                            )
                    else:
                        amount = line.company_currency_id._convert(
                            abs(line.amount_residual),
                            move.currency_id,
                            move.company_id,
                            line.date,
                        )

                if move.currency_id.is_zero(amount):
                    continue

                payments_widget_vals["content"].append(
                    {
                        "journal_name": line.ref or line.move_id.name,
                        "amount": amount,
                        "currency_id": move.currency_id.id,
                        "id": line.id,
                        "move_id": line.move_id.id,
                        "date": fields.Date.to_string(line.date),
                        "account_payment_id": line.payment_id.id,
                    }
                )

            if not payments_widget_vals["content"]:
                continue

            move.invoice_outstanding_credits_debits_widget = payments_widget_vals
            move.invoice_has_outstanding = True
