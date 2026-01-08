from odoo import fields, models, api, exceptions


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for this in self:
            if this.location_dest_id.allowed_user_ids_inflows and this.env.user not in this.location_dest_id.allowed_user_ids_inflows:
                raise exceptions.ValidationError(
                    'La ubicación de destino tiene restricciones sobre quiénes pueden recibir existencias, y tu usuario no está autorizado para ello'
                )
            if this.location_id.allowed_user_ids_outflows and this.env.user not in this.location_id.allowed_user_ids_outflows:
                raise exceptions.ValidationError(
                    'La ubicación de origen tiene restricciones sobre quiénes pueden entregar existencias, y tu usuario no está autorizado para ello'
                )
        return super(StockPicking, self).button_validate()
