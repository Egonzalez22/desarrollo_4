from odoo import fields, api, models, exceptions
from datetime import date
import math
import locale


class PaymentGroup(models.Model):
    _name = 'grupo_account_payment.payment.group'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Grupo de pago'
    _order = 'name desc'

    name = fields.Char('Número', default="Borrador",
                       track_visibility='onchange')
    partner_id = fields.Many2one(
        'res.partner', string='Empresa', required=True, track_visibility='onchange')
    payment_ids = fields.One2many(
        'account.payment', 'payment_group_id', string='Lineas de pago', copy="False", track_visibility='onchange')
    fecha = fields.Date(
        string='Fecha', default=date.today(), required=True, track_visibility='onchange')
    user_id = fields.Many2one(
        'res.users', string="Usuario", default=lambda self: self.env.user)
    currency_id = fields.Many2one('res.currency', string='Moneda',
                                  default=lambda self: self.env.user.company_id.currency_id, groups='base.group_multi_currency', track_visibility='onchange')
    company_id = fields.Many2one(
        'res.company', string='Compañia', default=lambda self: self.env.user.company_id, track_visibility='onchange')
    amount_total = fields.Monetary(
        string='Total de pagos', compute='compute_total', default=0, store=True, track_visibility='onchange')
    amount_total_company_signed = fields.Monetary(
        string='Total en moneda de la compañia', default=0, compute='compute_total', store=True)
    payment_type = fields.Selection([
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ], string='Tipo de Pago', required=True)
    memo = fields.Char(string="Referencia", track_visibility='onchange')
    state = fields.Selection(string='Estado', selection=[(
        'draft', 'Borrador'), ('done', 'Confirmado'), ('cancel', 'Cancelado')], default='draft', track_visibility='onchange')
    invoice_ids = fields.Many2many(
        'account.move', string="Facturas", copy="False", track_visibility='onchange')
    amount_total_selected = fields.Monetary(
        string='Total deudas seleccionadas', compute='compute_total', default=0, store=True, track_visibility='onchange')
    cantRecibos = fields.Integer(compute="_cantRecibos")
    nro_recibo_fisico = fields.Char(string="Nro. recibo manual")
    diferenciaPagos = fields.Monetary( string='Diferencia',compute="compute_diferencia")

    paid_invoice_ids = fields.Many2many(
        'account.move', compute="compute_paid_invoices")

    fecha_letras = fields.Char(compute='_fechaLetras')
    partner_type = fields.Selection(
        string='Tipo de Empresa',
        selection=[('customer', 'cliente'), ('supplier', 'proveedor')]
    )
    invoice_type = fields.Char(compute='_compute_invoice_type')
    
    mantenerAbierto = fields.Selection(
        string='Contabilizar Diferencia',
        selection=[('mantener', 'Mantener Abierto'), ('paid', 'Marcar como completamente pagado')], default='mantener'
    )
    
    writeoff_account_id = fields.Many2one(
        string='Contabilizar Diferencia en:',
        comodel_name='account.account',
    )
    writeoff_label = fields.Char(string='Explicación')
    
    ocultar_mantenerAbierto = fields.Boolean(
        string='field_name', compute = 'compute_mantenerAbierto'
    )
    ocultar_writeoff  = fields.Boolean(
        string='field_name', compute = 'compute_ocultar_writeoff'
    )
    writeOffMove_id = fields.Many2one('account.move',string="Asiento de conciliación", copy=False) 
    
    invoice_group_ids = fields.Many2many(
        'account.move', string="Facturas en otros grupos de pago",
        compute='_compute_invoice_group_ids')
    

    @api.depends('invoice_ids')
    def _compute_invoice_group_ids(self):
        for group in self:
            draft_groups = self.env['grupo_account_payment.payment.group'].search([('state', '=', 'draft')])
            invoices_in_draft_groups = draft_groups.mapped('invoice_ids')
            group.invoice_group_ids = invoices_in_draft_groups
            
    def crearAsientoConciliacion(self):
        for record in self:
            lines_ids = []
            if record.payment_type == 'outbound':
                debit = {
                    'account_id': record.partner_id.property_account_payable_id.id,
                    'date': record.fecha,
                    'name': record.writeoff_label,
                    'currency_id': record.currency_id.id,
                    'amount_currency': record.diferenciaPagos,
                    'partner_id': record.partner_id.id,
                }
                lines_ids.append((0, 0, debit))
                credit = {
                    'account_id': record.writeoff_account_id.id,
                    'date': record.fecha,
                    'name': record.writeoff_label,
                    'currency_id': record.currency_id.id,
                    'amount_currency': record.diferenciaPagos * -1,
                }
                lines_ids.append((0, 0, credit))
            elif record.payment_type == 'inbound':
                debit = {
                    'account_id': record.writeoff_account_id.id,
                    'date': record.fecha,
                    'name': record.writeoff_label,
                    'currency_id': record.currency_id.id,
                    'amount_currency': record.diferenciaPagos,
                }
                lines_ids.append((0, 0, debit))
                credit = {
                    'account_id': record.partner_id.property_account_receivable_id.id,
                    'date': record.fecha,
                    'name': record.writeoff_label,
                    'currency_id': record.currency_id.id,
                    'partner_id': record.partner_id.id,
                    'amount_currency': record.diferenciaPagos * -1,
                }
                lines_ids.append((0, 0, credit))

            move = {
                'journal_id': record.env['account.journal'].search([('type', '=', 'general')])[0].id,
                'date': record.fecha,
                'partner_id': record.partner_id.id,
                'move_type': 'entry',
                'ref': record.writeoff_label,
                'line_ids': lines_ids
            }

            move_id = record.env['account.move'].create(move)
            if move_id:
                record.write({'writeOffMove_id': move_id.id})
                move_id.action_post()

            
    @api.depends('amount_total_selected','amount_total')
    def compute_diferencia(self):
        for record in self:
            record.diferenciaPagos = record.amount_total_selected - record.amount_total
        
    @api.depends('amount_total_selected','amount_total','diferenciaPagos')    
    def compute_mantenerAbierto(self):
        if self.amount_total_selected != 0 and self.amount_total != 0 and self.diferenciaPagos != 0 :
            self.ocultar_mantenerAbierto = False
        else:
            self.ocultar_mantenerAbierto = True
        
    @api.depends('mantenerAbierto')    
    def compute_ocultar_writeoff(self):
        if self.mantenerAbierto == 'mantener' :
            self.ocultar_writeoff = True
        else:
            self.ocultar_writeoff = False
                
    def compute_paid_invoices(self):
        for recibo in self:
            invoices = []
            for i in recibo.payment_ids:
                if i.payment_type == 'outbound':
                    for bill in i.reconciled_bill_ids:
                        invoices.append((4, bill.id, 0))
                else:
                    for invoice in i.reconciled_invoice_ids:
                        invoices.append((4, invoice.id, 0))
            recibo.paid_invoice_ids = invoices

    def _fechaLetras(self):
        for this in self:
            this.fecha_letras = this.fecha.strftime("%d de %B de %Y")

    def _cantRecibos(self):
        for this in self:
            if len(this.invoice_ids) > 10:
                this.cantRecibos = math.ceil(len(this.invoice_ids)/10)
            else:
                this.cantRecibos = 1

    @api.onchange('partner_id')
    @api.depends('payment_ids')
    def onchange_partner(self):
        for i in self:
            if i.payment_ids:
                for j in i.payment_ids:
                    j.update({'partner_id': i.partner_id.id})
            if i.invoice_ids and not i.invoice_ids.filtered(lambda x: x.partner_id == i.partner_id or x.partner_id.commercial_partner_id == i.partner_id ):
                i.update({'invoice_ids': [(5, 0, 0)]})

    @api.onchange('fecha')
    @api.depends('payment_ids')
    def onchange_fecha(self):
        for i in self:
            if i.payment_ids:
                for j in i.payment_ids:
                    j.update({'date': i.fecha})

    @api.onchange('payment_ids','invoice_ids','currency_id')
    @api.depends('payment_ids','invoice_ids','currency_id')
    def compute_total(self):
        for i in self:
            amount = 0
            for p in i.payment_ids:
                if p.currency_id != i.currency_id:
                    amount_converted = p.currency_id._convert(p.amount, i.currency_id, self.company_id, i.fecha)
                    amount += amount_converted
                else:
                    amount += p.amount
            i.amount_total = amount
            amount_total_selected = 0
            for invoice in i.invoice_ids :
                if invoice.currency_id == i.currency_id :
                    amount_total_selected += invoice.amount_residual
                else :
                    amount_total_selected += invoice.currency_id._convert(invoice.amount_residual,i.currency_id,self.env.company,i.fecha)            

            i.amount_total_selected = amount_total_selected
            
    @api.depends('payment_type')
    def genera_secuencia(self):
        if self.payment_type == 'inbound':
            print(f"seq:::{self.sudo().env['ir.sequence'].next_by_code('seq_recibo')}")
            seq = self.sudo().env['ir.sequence'].next_by_code('seq_recibo')
        elif self.payment_type == 'outbound':
            seq = self.sudo().env['ir.sequence'].next_by_code('seq_orden_pago')
        return seq

    def button_confirmar(self):
        for record in self:
            record.confirmar()
            if record.diferenciaPagos and record.mantenerAbierto == 'paid':
                record.crearAsientoConciliacion()
            record.conciliar()
            
    def confirmar(self):
        for i in self:
            for j in i.payment_ids:
                if not j.tipo_pago:
                    raise exceptions.ValidationError("El tipo de pago no puede estar vacío, por favor asigne el valor en la linea de pago.")
                j.action_post()
                if j.payment_type == 'inbound':
                    movimiento = j.line_ids.filtered(
                        lambda z: z.debit > 0)
                elif j.payment_type == 'outbound':
                    movimiento = j.line_ids.filtered(
                        lambda z: z.credit > 0)
                else:
                    movimiento = j.line_ids
                for x in movimiento:
                    referencia = j.tipo_pago.capitalize()+" "
                    if j.bank_id:
                        referencia += j.bank_id.name+" "
                    if j.nro_cheque:
                        referencia += j.nro_cheque+" "
                    if j.nro_documento:
                        referencia += j.nro_documento+" "
                    x.write({'ref': referencia})
            i.write({'state': 'done'})
            

            
            
    def conciliar(self):
       for record in self:
            lineasDeuda = record.invoice_ids.line_ids.filtered(lambda x: x.account_id.account_type in ['asset_receivable', 'liability_payable'])
            lineasPago = record.payment_ids.line_ids.filtered(lambda x: x.account_id.account_type in ['asset_receivable', 'liability_payable'])
            lineasConciliacion = record.writeOffMove_id.line_ids.filtered(lambda x: x.account_id.account_type in ['asset_receivable', 'liability_payable'])
            (lineasDeuda + lineasPago + lineasConciliacion).reconcile()
        

    def button_cancelar(self):
        for i in self.payment_ids:
            i.action_cancel()
            i.action_draft()
        if self.writeOffMove_id :
            self.writeOffMove_id.button_draft()
            self.writeOffMove_id.unlink()

        self.write({'state': 'cancel'})

    def button_draft(self):
        for i in self.payment_ids:
            i.action_draft()
        self.write({'state': 'draft'})

    def asigna_nombre(self):
        for i in self:
            if self.name and self.name == 'Borrador':
                new_name = i.genera_secuencia()
                i.write({'name': new_name})
            else:
                return

    def write(self, vals):
        for i in self:
            if vals.get('state') and vals.get('state') == 'done':
                i.asigna_nombre()
            return super(PaymentGroup, i).write(vals)

    @api.model
    def create(self, vals):
        flag = True
        if vals.get('payment_type') == 'inbound':
            if not flag:
                raise exceptions.ValidationError(
                    ('No tiene permisos para registrar recibos'))
        if vals.get('payment_type') == 'outbound':
            if not flag:
                raise exceptions.ValidationError(
                    ('No tiene permisos para registrar ordenes de pago'))
        if not vals.get('payment_type'):
            raise exceptions.ValidationError(
                ('Tipo de pago no definido. Contacte con su administrador'))
        return super(PaymentGroup, self).create(vals)

    def amount_to_text_esp(self, amount):
        MONEDA_SINGULAR = 'bolivar'
        MONEDA_PLURAL = 'bolivares'

        CENTIMOS_SINGULAR = 'centimo'
        CENTIMOS_PLURAL = 'centimos'

        MAX_NUMERO = 999999999999

        UNIDADES = (
            'cero',
            'uno',
            'dos',
            'tres',
            'cuatro',
            'cinco',
            'seis',
            'siete',
            'ocho',
            'nueve'
        )

        DECENAS = (
            'diez',
            'once',
            'doce',
            'trece',
            'catorce',
            'quince',
            'dieciseis',
            'diecisiete',
            'dieciocho',
            'diecinueve'
        )

        DIEZ_DIEZ = (
            'cero',
            'diez',
            'veinte',
            'treinta',
            'cuarenta',
            'cincuenta',
            'sesenta',
            'setenta',
            'ochenta',
            'noventa'
        )

        CIENTOS = (
            '_',
            'ciento',
            'doscientos',
            'trescientos',
            'cuatroscientos',
            'quinientos',
            'seiscientos',
            'setecientos',
            'ochocientos',
            'novecientos'
        )

        def numero_a_letras(numero):
            numero_entero = int(numero)
            if numero_entero > MAX_NUMERO:
                raise OverflowError('Número demasiado alto')
            if numero_entero < 0:
                return 'menos %s' % numero_a_letras(abs(numero))
            letras_decimal = ''
            parte_decimal = int(
                round((abs(numero) - abs(numero_entero)) * 100))
            if parte_decimal > 9:
                letras_decimal = 'punto %s' % numero_a_letras(parte_decimal)
            elif parte_decimal > 0:
                letras_decimal = 'punto cero %s' % numero_a_letras(
                    parte_decimal)
            if (numero_entero <= 99):
                resultado = leer_decenas(numero_entero)
            elif (numero_entero <= 999):
                resultado = leer_centenas(numero_entero)
            elif (numero_entero <= 999999):
                resultado = leer_miles(numero_entero)
            elif (numero_entero <= 999999999):
                resultado = leer_millones(numero_entero)
            else:
                resultado = leer_millardos(numero_entero)
            resultado = resultado.replace('uno mil', 'un mil')
            resultado = resultado.strip()
            resultado = resultado.replace(' _ ', ' ')
            resultado = resultado.replace('  ', ' ')
            if parte_decimal > 0:
                resultado = '%s %s' % (resultado, letras_decimal)
            return resultado.upper()

        def numero_a_moneda(numero):
            numero_entero = int(numero)
            parte_decimal = int(
                round((abs(numero) - abs(numero_entero)) * 100))
            centimos = ''
            if parte_decimal == 1:
                centimos = CENTIMOS_SINGULAR
            else:
                centimos = CENTIMOS_PLURAL
            moneda = ''
            if numero_entero == 1:
                moneda = MONEDA_SINGULAR
            else:
                moneda = MONEDA_PLURAL
            letras = numero_a_letras(numero_entero)
            letras = letras.replace('uno', 'un')
            letras_decimal = 'con %s %s' % (numero_a_letras(
                parte_decimal).replace('uno', 'un'), centimos)
            letras = '%s %s %s' % (letras, moneda, letras_decimal)
            return letras

        def leer_decenas(numero):
            if numero < 10:
                return UNIDADES[numero]
            decena, unidad = divmod(numero, 10)
            if numero <= 19:
                resultado = DECENAS[unidad]
            elif numero <= 29:
                resultado = 'veinti%s' % UNIDADES[unidad]
            else:
                resultado = DIEZ_DIEZ[decena]
                if unidad > 0:
                    resultado = '%s y %s' % (resultado, UNIDADES[unidad])
            return resultado

        def leer_centenas(numero):
            centena, decena = divmod(numero, 100)
            if numero == 0:
                resultado = 'cien'
            else:
                resultado = CIENTOS[centena]
                if decena > 0:
                    resultado = '%s %s' % (resultado, leer_decenas(decena))
            return resultado

        def leer_miles(numero):
            millar, centena = divmod(numero, 1000)
            resultado = ''
            if (millar == 1):
                resultado = ''
            if (millar >= 2) and (millar <= 9):
                resultado = UNIDADES[millar]
            elif (millar >= 10) and (millar <= 99):
                resultado = leer_decenas(millar)
            elif (millar >= 100) and (millar <= 999):
                resultado = leer_centenas(millar)
            resultado = '%s mil' % resultado
            if centena > 0:
                resultado = '%s %s' % (resultado, leer_centenas(centena))
            return resultado

        def leer_millones(numero):
            millon, millar = divmod(numero, 1000000)
            resultado = ''
            if (millon == 1):
                resultado = ' un millon '
            if (millon >= 2) and (millon <= 9):
                resultado = UNIDADES[millon]
            elif (millon >= 10) and (millon <= 99):
                resultado = leer_decenas(millon)
            elif (millon >= 100) and (millon <= 999):
                resultado = leer_centenas(millon)
            if millon > 1:
                resultado = '%s millones' % resultado
            if (millar > 0) and (millar <= 999):
                resultado = '%s %s' % (resultado, leer_centenas(millar))
            elif (millar >= 1000) and (millar <= 999999):
                resultado = '%s %s' % (resultado, leer_miles(millar))
            return resultado

        def leer_millardos(numero):
            millardo, millon = divmod(numero, 1000000)
            return '%s millones %s' % (leer_miles(millardo), leer_millones(millon))

        convert_amount_in_words = numero_a_letras(amount)
        return convert_amount_in_words

# ------ condiciones
    @api.depends('payment_type')
    def _compute_invoice_type(self):
        for record in self:
            record.invoice_type = 'out_invoice' if record.payment_type == 'inbound' else 'in_invoice'