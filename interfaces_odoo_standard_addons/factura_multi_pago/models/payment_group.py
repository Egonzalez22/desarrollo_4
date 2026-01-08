from odoo import fields, api, models
from odoo.exceptions import ValidationError


class PaymentGroup(models.Model):
    _name = 'factura_multi_pago.payment_group'
    _order = 'fecha DESC'

    name = fields.Char('Número', default='Borrador')
    fecha = fields.Date(string='Fecha', default=lambda self: fields.Date.today(), required=True)
    state = fields.Selection(
        string='Estado',
        selection=[
            ('draft', 'Borrador'),
            ('done', 'Confirmado'),
            ('cancel', 'Cancelado'),
        ],
        default='draft',
        track_visibility='onchange',
    )
    tipo = fields.Selection(
        string='Tipo',
        selection=[
            ('cliente', 'Cliente'),
            ('proveedor', 'Proveedor'),
        ],
        default='cliente',
    )
    partner_id = fields.Many2one('res.partner', string='Empresa', required=True)
    payment_ids = fields.One2many('account.payment', 'payment_group_id', string='Líneas de pago')
    currency_id = fields.Many2one(
        'res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)
    amount_total = fields.Monetary(string='Total de pagos', compute='compute_total', default=0)
    total_confirmado = fields.Monetary(string='Total confirmado', compute='compute_total_confirmado')
    saldo_total = fields.Monetary(string='Saldo total', compute='compute_saldo_total')
    memo = fields.Char(string="Memo")
    invoice_ids = fields.Many2many('account.move', 'invoice_invoice_ids', compute='compute_invoice_ids', string='Facturas')
    group_line_ids = fields.One2many('factura_multi_pago.payment_group_line', 'payment_group_id', string='Líneas de grupo de pago')
    payment_group_distribution_ids = fields.One2many('factura_multi_pago.payment_group_distribution', 'payment_group_id', string='Distribución de pago')
    payment_ids = fields.One2many('account.payment', 'payment_group_id', string='Líneas de pago generadas')
    has_draft_lines = fields.Boolean(compute='compute_has_draft_lines')
    has_done_lines = fields.Boolean(compute='compute_has_done_lines')
    is_valid = fields.Boolean(compute='compute_is_valid')
    error_msg = fields.Text(string='Error:', compute='compute_error_msg')

    @api.depends('payment_group_distribution_ids')
    def compute_error_msg(self):
        for rec in self:
            error_msg = ''
            for dist in rec.payment_group_distribution_ids:
                if not dist.is_valid:
                    error_msg = dist.error_msg
            rec.error_msg = error_msg

    @api.depends('payment_group_distribution_ids')
    def compute_is_valid(self):
        for rec in self:
            is_valid = True
            for dist in rec.payment_group_distribution_ids:
                if not dist.is_valid:
                    is_valid = False
            rec.is_valid = is_valid

    def compute_has_draft_lines(self):
        for rec in self:
            has_draft_lines = False
            for dist in rec.payment_group_distribution_ids:
                if not dist.done:
                    has_draft_lines = True
            rec.has_draft_lines = has_draft_lines

    def compute_has_done_lines(self):
        for rec in self:
            has_done_lines = False
            for dist in rec.payment_group_distribution_ids:
                if dist.done:
                    has_done_lines = True
            rec.has_done_lines = has_done_lines

    def compute_total(self):
        for rec in self:
            amount = 0
            for group_line in rec.group_line_ids:
                amount += group_line.amount
            self.amount_total = amount

    def compute_saldo_total(self):
        for rec in self:
            amount = 0
            total = 0
            saldo_total = 0
            for group_line in rec.group_line_ids:
                amount += group_line.amount

                dists = self.env['factura_multi_pago.payment_group_distribution'].search([('payment_group_line_id', '=', group_line.id)])
                for dist in dists:
                    total += dist.amount

            rec.saldo_total = amount - total

    @api.depends('amount_total', 'saldo_total')
    def compute_total_confirmado(self):
        for rec in self:
            rec.total_confirmado = rec.amount_total - rec.saldo_total

    def compute_invoice_ids(self):
        for rec in self:
            invoice_ids = []
            for dist in rec.payment_group_distribution_ids:
                invoice_ids.append(dist.account_move_id.id)
            rec.invoice_ids = invoice_ids

    def button_confirmar(self):
        for i in self:
            facturas_contado = False
            facturas_credito = False
            for fac in i.invoice_ids:
                if fac.tipo_factura == 'contado':
                    facturas_contado = True
                else:
                    facturas_credito = True
            if facturas_contado and facturas_credito:
                raise ValidationError('No puede pagar en un mismo recibo facturas al Contado y facturas a Crédito.')

            if not i.partner_id.property_account_receivable_id:
                i.partner_id.property_account_receivable_id = i.partner_id.parent_id.property_account_receivable_id
            if not i.partner_id.property_account_payable_id:
                i.partner_id.property_account_payable_id = i.partner_id.parent_id.property_account_payable_id

            """
            payment_ids = []
            for l in i.group_line_ids:
                payment = self.env['account.payment'].create({
                    'tipo_pago': 'TCredito',
                    'amount': l.amount,
                    'bank_id': l.bank_id,
                    'nro_documento': l.nro_documento,
                    'nro_cheque': l.nro_documento,
                    'fecha_cheque': l.fecha_cheque,
                    'fecha_vencimiento_cheque': l.fecha_venc_cheque,
                })
                payment_ids.append(payment.id)
            i.payment_ids = payment_ids

            for j in i.payment_ids:
                #j.post()
                if j.payment_type == 'inbound':
                    movimiento = j.line_ids.filtered(
                        lambda z: z.debit > 0)
                elif j.payment_type == 'outbound':
                    movimiento = j.line_ids.filtered(
                        lambda z: z.credit > 0)
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
                    x.write({'ref': referencia})
            """

            i.payments_create()

            """
            for inv in i.invoice_ids.sorted(key=lambda x: x.invoice_date_due):
                for payment in i.payment_ids:
                    for ml in payment.line_ids:
                        #inv.register_payment(ml)
                for nc in i.refund_ids:
                    for inv in i.invoice_ids.filtered(lambda x: x.residual > 0):
                        for aml in nc.move_id.line_ids.filtered(lambda x: x.account_id.user_type_id.type in ['payable',
                                                                                                             'receivable'] and not x.reconciled):
                            inv.register_payment(aml)
            """
            i.write({'state': 'done'})

    def button_cancelar(self):
        for i in self.payment_ids:
            i.action_cancel()
        for i in self.payment_group_distribution_ids:
            i.done_manual = False
        self.write({'state': 'cancel'})

    def button_draft(self):
        #for i in self.invoice_ids:
        #    i.action_draft()
        self.write({'state': 'draft'})

    def payments_create(self):
        for dist in self.payment_group_distribution_ids.filtered(lambda dist: not dist.done):
            dist.payment_group_line_id
            active_ids = [dist.account_move_id.id]

            cliente = self.env['res.partner'].search([('id','=', self.partner_id.id)])
            ctx = dict(
                active_ids=active_ids, # Use ids and not id (it has to be a list)
                active_model='account.move',
            )
            payment_type = 'inbound'
            partner_type = 'customer'
            if 'out' in dist.account_move_id.move_type:
                payment_type = 'outbound'
                partner_type = 'supplier'
            values = {
                'payment_type': payment_type,
                'partner_type': partner_type,
                'partner_id': self.partner_id.id,
                'payment_method_line_id': self.env['account.payment.method.line'].search([])[0].id,
                'amount': dist.amount,
                'payment_date': self.fecha,
                'currency_id': self.currency_id.id,
                'journal_id': dist.payment_group_line_id.journal_id.id,
            }
            wizard = self.env['account.payment.register'].with_context(ctx).create(values)

            custom_data = {
                'tipo_pago': dist.payment_group_line_id.tipo_pago,
                'journal_id': dist.payment_group_line_id.journal_id,
                'bank_id': dist.payment_group_line_id.bank_id,
                'nro_documento': dist.payment_group_line_id.nro_documento,
                'nro_cheque': dist.payment_group_line_id.nro_cheque,
                'fecha_cheque': dist.payment_group_line_id.fecha_cheque,
                'fecha_vencimiento_cheque': dist.payment_group_line_id.fecha_venc_cheque,
            }
            payments = wizard._create_payments(custom_data)
            for payment in payments:
                payment.payment_group_id = self.id
            self.payment_ids = self.env['account.payment'].search([('payment_group_id', '=', self.id)])
            dist.done_manual = True


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payments(self, custom_data=None):
        self.ensure_one()
        batches = self._get_batches()
        first_batch_result = batches[0]
        edit_mode = self.can_edit_wizard and (len(first_batch_result['lines']) == 1 or self.group_payment)
        to_process = []

        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard(first_batch_result)
            to_process.append({
                'create_vals': payment_vals,
                'to_reconcile': first_batch_result['lines'],
                'batch': first_batch_result,
            })
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'payment_values': {
                                **batch_result['payment_values'],
                                'payment_type': 'inbound' if line.balance > 0 else 'outbound'
                            },
                            'lines': line,
                        })
                batches = new_batches

            for batch_result in batches:
                to_process.append({
                    'create_vals': self._create_payment_vals_from_batch(batch_result),
                    'to_reconcile': batch_result['lines'],
                    'batch': batch_result,
                })

        if custom_data:
            for vals in to_process:
                vals['create_vals']['tipo_pago'] = custom_data['tipo_pago']
                vals['create_vals']['bank_id'] = custom_data['bank_id']
                vals['create_vals']['nro_documento'] = custom_data['nro_documento']
                vals['create_vals']['nro_cheque'] = custom_data['nro_cheque']
                vals['create_vals']['fecha_cheque'] = custom_data['fecha_cheque']
                vals['create_vals']['fecha_vencimiento_cheque'] = custom_data['fecha_vencimiento_cheque']

        payments = self._init_payments(to_process, edit_mode=edit_mode)
        self._post_payments(to_process, edit_mode=edit_mode)
        self._reconcile_payments(to_process, edit_mode=edit_mode)
        return payments


