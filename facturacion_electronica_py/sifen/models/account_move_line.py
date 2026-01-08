import math
import re

from odoo import _, api, exceptions, fields, models


def round_up(n, decimals=0):
    multiplier = 10**decimals
    return math.ceil(n * multiplier) / multiplier


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ### GRUPO ITEMS DE LA OPERACION ###

    def getgCamItem(self):
        line = self
        gCamItem = {}
        gCamItem['dCodInt'] = line.getdCodInt()
        # gCamItem['dParAranc'] = line.getdParAranc()
        # gCamItem['dNCM'] = line.getdNCM()
        if line.move_id.getiTiOpe() == '3':
            gCamItem['dDncpG'] = line.getdDncpG()
            gCamItem['dDncpE'] = line.getdDncpE()
        # gCamItem['dGtin'] = line.getdGtin()
        # gCamItem['dGtinPq'] = line.getdGtinPq()
        gCamItem['dDesProSer'] = line.getdDesProSer()
        gCamItem['cUniMed'] = line.getcUniMed()
        gCamItem['dDesUniMed'] = line.getdDesUniMed()
        gCamItem['dCantProSer'] = line.getdCantProSer()
        # gCamItem['cPaisOrig'] = line.getcPaisOrig()
        # gCamItem['dDesPaisOrig'] = line.getdDesPaisOrig()
        gCamItem['dInfItem'] = line.getdDesProSer()  # getdInfItem
        # gCamItem['cRelMerc'] = line.getcRelMerc()  # OPCIONAL EN LA NOTA DE REMISION
        # gCamItem['dDesRelMerc'] = line.getdDesRelMerc()  # OPCIONAL EN LA NOTA DE REMISIÓN
        # gCamItem['dCanQuiMer'] = line.getdCanQuiMer()  # OPCIONAL EN LA NOTA DE REMISIÓN
        # gCamItem['dPorQuiMer'] = line.getdPorQuiMer()  # OPCIONAL EN LA NOTA DE REMISIÓN

        # if line.product_id.tracking and line.product_id.tracking != 'none':
        #    gCamItem['gRasMerc'] = line.getgRasMerc()


        # OBLIGATORIO SI HAY UNA FACTURA ASOCIADA POR ANTICIPO
        # TODO: Temporal
        # if line.move_id.factura_anticipo_id and line.move_id.factura_anticipo_id.cdc:
        #     gCamItem['dCDCAnticipo'] = line.move_id.factura_anticipo_id.cdc
        
        if line.move_id.facturas_anticipo_asociadas and line.move_id.facturas_anticipo_asociadas[0].cdc:
            gCamItem['dCDCAnticipo'] = line.move_id.facturas_anticipo_asociadas[0].cdc

        gCamItem['gValorItem'] = line.getgValorItem()  # NO INFORMAR EN LA NOTA DE REMISION
        if self.move_id.tipo_documento not in ["nota_remision", "autofactura"]:
            gCamItem['gCamIVA'] = line.getgCamIVA()  # NO INFORMAR EN AUTOFACTURA NI NOTA DE REMISION

        # gCamItem['gVehNuevo'] = line.getgVehNuevo()  # Grupo de detalle de vehículos nuevos

        return gCamItem

    ### FIN GRUPO ITEMS DE LA OPERACION ###
    def getdCodInt(self):
        if self.product_id and self.product_id.default_code:
            return self.product_id.default_code
        elif self.product_id and not self.product_id.default_code:
            return str(self.product_id.id)
        else:
            return str(self.id)

    def getdDesProSer(self):
        # Eliminamos caracteres extraños del nombre del producto
        if self.name:
            name = self.name.replace('\n', ' ')
            name = name.replace('\r', ' ')
            name = name.replace('\t', ' ')
            # Eliminamos caracteres especiales
            name = re.sub('\W+', ' ', name)
        else:
            name = ""

        return name

    def getcUniMed(self):
        return self.product_uom_id.cod_set if self.product_uom_id.cod_set else 77

    def getdDesUniMed(self):
        return self.product_uom_id.des_set if self.product_uom_id.des_set else "UNI"

    def getdCantProSer(self):
        """
        E711: Cantidad del producto y/o servicio
        1-10p(0-4)
        """
        return round(self.quantity, 4)

    def getcPaisOrig(self):  # COD Pais de Origen
        return 0

    def getdDesPaisOrig(self):  # Descripción País de Origen
        return 0

    ### GRUPO PRECIOS, DESCUENTOS, VALOR ITEM ###
    def getdPUniProSer(self):
        """
        E721: Precio unitario del producto y/o servicio (incluidos impuestos)
        1-15p(0-8)
        """
        return round(self.price_unit, 8)

    def getdTiCamIt(self):
        """
        E725: Tipo de cambio por ítem
        1-5p(0-4)
        """
        cotizacion = self.move_id.obtener_cotizacion()
        return round(cotizacion, 4)

    def getdTotBruOpeItem(self):
        """
        E727
        Total bruto de la operación por ítem
        Corresponde a la del precio por ítem (E721) y la multiplicación
        cantidad por ítem (E711)
        """
        total = self.price_unit * self.quantity
        return round(total, 8)

    def getdDescItem(self):
        """
        EA002
        Descuento particular sobre el precio unitario
        por ítem (incluidos impuestos)
        Si no completar con 0 (cero) hay descuento por ítem
        1-15p(0-8)
        """
        monto = 0
        if self.discount:
            monto = self.getdTotBruOpeItem() * self.discount / 100 / self.quantity
            # Limitamos los decimales a 8
            monto = round(monto, 8)

        return monto

    def getdPorcDesIt(self):
        """
        EA003
        Porcentaje de descuento particular por ítem
        Debe existir si EA002 es mayor a 0 (cero) [EA002 * 100 / E721]
        """
        return round(self.discount, 8)

    def getdAntPreUniIt(self):
        """
        EA006
        Anticipo particular sobre el precio unitario por ítem (incluidos impuestos)
        No se implemento el anticipo por item
        """
        return 0



    def getdDescGloItem(self):
        """
        EA004
        Descuento global sobre el precio unitario por ítem (incluidos impuestos)
        Si se cuenta con un descuento global, debe ser aplicado (no es
        prorrateo) a cada uno de los ítems, independientemente que un
        ítem cuente con un descuento particular.
        1-15p(0-8)
        """
        percent = self.move_id.getGlobalDiscAntPercent()

        if self.move_id.tiene_descuento_global():
            monto = (self.getdTotBruOpeItem() * percent / 100) / self.quantity
            return round(monto, 8)

        return 0


    def getdAntGloPreUniIt(self):
        """
        EA007
        Si se cuenta con un anticipo
        global, debe ser aplicado a cada uno de los ítems,
        independientemente de que un ítem cuente con un anticipo
        particular. Si no hay anticipo global por ítem, completar con 0 (cero)
        1-15p(0-8)
        """
        percent = self.move_id.getGlobalDiscAntPercent()

        if self.move_id.getiCondAnt():
            monto = (self.getdTotBruOpeItem() * percent / 100) / self.quantity
            return round(monto, 8)
            
        return 0

    def getdTotOpeItem(self):
        """
        EA008
        Valor total de la operación por ítem
        Cálculo para IVA, Renta,
        ninguno, IVA - Renta
        Si D013 = 1, 3, 4 o 5 (afectado al IVA, Renta, ninguno, IVA - Renta),
        entonces EA008 corresponde al cálculo aritmético: 
        
        (E721 (Precio unitario) - EA002 (Descuento particular) - EA004 (Descuento global) - EA006 (Anticipo particular) - EA007 (Anticipo global)) * E711(cantidad)
        
        Cálculo para Autofactura
        (C002=4): E721*E711

        1-15p(0 8)
        """
        monto = self.getdTotBruOpeItem()

        # Si hay descuento por item
        if self.getdDescItem():
             monto = monto - (self.getdDescItem() * self.quantity)
        
        # Si hay anticipo global
        if self.move_id.getiCondAnt():
            anticipo_linea = (self.getdAntGloPreUniIt() * self.quantity)
            monto = monto - anticipo_linea
        
        # Si hay descuento global
        if self.move_id.tiene_descuento_global():
            descuento_linea = (self.getdDescGloItem() * self.quantity)
            monto = monto - descuento_linea

        monto = round(monto, 8)
        return monto

    def getdTotOpeGs(self):
        """
        EA009 
        Valor total de la operación por ítem en guaraníes
        1-15p(0-8)
        """
        total_gs = self.getdTotOpeItem() * self.getdTiCamIt()
        return total_gs

    def getgValorRestaItem(self):
        """
        E8.1.1 Campos que describen los descuentos, anticipos y valor total por ítem (EA001-EA050)
        """
        gValorRestaItem = {}

        gValorRestaItem['dDescItem'] = self.getdDescItem()
        gValorRestaItem['dPorcDesIt'] = self.getdPorcDesIt()
        gValorRestaItem['dDescGloItem'] = self.getdDescGloItem()
        gValorRestaItem['dAntPreUniIt'] = self.getdAntPreUniIt()
        gValorRestaItem['dAntGloPreUniIt'] = self.getdAntGloPreUniIt()
        gValorRestaItem['dTotOpeItem'] = self.getdTotOpeItem()
        # Obligatorio si existe el campo E725
        # gValorRestaItem['dTotOpeGs'] = self.getdTotOpeGs()

        return gValorRestaItem

    def getgValorItem(self):
        """
        E8.1. Campos que describen el precio, tipo de cambio y valor total de la operación por ítem (E720-E729)
        """
        # NO INFORMAR EN LA NOTA DE REMISION
        gValorItem = {}
        gValorItem['dPUniProSer'] = self.getdPUniProSer()
        gValorItem['dTotBruOpeItem'] = self.getdTotBruOpeItem()
        gValorItem['gValorRestaItem'] = self.getgValorRestaItem()

        # TODO: Verificar cuando se usa en moneda USD cuando es tipo de cambio por item
        # if self.move_id.getdCondTiCam() == 1:
        #     gValorItem['dTiCamIt'] = self.getdTiCamIt()  # OBLIGATORIO SI EL TIPO DE CAMBIO ES POR ITEM

        return gValorItem

    ### FIN GRUPO PRECIOS, DESCUENTOS, VALOR ITEM ###

    ### GRUPO IMPUESTOS ###

    def getiAfecIVA(self):
        # Forma de Afectación Tributaria
        # 1= Gravado IVA
        # 2= Exonerado (Art. 83- Ley 125/91)
        # 3= Exento
        # 4= Gravado parcial (Grav-Exento)
        if self.tax_ids.amount == 0.0000:
            return 3
        elif self.tax_ids.amount == 5.0000:
            return 1
        elif self.tax_ids.amount == 10.0000:
            return 1

    def getdDesAfecIVA(self):
        if self.tax_ids.amount == 0.0000:
            return 'Exento'
        elif self.tax_ids.amount == 5.0000:
            return 'Gravado IVA'
        elif self.tax_ids.amount == 10.0000:
            return 'Gravado IVA'

    def getdPropIVA(self):
        if self.tax_ids.amount == 0.0000:
            return 0
        else:
            return 100

    def getdTasaIVA(self):
        if self.tax_ids.amount == 0.0000:
            return 0
        elif self.tax_ids.amount == 5.0000:
            return 5
        elif self.tax_ids.amount == 10.0000:
            return 10

    def getdBasGravIVA(self):
        precio = self.getdTotOpeItem()
        if self.tax_ids.amount == 0.0000:
            return 0
        elif self.tax_ids.amount == 5.0000:
            base = precio * 1 / 1.05
            return round(base, 8)
        elif self.tax_ids.amount == 10.0000:
            base = precio * 1 / 1.1
            return round(base, 8)

    def getdBasExe(self):
        """
        Nota Técnica 13
        Si E731 = 4 este campo es igual al resultado delcálculo:
        [100 * EA008 * (100 - E733)] / [10000 + (E734 * E733)]
        Si E731 = 1 , 2 o 3 este campo es igual 0
        """
        E731 = self.getiAfecIVA()
        if E731 in [1, 2, 3]:
            return 0
        else:
            return 0

    def getdLiqIVAItem(self):
        """
        E736: Liquidación del IVA por ítem
        1-15p(0-8)
        """
        precio = self.getdTotOpeItem()
        if self.tax_ids.amount == 0.0000:
            return 0
        elif self.tax_ids.amount == 5.0000:
            iva_precio = precio / 21
            return round(iva_precio, 8)
        elif self.tax_ids.amount == 10.0000:
            iva_precio = precio / 11
            return round(iva_precio, 8)

    def getgCamIVA(self):
        """
        E730: Campos que describen el IVA de la operación
        Obligatorio si D013=1, 3, 4 o 5 y C002 ≠ 4 o 7
        No informar si D013=2 y C002= 4 o 7
        """
        gCamIVA = {  # NO INFORMAR EN AUTOFACTURA NI NOTA DE REMISION
            'iAfecIVA': self.getiAfecIVA(),
            'dDesAfecIVA': self.getdDesAfecIVA(),
            'dPropIVA': self.getdPropIVA(),
            'dTasaIVA': self.getdTasaIVA(),
            'dBasGravIVA': self.getdBasGravIVA(),
            'dLiqIVAItem': self.getdLiqIVAItem(),
            'dBasExe': self.getdBasExe(),
        }
        return gCamIVA

    ### FIN GRUPO IMPUESTOS ###

    ### GRUPO RASTREO DE MERCADERIAS ###
    def getdNumLote(self):
        return 0

    def getdVencMerc(self):
        return 0

    def getdNSerie(self):
        return 0

    def getdNumPedi(self):
        return 0

    def getdNumSegui(self):
        return 0

    def getgRasMerc(self):
        gRasMerc = {  # Grupo de rastreo de la mercadería
            'dNumLote': self.getdNumLote(),
            'dVencMerc': self.getdVencMerc(),
            'dNSerie': self.getdNSerie(),
            'dNumPedi': self.getdNumPedi(),
            'dNumSegui': self.getdNumSegui(),
            #'dNomImp': self.getdNomImp(),  # Obligados por la RG N° 16/2019– Agroquímicos
            #'dDirImp': self.getdDirImp(),  # Obligados por la RG N° 16/2019– Agroquímicos
            #'dNumFir': self.getdNumFir(),  # Obligados por la RG N° 16/2019– Agroquímicos
            #'dNumReg': self.getdNumReg(),  # Obligados por la RG N° 16/2019– Agroquímicos
            #'dNumRegEntCom': self.getdNumRegEntCom() # Obligados por la RG N° 16/2019– Agroquímicos
        }
        return gRasMerc

    ### FIN GRUPO RASTREO MERCADERIAS ###
    
    def getdDncpG(self):
        """
        E704:
        Código DNCP - Nivel General
        Obligatorio si D202 = 3
        Informar se existe el código de la DNCP Colocar 0 (cero) a la izquierda para completar los espacios vacíos
        longitud 8
        """
        codigo = self.product_id.codigo_dncp_general or "11111111"
        return codigo.zfill(8)

    def getdDncpE(self):
        """
        E705:
        Código DNCP - Nivel Especifico
        Obligatorio si existe el campo E704
        longitud 3-4
        """
        codigo = self.product_id.codigo_dncp_especifico or "1111"
        return codigo
