from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    ### PAGO CON ENTREGA INICIAL ###

    def getiTiPago(self):
        # 1 = Efectivo
        # 2 = Cheque
        # 3 = Tarjeta de crédito
        # 4 = Tarjeta de débito
        # 5 = Transferencia
        # 6 = Giro
        # 7 = Billetera electrónica
        # 8 = Tarjeta empresarial
        # 9 = Vale
        # 10 = Retención
        # 11 = Pago por anticipo
        # 12 = Valor fiscal
        # 13 = Valor comercial
        # 14 = Compensación
        # 15 = Permuta
        # 16 = Pago bancario(Informar solo si E011 = 5)
        # 17 = Pago Móvil
        # 18 = Donación
        # 19 = Promoción
        # 20 = Consumo Interno
        # 21 = Pago Electrónico
        # 99 = Otro
        return 1

    def getdDesTiPag(self):
        return 'Efectivo'

    def getdMonTiPag(self):
        """
        E608: Monto por tipo de pago 1-15p(0-4)
        """
        return round(self.get_amount_total(), 4)

    def getcMoneTiPag(self):
        return self.currency_id.name

    def getdDMoneTiPag(self):
        if self.currency_id.name == 'PYG':
            return "Guarani"
        elif self.currency_id.name == 'USD':
            return "US Dollar"
        return self.currency_id.currency_unit_label

    def getdTiCamTiPag(self):
        if self.getdCondTiCam() == 1:
            return self.obtener_cotizacion()
        else:
            return ""

    def getgPagCheq(self):
        return

    def getdDesDenTarj(self):
        return

    def getdRSProTar(self):
        return

    def getdRUCProTar(self):
        return

    def getdDVProTar(self):
        return

    def getiForProPa(self):
        return

    def getdCodAuOpe(self):
        return

    def getdNomTit(self):
        return

    def getdNumTarj(self):
        return

    def getdNumCheq(self):
        return

    def getdNumTarj(self):
        return

    def getgPaConEIni(self):
        gPaConEIni = {  # OBLIGATORIO SI EL PAGO ES AL CONTADO
            'iTiPago': self.getiTiPago(),
            'dDesTiPag': self.getdDesTiPag(),
            'dMonTiPag': self.getdMonTiPag(),
            'cMoneTiPag': self.getcMoneTiPag(),
            'dDMoneTiPag': self.getdDMoneTiPag(),
        }
        if self.currency_id.name != "PYG":
            gPaConEIni['dTiCamTiPag'] = self.getdTiCamTiPag()  # OBLIGATORIO SI LA MONEDA NO ES PYG

        if self.getiTiPago() == 3 or self.getiTiPago() == 4:
            gPagTarCD = {  # OBLIGATORIO SI EL PAGO ES CON TC O TD (E606 = 3 O 4)
                'iDenTarj': self.getgPagCheq(),
                'dDesDenTarj': self.getdDesDenTarj(),
                'dRSProTar': self.getdRSProTar(),
                'dRUCProTar': self.getdRUCProTar(),
                'dDVProTar': self.getdDVProTar(),
                'iForProPa': self.getiForProPa(),
                'dCodAuOpe': self.getdCodAuOpe(),
                'dNomTit': self.getdNomTit(),
                'dNumTarj': self.getdNumTarj(),
            }
            gPaConEIni['gPagTarCD'] = gPagTarCD
        elif self.getiTiPago() == 2:
            gPagCheq = {  # OBLIGAROTIO SI EL PAGO ES CON CHEQUE (E606 = 2)
                'dNumCheq': self.getdNumCheq(),
                'dBcoEmi': self.getdBcoEmi(),
            }
            gPaConEIni['gPagCheq'] = gPagCheq
        return gPaConEIni

    ### FIN PAGO CON ENTREGA INICIAL ###
