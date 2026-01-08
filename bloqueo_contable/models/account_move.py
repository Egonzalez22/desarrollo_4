from odoo import models, api, exceptions, _

from odoo.tools import format_date

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    def bloqueo_contable(self):
        fecha_factura = self.invoice_date or self.date
        affects_tax_report = self._affect_tax_report()
        lock_dates = self._get_violated_lock_dates(fecha_factura, affects_tax_report)
        
        if lock_dates:
            lock_date, lock_type = lock_dates[-1]
            if fecha_factura <= lock_date:
                lock_date=format_date(self.env, lock_date)
                raise exceptions.ValidationError(f"La fecha se establece antes de la fecha de bloqueo {lock_type}: {lock_date}")
            
    @api.model
    def create(self, vals):
        result = super(AccountMove, self).create(vals)
        for record in self:
            record.bloqueo_contable()

        return result
    
    @api.model
    def write(self, vals):
        result = super(AccountMove, self).write(vals)
        for record in self:
            record.bloqueo_contable()

        return result
    
    def _get_lock_date_message(self, invoice_date, has_tax):
        """Get a message describing the latest lock date affecting the specified date.
        :param invoice_date: The date to be checked
        :param has_tax: If any taxes are involved in the lines of the invoice
        :return: a message describing the latest lock date affecting this move and the date it will be
                 accounted on if posted, or False if no lock dates affect this move.
        """
        lock_dates = self._get_violated_lock_dates(invoice_date, has_tax)
        if lock_dates:
            invoice_date = self._get_accounting_date(invoice_date, has_tax)
            lock_date, lock_type = lock_dates[-1]
            tax_lock_date_message = _(
                "La fecha se establece antes de la fecha de bloqueo %(lock_type)s %(lock_date)s. ",
                lock_type=lock_type,
                lock_date=format_date(self.env, lock_date),
                invoice_date=format_date(self.env, invoice_date))
            return tax_lock_date_message
        return False
