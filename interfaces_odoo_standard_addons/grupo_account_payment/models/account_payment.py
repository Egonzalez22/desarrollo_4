from odoo import fields, api, models, exceptions


class AccountPayment(models.Model):
    _inherit = "account.payment"

    payment_group_id = fields.Many2one("grupo_account_payment.payment.group", string="Grupo de pago")

    payment_group_invo_count = fields.Integer(string="Cantidad de Facturas", compute="_get_group_invo_count")

    def _get_group_invo_count(self):
        for record in self:
            record.payment_group_invo_count = len(record.payment_group_id.invoice_ids.ids)

    def action_get_payment_group_invo(self):
        # grupo_account_payment/models/account_payment.py
        self.ensure_one()
        return {
            "name": "Facturas",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "domain": [("id", "in", self.payment_group_id.invoice_ids.ids)],
        }

    @api.constrains("nro_cheque")
    def valida_cheque_duplicado(self):
        if self.nro_cheque:
            duplicado = self.env["account.payment"].search(
                [("bank_id", "=", self.bank_id.id), ("nro_cheque", "=", self.nro_cheque), ("id", "!=", self.id)]
            )
            if duplicado:
                raise exceptions.ValidationError("Cheque ya existente: " + self.bank_id.name + " " + self.nro_cheque)
        else:
            return

    @api.depends("payment_group_id")
    def action_post(self):
        # grupo_account_payment/models/account_payment.py
        if not self.payment_group_id and not self.is_internal_transfer and not self._context.get("avoid_payment_group"):
            raise exceptions.ValidationError("No puede crear una linea de pago directamente, por favor vaya a Recibos u Ordenes de Pago.")

        if self.payment_group_id and self.currency_id != self.payment_group_id.currency_id:

            raise exceptions.ValidationError("No se permite la moneda %s para este pago" % self.currency_id.name)

        return super(AccountPayment, self).action_post()

    @api.model
    def create(self, vals):
        # grupo_account_payment/models/account_payment.py
        context = self.env.context
        if "default_diferenciaPagos" in context:
            vals["amount"] = context["default_diferenciaPagos"]
        return super(AccountPayment, self).create(vals)

    @api.depends("journal_id")
    def _compute_currency_id(self):
        # grupo_account_payment/models/account_payment.py
        result = super(AccountPayment, self)._compute_currency_id()
        for this in self:
            if this.payment_group_id:
                this.currency_id = this.payment_group_id.currency_id
        return result
