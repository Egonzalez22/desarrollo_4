import math

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    ### GRUPO SUBTOTALES ###

    def getdSubExe(self):
        """
        F002
        Subtotal de la operación exenta
        1-15p(0-8)
        """
        lines = self.get_lineas_facturables().filtered(lambda x: x.tax_ids.amount == 0.0000)
        total = 0
        for i in lines:
            total = total + i.getdTotOpeItem()
        
        return round(total, 8)

    def getdSubExo(self):
        return 0

    def getdSub5(self):
        """
        F004
        Subtotal de la operación con IVA incluido a la tasa 5%
        1-15p(0-8)
        """
        lines = self.get_lineas_facturables().filtered(lambda x: x.tax_ids.amount == 5.0000)
        total = 0
        for i in lines:
            total = total + i.getdTotOpeItem()
        return round(total, 8)

    def getdSub10(self):
        """ 
        F005
        Subtotal de la operación con IVA incluido a la tasa 10%
        1-15p(0-8)
        """
        lines = self.get_lineas_facturables().filtered(lambda x: x.tax_ids.amount == 10.0000)
        total = 0
        for i in lines:
            total = total + i.getdTotOpeItem()

        total_redondeado = round(total, 8)
        return total_redondeado

    def getdTotOpe(self):
        """
        F008
        Total Bruto de la operación
        Cuando D013 = 1, 3, 4 o 5
        corresponde a la suma de los
        subtotales de la operación
        (F002, F003, F004 y F005)
        Cuando D013 = 2 corresponde a F006
        Cuando C002=4 corresponde a la suma de todas las ocurrencias
        de EA008 (Valor total de la operación por ítem)
        1-15p(0-8)
        """
        lines = self.get_lineas_facturables()
        total = 0
        for i in lines:
            total = total + i.getdTotOpeItem()

        # Limitamos los decimales a 8
        total = round(total, 8)
        return total

    def getdTotDesc(self):
        """
        F009
        Total descuento particular por ítem
        Suma de todos los descuentos particulares por ítem (EA002)
        1-15p(0-8)
        """
        lines = self.get_lineas_facturables()
        total = 0
        for i in lines:
            total = total + (i.getdDescItem() * i.quantity)

        # Limitamos los decimales a 8
        total = round(total, 8)
        return total

    def getdTotDescGlotem(self):
        """
        F033
        Total descuento global por ítem
        Sumatoria de todas las ocurrencias de descuentos globales por ítem
        1-15p(0-8)
        """
        if self.tiene_descuento_global():
            lineas_descuentos = self.get_lineas_descuentos_globales()
            if lineas_descuentos:
                total = abs(sum(lineas_descuentos.mapped('price_total')))
                return round(total, 8)

        return 0

    def getdTotAntItem(self):
        return 0

    def getdTotAnt(self):
        """
        F035
        Total Anticipo global por ítem
        1-15p(0-8)
        """
        if self.getiCondAnt():
            lineas_anticipo = self.get_lineas_anticipo()
            if lineas_anticipo:
                total = abs(sum(lineas_anticipo.mapped('price_total')))
                return round(total, 8)

        return 0

    def getdPorcDescTotal(self):
        """
        F010
        Porcentaje de
        descuento global sobre
        total de la operación
        Informativo, si no existe %, completar con cero
        1-3p(0-8)
        """
        if self.tiene_descuento_global():
            percent = self.getGlobalDiscAntPercent()
            return abs(round(percent, 8))

        return 0

    def getdDescTotal(self):
        """
        F011
        Sumatoria de todos los descuentos
        (Global por Ítem y particular por ítem) de cada ítem
        1-15p(0-8)
        """

        # Descuentos por linea
        lines = self.get_lineas_facturables()
        total = 0
        for i in lines:
            total = total + (i.getdDescItem() * i.quantity)

        # Descuentos globales
        total += self.getdTotDescGlotem()

        total = round(total, 8)
        return abs(total)

    def getdAnticipo(self):
        if self.getiCondAnt():
            lineas_anticipo = self.get_lineas_anticipo()
            if lineas_anticipo:
                total = abs(sum(lineas_anticipo.mapped('price_total')))
                return round(total, 8)

        return 0

    def getdRedon(self):
        # redondeo = round(self.getdTotOpe() / 100) * 100
        # return redondeo
        return 0

    def getdComi(self):
        return 0

    def getdTotGralOpe(self):
        """
        Total Neto de la operación
        1-15p(0-8)
        """
        total = self.getdTotOpe() - self.getdRedon() + self.getdComi()

        return round(total, 8)

    def getdIVA5(self):
        """
        Liquidación del IVA a la tasa del 5%
        1-15p(0-8)
        """
        lines = self.get_lineas_facturables().filtered(lambda x: x.tax_ids.amount == 5.0000)
        total = 0
        for i in lines:
            total = total + i.getdLiqIVAItem()

        return round(total, 8)

    def getdIVA10(self):
        """
        Liquidación del IVA a la tasa del 10%
        1-15p(0-8)
        """
        lines = self.get_lineas_facturables().filtered(lambda x: x.tax_ids.amount == 10.0000)
        total = 0
        for i in lines:
            total = total + i.getdLiqIVAItem()

        return round(total, 8)

    def getdLiqTotIVA5(self):
        return 0

    def getdLiqTotIVA10(self):
        return 0

    def getdIVAComi(self):
        return 0

    def getdTotIVA(self):
        """
        F017: Liquidación total del IVA
        1-15p(0-8)

        Corresponde al cálculo
        aritmético F015 (Liquidación del
        IVA al 10%) + F016(Liquidación
        del IVA al 5%) – F036 (redondeo
        al 5%) – F037 (redondeo al 10%)
        + F026 (Liquidación total del IVA
        de la comisión)
        No debe existir el campo si D013
        ≠ 1 o D013≠5
        """
        total = self.getdIVA5() + self.getdIVA10() - self.getdLiqTotIVA10() - self.getdLiqTotIVA5()
        return round(total, 8)

    def getdBaseGrav5(self):
        """
        F018: Total base gravada al 5%
        1-15p(0-8)

        Suma de todas las ocurrencias
        de E735 (base gravada del IVA
        por ítem) cuando la operación
        sea a la tasa del 5% (E734=5).
        No debe existir el campo si D013
        ≠ 1 o D013≠5
        """
        lines = self.get_lineas_facturables().filtered(lambda x: x.tax_ids.amount == 5.0000)
        total = 0
        for i in lines:
            total = total + i.getdBasGravIVA()
        return round(total, 8)

    def getdBaseGrav10(self):
        """
        F019: Total base gravada al 10%
        1-15p(0-8)

        Suma de todas las ocurrencias
        de E735 (base gravada del IVA
        por ítem) cuando la operación
        sea a la tasa del 10%
        (E734=10).
        No debe existir el campo si D013
        ≠ 1 o D013≠5
        """
        lines = self.get_lineas_facturables().filtered(lambda x: x.tax_ids.amount == 10.0000)
        total = 0
        for i in lines:
            total = total + i.getdBasGravIVA()
        return round(total, 8)

    def getdTBasGraIVA(self):
        """
        F020: Total de la base gravada de IVA
        1-15p(0-8)

        Corresponde al cálculo aritmético
        F018+F019
        No debe existir el campo si D013
        ≠ 1 o D013≠5
        """
        total = self.getdBaseGrav5() + self.getdBaseGrav10()
        return round(total, 8)

    def getdTotalGs(self):
        """
        F023: Total general de la operación en Guaraníes
        1-15p(0-8)
        """
        total_gs = self.getdTotGralOpe() * self.getdTiCam()
        # Limitamos los decimales a 8
        total_gs = round(total_gs, 8)
        return total_gs

    def getdTotCom(self):
        return

    def getgTotSub(self):
        """
        Campos de subtotales y totales
        Obligatorio si C002 ≠ 7
        No informar si C002 = 7
        Cuando C002= 4, no informar F002, F003, F004, F005, F015, F016, F017, F018, F019, F020, F023, F025 y F026
        """
        gTotSub = {}

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dSubExe'] = self.getdSubExe()

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dSubExo'] = self.getdSubExo()

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dSub5'] = self.getdSub5()

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dSub10'] = self.getdSub10()

        gTotSub['dTotOpe'] = self.getdTotOpe()
        gTotSub['dTotDesc'] = self.getdTotDesc()
        gTotSub['dTotDescGlotem'] = self.getdTotDescGlotem()
        gTotSub['dTotAntItem'] = self.getdTotAntItem()
        gTotSub['dTotAnt'] = self.getdTotAnt()
        gTotSub['dPorcDescTotal'] = self.getdPorcDescTotal()
        gTotSub['dDescTotal'] = self.getdDescTotal()
        gTotSub['dAnticipo'] = self.getdAnticipo()
        gTotSub['dRedon'] = self.getdRedon()
        gTotSub['dComi'] = self.getdComi()

        gTotSub['dTotGralOpe'] = self.getdTotGralOpe()

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dIVA5'] = self.getdIVA5()

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dIVA10'] = self.getdIVA10()

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dLiqTotIVA5'] = self.getdLiqTotIVA5()

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dLiqTotIVA10'] = self.getdLiqTotIVA10()

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dIVAComi'] = self.getdIVAComi()

        if self.tipo_documento not in ['autofactura']:
            # TODO: Falta validar No debe existir el campo si D013 ≠ 1 o D013≠5
            gTotSub['dTotIVA'] = self.getdTotIVA()

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dBaseGrav5'] = self.getdBaseGrav5()

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dBaseGrav10'] = self.getdBaseGrav10()

        if self.tipo_documento not in ['autofactura']:
            gTotSub['dTBasGraIVA'] = self.getdTBasGraIVA()

        if self.currency_id.name != 'PYG' and self.tipo_documento not in ['autofactura']:
            gTotSub['dTotalGs'] = self.getdTotalGs()

        # if self.getdComi() != 0:
        #     gTotSub['dComi'] = self.getdComi()
        #     gTotSub['dTotCom'] = self.getdTotCom()
        # if self.getiCondAnt():
        #     gTotSub['dAnticipo'] = self.getdAnticipo()
        #     gTotSub['dTotAntItem'] = self.getdTotAntItem()
        #     gTotSub['dTotAnt'] = self.getdTotAnt()

        # if self.desc():
        #     gTotSub['dDescTotal'] = self.getdDescTotal()
        #     if self.desc() == 2:
        #         gTotSub['dTotDescGlotem'] = self.getdTotDescGlotem()
        #         gTotSub['dTotDesc'] = self.getdTotDesc()
        #     elif self.desc() == 1:
        #         gTotSub['dPorcDescTotal'] = self.getdPorcDescTotal()

        return gTotSub

    ### FIN GRUPOS SUBTOTALES ###
