from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def getdOrdCompra(self):
        return

    def getdOrdVta(self):
        return

    def getdAsiento(self):
        return

    # CAMPOS DE USO GENERAL
    def getgCamGen(self):
        gCamGen = {  # Campos de uso general
            'dOrdCompra': self.getdOrdCompra(),
            'dOrdVta': self.getdOrdVta(),
            'dAsiento': self.getdAsiento(),
            'gCamCarg': {  # OPCIONAL EN LA NOTA DE REMISION
                'cUniMedTotVol': self.getcUniMedTotVol(),
                'dDesUniMedTotVol': self.getdDesUniMedTotVol(),
                'dTotVolMerc': self.getdTotVolMerc(),
                'cUniMedTotPes': self.getcUniMedTotPes(),
                'dDesUniMedTotPes': self.getdDesUniMedTotPes(),
                'dTotPesMerc': self.getdTotPesMerc(),
                'iCarCarga': self.getiCarCarga(),
                'dDesCarCarga': self.getdDesCarCarga(),
            },
        }
        return gCamGen

    ### FIN CAMPOS DE USO GENERAL ###
