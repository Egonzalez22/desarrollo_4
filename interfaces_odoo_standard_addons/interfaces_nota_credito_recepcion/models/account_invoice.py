from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    nota_credito_picking_id = fields.Many2one('stock.picking')
    factura_origen_nc = fields.Char('Fatura de Origen')
    stock_picking_id = fields.Many2one('stock.picking.type', string="Operacion")
    confirmar_sin_devolucion = fields.Boolean('Confirmar sin devolución', track_visibility="onchange", default=False, copy=False)

    def button_cancel(self):
        for this in self:
            if this.move_type == 'out_refund' and this.nota_credito_picking_id:
                if this.nota_credito_picking_id.state in ['done']:
                    raise ValidationError('La devolución ya fue hecha, no se puede cancelar la nota de crédito')
                else:
                    this.nota_credito_picking_id.action_cancel()
        return super(AccountMove, self).button_cancel()

    def action_post(self):
        # Si existe la key, entonces se procesa desde donde se llama
        if self.env.context.get('procesar_devolucion_personalizada'):
            r = super(AccountMove, self).action_post()
            return r

        for i in self:
            confirmar_sin_devolucion = i.confirmar_sin_devolucion
            if i.mapped('invoice_line_ids').filtered(lambda q: q.product_id).mapped('product_id.detailed_type') == ['service']:
                confirmar_sin_devolucion = True
            if not i.stock_picking_id and i.move_type in ['out_refund', 'in_refund'] and not confirmar_sin_devolucion:
                raise ValidationError('No se definió una operación para la recepción de las devoluciones')
        # confirmar account move
        r = super(AccountMove, self).action_post()

        for this in self:
            servicio = False
            confirmar_sin_devolucion = this.confirmar_sin_devolucion
            if this.mapped('invoice_line_ids').filtered(lambda q: q.product_id).mapped('product_id.detailed_type') == ['service']:
                confirmar_sin_devolucion = True

            if not confirmar_sin_devolucion and this.move_type in ['out_refund', 'in_refund'] and this.invoice_line_ids.filtered(lambda q: q.product_id):
                lines = []
                servicio = False
                # location_id = self.env['stock.location'].search([('usage', '=', 'customer')]).id
                for line in this.invoice_line_ids:
                    if line.product_id.detailed_type == 'service':
                        # ignorar productos tipo servicio
                        continue
                    else:
                        lines.append((0, 0, {
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.quantity,
                            'name': line.product_id.name,
                            'product_uom': line.product_uom_id.id,
                            'location_id': this.stock_picking_id.default_location_src_id.id,
                            'location_dest_id': this.stock_picking_id.default_location_dest_id.id,
                            'date': this.invoice_date,
                            'company_id': self.env.company.id,
                        }))
                if not lines:
                    # si no tiene lineas entonces es solo servicios
                    servicio = True  
                vals = {'partner_id': this.partner_id.id,
                        # 'origin': this.fake_number,
                        'origin': '0',
                        'picking_type_id': this.stock_picking_id.id,  # tipo de operacion m2o stock.picking.type
                        'location_id': this.stock_picking_id.default_location_src_id.id,  # ubicacion de origen m2o stock.location
                        'location_dest_id': this.stock_picking_id.default_location_dest_id.id,
                        'move_ids_without_package': lines,  # Movimietos de Almacén sin paquete o2m stock.move
                        'move_type': 'one'}  # ver que valores poner si one o direct

                if not servicio:
                    this.update({'nota_credito_picking_id': self.env['stock.picking'].create(vals)})
                    this.nota_credito_picking_id.action_confirm()
                    this.nota_credito_picking_id.action_assign()
        return r
