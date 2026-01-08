from odoo import models, fields, api
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(selection_add=[
        ('waiting_currency_update', 'Pendiente de Actualizar Cotización'),
        ('waiting_approval', 'Pendiente de Aprobación por Directorio'),
        ('approved','Aprobado por el Directorio')
    ])

    rate_updated = fields.Boolean(string="Se actualizó la cotización", default=False, copy=False)

    requiere_aprobacion = fields.Boolean(string="Requiere Aprobacion", default=False, compute="computeRequiereAprobacion")

    def computeRequiereAprobacion(self):
        for record in self:
            if record.company_id.restriction_receiving_import and record.purchase_id.currency_id != record.company_id.currency_id:
                record.requiere_aprobacion = True
            else:
                record.requiere_aprobacion = False

    def action_request_currency_update(self):
        for picking in self:
            if picking.requiere_aprobacion:
                picking._sanity_check()
                picking.state = 'waiting_currency_update'

    def action_submit_for_approval(self):
        for picking in self:
            if picking.state == 'waiting_currency_update':
                picking.rate_updated = True
                picking.state = 'waiting_approval'

    def action_approve(self):
        for picking in self:
            if picking.state == 'waiting_approval':
                picking.state = 'approved'

    def button_validate(self):
        for record in self:
            if record.requiere_aprobacion and record.state != 'approved':
                raise UserError("No puede validar la recepción hasta que se actualice la cotización y el directorio haya dado su visto bueno.")
        return super().button_validate()