class PaymentGroupLine(models.Model):
    _name = 'factura_multi_pago.payment_group_line'
    _rec_name = 'id'

    payment_group_id = fields.Many2one('factura_multi_pago.payment_group', string='Empresa', readonly=True)
    amount = fields.Monetary(string='Monto')
    currency_id = fields.Many2one(
        'res.currency', string='Moneda', default=lambda self: self.env.company.currency_id)
    tipo_pago = fields.Selection(string='Tipo de pago', selection=[('Efectivo', 'Efectivo'), ('Cheque', 'Cheque'),
                                                                   ('TCredito', 'Tarjeta de crédito'),
                                                                   ('TDebito', 'Tarjeta de débito'),
                                                                   ('Transferencia', 'Transferencia / Depósito'),
                                                                   ('Retencion', 'Retención'), ('Otros', 'Otros')])
    journal_id = fields.Many2one('account.journal', string='Diario')
    bank_id = fields.Many2one('res.bank', string='Banco')
    nro_documento = fields.Char(string='Nro. de documento')
    nro_cheque = fields.Char(string='Nro. cheque')
    fecha_cheque = fields.Date(string='Fecha del cheque')
    fecha_venc_cheque = fields.Date(string='Fecha de vencimiento del cheque')
    saldo_total = fields.Monetary(string='Saldo total', compute='compute_saldo_total')

    def compute_saldo_total(self):
        for rec in self:
            dists = self.env['factura_multi_pago.payment_group_distribution'].search([('payment_group_line_id', '=', rec.id)])
            total = 0
            for dist in dists:
                total += dist.amount
            rec.saldo_total = rec.amount - total

    def name_get(self):
        return [(record.id, f'{record.id} ({record.amount})') for record in self]


