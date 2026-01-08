from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    ### GRUPO CAMPOS ESPECIALES ###

    ### SECTOR SEGUROS ###

    def getdPoliza(self):
        return

    def getdUnidVig(self):
        return

    def getdVigencia(self):
        return

    def getdNumPoliza(self):
        return

    def getdFecIniVig(self):
        return

    def getdFecFinVig(self):
        return

    def getdCodInt(self):
        return '001'

    def getgGrupSeg(self):
        """
        Póliza de seguros (EA790-EA799)
        """
        gGrupPolSeg = {
            'dPoliza': self.getdPoliza(),
            'dUnidVig': self.getdUnidVig(),
            'dVigencia': self.getdVigencia(),
            'dNumPoliza': self.getdNumPoliza(),
            'dFecIniVig': self.getdFecIniVig(),
            'dFecFinVig': self.getdFecFinVig(),
            'dCodInt': self.getdCodInt(),
        }
        return gGrupPolSeg

    ### FIN SECTOR SEGUROS ###

    ### SECTOR SUPERMERCADOS ###
    def getdNomCaj(self):
        return

    def getdEfectivo(self):
        return

    def getdVuelto(self):
        return

    def getdDonac(self):
        return

    def getdDesDonac(self):
        return

    def getgGrupSup(self):
        gGrupSup = {  # Sector supermercados
            'dNomCaj': self.getdNomCaj(),
            'dEfectivo': self.getdEfectivo(),
            'dVuelto': self.getdVuelto(),
            'dDonac': self.getdDonac(),
            'dDesDonac': self.getdDesDonac(),
        }
        return gGrupSup

    ### FIN SECTOR SUPERMERCADOS ###

    def getgCamEsp(self):
        """
        Campos complementarios comerciales de uso específico (E790-E899)
        """
        gCamEsp = {
            'gGrupSeg': {'dCodEmpSeg': self.getdCodEmpSeg(), 'gGrupPolSeg': self.getgGrupSeg()},  # Sector seguros
            'gGrupSup': self.getgGrupSup(),  # Sector supermercados
            'gGrupAdi': {  # Grupo de datos adicionales de uso comercial
                'dCiclo': self.getdCiclo(),
                'dFecIniC': self.getdFecIniC(),
                'dFecFinC': self.getdFecFinC(),
                'dVencPag': self.getdVencPag(),
                'dContrato': self.getdContrato(),
                'dSalAnt': self.getdSalAnt(),
            },
        }
        if self.company_id.sector_seguros:
            gCamEsp['gGrupSeg'] = self.getgGrupSeg()
        if self.company_id.sector_supermercado:
            gCamEsp['gGrupSup'] = self.getgGrupSup()
        return gCamEsp

    ### FIN GRUPO CAMPOS ESPECIALES ###
