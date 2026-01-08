from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    motivo_emision = fields.Selection(
        string="Motivo de Emisión",
        selection=[
            ('1', 'Devolución y Ajuste de precios'),
            ('2', 'Devolución'),
            ('3', 'Descuento'),
            ('4', 'Bonificación'),
            ('5', 'Crédito incobrable'),
            ('6', 'Recupero de costo'),
            ('7', 'Recupero de gasto'),
            ('8', 'Ajuste de precio'),
        ],
        default="1",
        track_visibility="onchange",
    )

    def getiMotEmi(self):
        if self.motivo_emision:
            return int(self.motivo_emision)

        # TODO: Validar que se seleccione en notas
        return None

    def getdDesMotEmi(self):
        if self.motivo_emision:
            items = dict(self._fields['motivo_emision'].selection)
            return items[self.motivo_emision]

        return None

    def getgCamNCDE(self):
        gCamNCDE = {
            'iMotEmi': self.getiMotEmi(),
            'dDesMotEmi': self.getdDesMotEmi(),
        }

        return gCamNCDE

    def getgDtipDE_nota_credito(self):
        xml = {}

        xml['gCamNCDE'] = self.getgCamNCDE()

        xml['gCamItem'] = []
        for line in self.get_lineas_facturables().sorted(key=lambda r: r.price_total):
            # Se comenta esta validacion, porque se pueden ir items con valor cero
            # if line.quantity > 0 and line.price_unit > 0:
            xml['gCamItem'].append(line.getgCamItem())

        return xml