from odoo import fields, api, models, exceptions
from datetime import datetime


class AccountCajaSession(models.Model):
    _name = 'account.caja.session'
    _order = 'id desc'

    name = fields.Char(string="Número", required=True,
                       default='Nuevo', readonly=True)
    statement_ids = fields.Many2many(
        'account.bank.statement', string="Extractos")
    fecha_hora_inicio = fields.Datetime(
        'Fecha/hora inicio', default=lambda x: datetime.now())
    fecha_hora_fin = fields.Datetime('Fecha/hora fin')
    user_id = fields.Many2one(
        'res.users', string="Cajero", required=True, default=lambda self: self.env.user)
    state = fields.Selection(string="Estado", selection=[('apertura', 'Apertura'), (
        'proceso', 'En proceso'), ('cierre', 'Cierre'), ('done', 'Cerrada y contabilizada')], default='apertura')
    caja_id = fields.Many2one('account.caja', string="Caja", required=True)
    company_id = fields.Many2one(
        'res.company', string="Compañia", default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    
    payment_ids = fields.One2many('account.payment', 'caja_session_id', string="Pagos")


    # st_efectivo = fields.Many2one(
    #    'account.bank.statement', string="Diario de efectivo", compute="compute_st_efectivo")
    # saldo_apertura = fields.Monetary(
    #    string='Saldo de apertura', related="st_efectivo.balance_start")

    # saldo_teorico_cierre = fields.Monetary(
    #    string='Saldo teórico de cierre', related="st_efectivo.balance_end")
    # saldo_cierre = fields.Monetary(
    #    string='Saldo cierre', related="st_efectivo.balance_end_real")
    # diferencia = fields.Monetary(
    #    string='Diferencia', compute="compute_diferencia")

    # @api.depends('saldo_cierre','st_efectivo.line_ids')
    # @api.onchange('saldo_cierre','st_efectivo.line_ids')
    # def compute_diferencia(self):
    #     for i in self:
    #         i.diferencia=i.balance_end - i.balance_end_real

    # def compute_st_efectivo(self):
    #     for i in self:
    #         for j in i.statement_ids:
    #             if j.journal_id.type == 'cash':
    #                 i.st_efectivo = j

    def open_cashbox_id(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        if context.get('balance'):
            context['statement_id'] = self.st_efectivo.id
            if context['balance'] == 'start':
                cashbox_id = self.st_efectivo.cashbox_start_id.id
            elif context['balance'] == 'close':
                cashbox_id = self.st_efectivo.cashbox_end_id.id
            else:
                cashbox_id = False

            action = {
                'name': 'Control de efectivo',
                'view_mode': 'form',
                'res_model': 'account.bank.statement.cashbox',
                'view_id': self.env.ref('account.view_account_bnk_stmt_cashbox_footer').id,
                'type': 'ir.actions.act_window',
                'res_id': cashbox_id,
                'context': context,
                'target': 'new'
            }
            return action

    def button_iniciar_sesion(self):
        self.write({'state': 'proceso'})

    def button_cerrar_sesion(self):
        if self.env.user == self.user_id or self.env.user.has_group('base.group_system'):
            for i in self.statement_ids:
                #     if (i != self.st_efectivo) and (i.balance_end != i.balance_end_real):
                i.write({'balance_end_real': i.balance_start + i.balance_end})
            self.write(
                {'state': 'cierre', 'fecha_hora_fin': fields.Datetime.now()})
        else:
            raise exceptions.ValidationError(
                'La sesión está asignada a otro usuario')

    def button_validar(self):
        if self.env.user == self.user_id or self.env.user.has_group('base.group_system'):
            for i in self.statement_ids:
                # i.button_post()
                for j in i.line_ids:
                    for x in j.payment_id.move_id.line_ids.filtered(lambda z: z.debit > 0 and not z.reconciled):
                        line_to_change = j.line_ids.filtered(
                            lambda x: x.credit > 0 and not x.reconciled)
                        line_to_change.write({'account_id': x.account_id.id})
                        (x + line_to_change).reconcile()
                # i.button_validate_or_action()
            self.write({'state': 'done'})
            return
        else:
            raise exceptions.ValidationError('La sesión está asignada a otro usuario')

    def validar_caja_abierta(self):
        duplicada = self.env['account.caja.session'].search([
            ('id', 'not in', self.ids),
            ('caja_id', 'in', self.caja_id.ids),
            ('state', '!=', 'done')
        ])
        if duplicada:
            raise exceptions.ValidationError('Ya existe una sesión abierta para esta caja')

    def validar_sesion_unica(self):
        duplicada = self.env['account.caja.session'].search([
            ('id', 'not in', self.ids),
            ('user_id', '=', self.env.user.id),
            ('state', '!=', 'done')
        ])
        if duplicada:
            raise exceptions.ValidationError('Ya existe una sesión abierta para este usuario')

    @api.model
    def create(self, vals_list):
        result = super(AccountCajaSession, self).create(vals_list)
        for this in result:
            caja = this.caja_id
            this.validar_caja_abierta()
            this.validar_sesion_unica()
            this.name = caja.sudo().sequence_id.next_by_id()
            statements = []
            for i in caja.journal_ids:
                st = {
                    'aux_journal_id': i.id,
                    'date': fields.Date.today(),
                    'name': this.name,
                    'company_id': this.env.company.id
                }
                statements.append((0, 0, st))
            this.update({'statement_ids': statements})
        return result
