from odoo import models, fields, api, exceptions, _


 
class ReporteOrdenPago(models.AbstractModel):
    _name = 'report.orden_personalizacion.orden_pago'

    @api.model
    def _get_report_values(self, docids, data=None):
        recibo_name = 0
        partner = 0
        monto_total = 0
        fecha = 0
        facturas = 0
        moneda = 0
        payments = self.env['account.payment'].browse(docids)

        if payments:
            for i in payments:
                if not i.partner_id:
                    raise exceptions.UserError(_('Los pagos deben tener un cliente'))
            if len(list(set(payments.mapped("state")))) > 1:
                raise exceptions.UserError(_('Los pagos deben estar Publicados'))
            if list(set(payments.mapped("state")))[0] != "posted":
                raise exceptions.UserError(_('Los pagos deben estar en estado Publicado'))
            if len(payments.mapped("partner_id")) > 1:
                raise exceptions.UserError(_('Debe seleccionar pagos de solo un cliente'))
            if len(payments.mapped("currency_id")) > 1:
                raise exceptions.UserError(
                    _('Los pagos deben de ser de una sola moneda'))
            if len(list(set(payments.mapped("nro_recibo")))) > 1:
                raise exceptions.UserError(
                    _('Debe seleccionar el mismo Nro OP'))

            else:
                recibo_name = list(set(payments.mapped("nro_recibo")))
                partner = payments.mapped("partner_id")
                moneda = payments.mapped("currency_id")
                facturas = payments.mapped('reconciled_bill_ids')
                # facturas = payments.mapped('reconciled_invoice_ids')
                fecha = payments[0].date
                for payment in payments:
                    monto_total += payment.amount
                
           

            return {

                'payments': payments,
                'facturas': facturas,
                'recibo_name': recibo_name[0],
                'fecha': fecha.strftime('%d/%m/%Y'),
                'partner': partner,
                'moneda': moneda,
                'monto_total': monto_total,
                'usuario': self.env.user,
            }
