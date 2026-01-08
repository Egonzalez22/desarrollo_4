from odoo import fields, api, models, exceptions, _


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ### Grupo de detalle de vehículos nuevos ###

    def getiTipOpVN(self):
        return

    def getdDesTipOpVN(self):
        return

    def getdChasis(self):
        return

    def getdColor(self):
        return

    def getdPotencia(self):
        return

    def getdCapMot(self):
        return

    def getdPNet(self):
        return

    def getdPBruto(self):
        return

    def getiTipCom(self):
        return

    def getdDesTipCom(self):
        return

    def getdDesTipCom(self):
        return

    def getdNroMotor(self):
        return

    def getdCapTracc(self):
        return

    def getdAnoFab(self):
        return

    def getcTipVeh(self):
        return

    def getdCapac(self):
        return

    def getdCilin(self):
        return

    def getgVehNuevo(self):
        gVehNuevo = {
            'iTipOpVN': self.getiTipOpVN(),
            'dDesTipOpVN': self.getdDesTipOpVN(),
            'dChasis': self.getdChasis(),
            'dColor': self.getdColor(),
            'dPotencia': self.getdPotencia(),
            'dCapMot': self.getdCapMot(),
            'dPNet': self.getdPNet(),
            'dPBruto': self.getdPBruto(),
            'iTipCom': self.getiTipCom(),
            'dDesTipCom': self.getdDesTipCom(),
            'dNroMotor': self.getdNroMotor(),
            'dCapTracc': self.getdCapTracc(),
            'dAnoFab': self.getdAnoFab(),
            'cTipVeh': self.getcTipVeh(),
            'dCapac': self.getdCapac(),
            'dCilin': self.getdCilin(),
        }
        return gVehNuevo

    ### FIN Grupo de detalle de vehículos nuevos ###