class PaymentGroupDistribution(models.Model):
    _name = 'factura_multi_pago.payment_group_distribution'

    payment_group_id = fields.Many2one('factura_multi_pago.payment_group', string='Grupo de pago')
    payment_group_line_id = fields.Many2one('factura_multi_pago.payment_group_line', string='Línea de grupo de pago', required=True)
    account_move_id = fields.Many2one('account.move', string='Factura', required=True)
    account_move_line_id = fields.Many2one('account.move.line', string='Línea de factura')
    currency_id = fields.Many2one('res.currency', string='Moneda')
    amount = fields.Monetary(string='Monto', required=True)
    total_factura = fields.Monetary(string='Total factura', compute='compute_total_factura')
    total_pendiente = fields.Monetary(string='Pendiente', compute='compute_total_pendiente')
    done_manual = fields.Boolean(string='Confirmado', default=False)
    done = fields.Boolean(string='Confirmado', compute='compute_done')
    is_valid = fields.Boolean(string='Válido', compute='compute_is_valid')
    error_msg = fields.Text(string='Error')

    @api.depends('done_manual')
    def compute_done(self):
        for rec in self:
            rec.done = rec.done_manual
            if not rec.account_move_id.amount_residual:
                rec.done = True

    def compute_total_factura(self):
        for rec in self:
            total_factura = 0
            if rec.account_move_id:
                total_factura = rec.account_move_id.amount_total
            rec.total_factura = total_factura

    def compute_total_pendiente(self):
        for rec in self:
            total_pendiente = 0
            if rec.account_move_id:
                total_pendiente = rec.account_move_id.amount_residual
            rec.total_pendiente = total_pendiente

    @api.onchange('account_move_id')
    def set_values_to(self):
        if self.account_move_id:
            ids = self.env['account.move.line'].search([('move_id', '=', self.account_move_id.id)])
            return {
                'domain': {'account_move_line_id': [('id', 'in', ids.ids)],}

            }

    @api.depends('amount', 'done')
    def compute_is_valid(self):
        currencies = []
        for rec in self:
            currency_id = rec.account_move_id.currency_id.id
            if currency_id not in currencies:
                currencies.append(currency_id)
            if len(currencies) > 1:
                rec.error_msg = 'Facturas con múltiples monedas'
                rec.is_valid = False
                continue

            if rec.done:
                rec.is_valid = True
                continue

            total_group_payment_amount = rec.payment_group_line_id.amount
            total_distribution_amount = 0
            payments = self.env['factura_multi_pago.payment_group_distribution'].search([
                ('payment_group_line_id', '=', rec.payment_group_line_id.id),
                #('done', '=', False),
            ])
            for payment in payments:
                if payment.done:
                    continue
                total_distribution_amount += payment.amount
            if total_distribution_amount > total_group_payment_amount:
                rec.error_msg = f'Distribución supera monto de línea de pago {rec.payment_group_line_id.id}'
                rec.is_valid = False
                continue

            moves_payments = self.env['factura_multi_pago.payment_group_distribution'].search(
                [
                    ('payment_group_id', '=', rec.payment_group_id.id),
                    ('account_move_id', '=', rec.account_move_id.id),
                ]
            )
            moves_pamount = 0
            for payment in moves_payments:
                if payment.done:
                    continue
                moves_pamount += payment.amount
            if moves_pamount > rec.account_move_id.amount_residual:
                rec.error_msg = f'Distribución supera pago pendiente en factura {rec.account_move_id.name}'
                rec.is_valid = False
                continue

            rec.error_msg = ''
            rec.is_valid = True
