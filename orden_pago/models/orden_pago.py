from odoo import api, exceptions, fields, models, tools


class OrdenPago(models.Model):
    _name = 'orden_pago.orden_pago'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Orden de Pago'

    name = fields.Char(string='Solicitud de pago', copy=False)
    concepto = fields.Char(string="Concepto de Pago")
    reporte_name = fields.Char(string="Grupo reporte")
    motivo_rechazo = fields.Char(string="Motivo de rechazo")
    importe_calculado = fields.Float(string='Importe Calculado', default=0)
    importe_pagado = fields.Float(string='Importe Pagado', default=0)
    fecha_aprobado = fields.Date(string="Fecha de aprobación")
    aprobado_por = fields.Many2one('res.users', string="Aprobado por")
    currency_id = fields.Many2one('res.currency', string="Moneda", default=lambda self: self.env.company.currency_id)
    state = fields.Selection(
        string='Estado',
        selection=[
            ('draft', 'Borrador'),
            ('to_approve', 'Para aprobar'),
            ('approved', 'Aprobado'),
            ('rejected', 'Rechazado'),
            ('cancel','Cancelado')
        ],
        default="draft",
    )
    # Partner del tipo proveedor
    partner_id = fields.Many2one(
        'res.partner',
        string='Proveedor',
        domain="[('supplier_rank','>',0)]",
        required=True,
    )
    # Facturas del proveedor, que esten en estado 'posted', que no esten pagadas y que sean in_invoice
    invoice_ids = fields.Many2many(
        'account.move',
        string="Facturas de proveedor",
        domain="[('partner_id','=',partner_id), ('state','in',['posted']), ('payment_state','in',['not_paid','partial']), ('move_type','=','in_invoice'), ('currency_id','=',currency_id)]",
    )
    
    # Se agrega formas de de pago
    tipo_pago = fields.Selection(
        string='Tipo de pago', 
        selection=[
            ('Efectivo', 'Efectivo'), 
            ('Cheque', 'Cheque'),
            ('TCredito', 'Tarjeta de crédito'), 
            ('TDebito', 'Tarjeta de débito'),
            ('Transferencia', 'Transferencia / Depósito'),
            ('Retencion', 'Retención'), 
            ('Otros', 'Otros')
        ])
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    @api.onchange('invoice_ids')
    def _compute_descripcion(self):
        for record in self:
            # 157538: Solamente cuando se modifican las lineas de factura modificamos el concepto
            descripciones = [
                tools.html2plaintext(invoice.narration).strip()
                for invoice in record.invoice_ids if invoice.narration
            ]
            record.concepto = ' / '.join(descripciones)         
                
    # Sobreescribimos el metodo create
    @api.model
    def create(self, values):
        res = super(OrdenPago, self).create(values)

        if res:
            res.write({'name': res.id})

            # Se elimina la secuencia y se toma el ID porque debe ser incremental y no cambiar mas
            # seq = self.env['ir.sequence'].sudo().next_by_code('seq_orden_pago_terranova')
            # return f'OP/{seq.zfill(4)}'

        return res


    def solicitar_aprobacion_masiva(self):
        for record in self:
            record.button_solicitud_aprobacion()

    def aprobacion_masiva(self):
        for record in self:
            record.button_aprobar()

    def button_solicitud_aprobacion(self):
        # Si no hay facturas no se puede solicitar aprobacion
        #if not self.invoice_ids:
        #    raise exceptions.ValidationError('No se puede solicitar aprobación sin facturas')

        # Solamente se puede solicitar aprobacion si el estado es borrador
        if self.state != 'draft':
            raise exceptions.ValidationError('Para solicitar aprobación las ordenes de pago deben estar en estado borrador')

        # El usuario debe tener permiso de solicitar aprobación
        if not self.env.user.has_group('orden_pago.solicitar_aprobacion'):
            raise exceptions.ValidationError('No tiene permiso para solicitar aprobación')

        self.write({'state': 'to_approve'})

    def button_aprobar(self):
        # Si no hay facturas y el importe_pagado es nulo, no se puede pasar a aprobación
        if not self.importe_pagado: #not self.invoice_ids and 
            raise exceptions.ValidationError('No se puede pasar a aprobación sin facturas o importe pagado')

        # Solamente se pueden aprobar las ordenes de pago que esten en estado para aprobar
        if self.state != 'to_approve':
            raise exceptions.ValidationError('Para aprobar las ordenes de pago deben estar en estado para aprobar')

        # El usuario debe tener permiso de solicitar aprobación
        if not self.env.user.has_group('orden_pago.aprobar_orden'):
            raise exceptions.ValidationError('No tiene permiso para solicitar aprobación')

        data = {
            'state': 'approved',
            'aprobado_por': self.env.user.id,
            'fecha_aprobado': fields.Date.today(),
        }
        if not self.invoice_ids:
            payment_vals = {
                ''
            }
        self.write(data)

    def button_restablecer_borrador(self):
        self.write({'state': 'draft'})

    def button_rechazar(self):
        self.write({'state': 'rejected'})

    def button_cancelar(self):
        self.write({'state': 'cancel'})

    def button_reporte(self):
        view_id = self.env.ref('orden_pago.orden_pago_informe_wizard_view')
        print(self.ids)
        return {
            'name': 'Generar Informe',
            'view_mode': 'form',
            'res_model': 'orden_pago.orden_pago_informe_wizard',
            'view_id': view_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_ids': self.ids},
        }

    @api.onchange('invoice_ids')
    def _onchange_invoice_ids(self):
        for record in self:
            if record.invoice_ids:
                total = sum(record.invoice_ids.mapped('amount_residual_signed')) * -1
                record.importe_calculado = total
                record.importe_pagado = total


    def get_amount_format(self, amount, currency=None):
        """
        Formateamos el monto con separadores de miles y decimales
        """
        # Formateamos con separadores de miles y decimales
        if currency and currency.name == 'PYG':
            amount = "{:,.0f}".format(amount).replace(',', '.')
            return amount

        # Si no hay currency o es diferente a PYG, formateamos con 2 decimales
        amount = "{:,.2f}".format(amount).replace(',', 'X').replace('.', ',').replace('X', '.')
        return amount

    payment_ids = fields.One2many("account.payment", inverse_name="orden_pago_id")
    payment_count = fields.Integer(
        compute="_compute_payment_count"
    )

    @api.depends("payment_ids")
    def _compute_payment_count(self):
        for record in self:
            record.payment_count = len(record.payment_ids)

    def action_view_payment_ids(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_account_payments_payable"
        )
        action["domain"] = [("id", "=", self.payment_ids.ids)]
        return action