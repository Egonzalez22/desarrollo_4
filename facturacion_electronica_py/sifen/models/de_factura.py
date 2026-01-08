import logging

from odoo import _, api, exceptions, models
from datetime import timedelta

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'fe.de']

    def obtener_timbrado(self):
        result = super(AccountMove, self).obtener_timbrado()
        if self.move_type == 'out_invoice' and self.tipo_documento == 'nota_debito':
            return self.obtener_timbrado_de()
        return result

    def getdFeIniT(self):
        timbrado = self.obtener_timbrado_de()
        if timbrado:
            fecha_vigencia = timbrado.inicio_vigencia.strftime('%Y-%m-%d')
            return fecha_vigencia
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido')

    def getdNumTim(self):
        timbrado = self.obtener_timbrado_de()
        if timbrado:
            nro_timbrado = timbrado.name
            return nro_timbrado
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido')

    def getdSerieNum(self):
        timbrado = self.obtener_timbrado_de()
        if timbrado:
            serie = timbrado.serie
            return serie
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido')

    def es_documento_electronico(self):
        """
        Retorna una bandera indicando si el diario del invoice es un documento electronico
        """
        diario = self.journal_id
        if diario:
            return diario.es_documento_electronico

        return False

    def getiTiDE(self):
        """
        C002: Tipo de Documento Electrónico
        1= Factura electrónica
        2= Factura electrónica de exportación
        3= Factura electrónica de importación
        4= Autofactura electrónica
        5= Nota de crédito electrónica
        6= Nota de débito electrónica
        7= Nota de remisión electrónica
        8= Comprobante de retenciónelectrónico
        """
        if self.tipo_documento == 'out_invoice':
            return 1
        if self.tipo_documento == 'out_refund':
            return 5
        if self.tipo_documento == 'nota_remision':
            return 7
        if self.tipo_documento == 'autofactura':
            return 4
        if self.tipo_documento == 'nota_debito':
            return 6

    def getdNumDoc(self):
        return str(self.name.split('-')[2]).zfill(7)

    def getdEst(self):
        timbrado = self.obtener_timbrado_de()
        if timbrado:
            establecimiento = timbrado.nro_establecimiento
            return establecimiento
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido')

    def getdPunExp(self):
        timbrado = self.obtener_timbrado_de()
        if timbrado:
            punto_expedicion = timbrado.nro_punto_expedicion
            return punto_expedicion
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido')

    def cItems(self):
        """
        Retorna la cantidad de items de la factura
        """
        items = self.get_lineas_facturables()
        if items:
            return len(items)
        else:
            return 0

    def getiTImp(self):
        if self.iTImp:
            return self.iTImp
        else:
            raise exceptions.ValidationError("Debe definir un tipo de impuesto afectado")

    def getdDesTImp(self):
        tipo = self.getiTImp()
        tipo = int(tipo) if tipo else False
        if tipo:
            if tipo == 1:
                return 'IVA'
            elif tipo == 2:
                return 'ISC'
            elif tipo == 3:
                return 'Renta'
            elif tipo == 4:
                return 'Ninguno'
            elif tipo == 5:
                return 'IVA - Renta'

    def getiTipTra(self):
        """
        D011
        Obligatorio si C002 = 1 o 4
        No informar si C002 ≠ 1 o 4
        """
        if self.iTipTra:
            return self.iTipTra
        else:
            if self.tipo_documento in ["out_invoice", "autofactura"]:
                raise exceptions.ValidationError("Debe definir un tipo de transacción")

    def getdDesTipTra(self):
        tipo = self.getiTipTra()
        tipo = int(tipo) if tipo else False
        if tipo:
            if tipo == 1:
                return 'Venta de mercadería'
            elif tipo == 2:
                return 'Prestación de servicios'
            elif tipo == 3:
                return 'Mixto (Venta de mercadería y servicios)'
            elif tipo == 4:
                return 'Venta de activo fijo'
            elif tipo == 5:
                return 'Venta de divisas'
            elif tipo == 6:
                return 'Compra de divisas'
            elif tipo == 7:
                return 'Promoción o entrega de muestras'
            elif tipo == 8:
                return 'Donación'
            elif tipo == 9:
                return 'Anticipo'
            elif tipo == 10:
                return 'Compra de productos'
            elif tipo == 11:
                return 'Compra de servicios'
            elif tipo == 12:
                return 'Venta de crédito fiscal'
            elif tipo == 13:
                return 'Muestras médicas'

    def getcMoneOpe(self):
        return self.currency_id.name

    def getdDesMoneOpe(self):
        if self.currency_id.name == 'PYG':
            return "Guarani"
        elif self.currency_id.name == 'USD':
            return "US Dollar"
        return self.currency_id.currency_unit_label

    def getdCondTiCam(self):
        if self.currency_id.name != 'PYG':
            return 1

    def getdTiCam(self):
        if self.getdCondTiCam() == 1:
            return self.obtener_cotizacion()

    def getiCondAnt(self):
        """
        D019
        Condición del Anticipo
        1 = Anticipo Global (un solo tipo de anticipo para todo el DE)
        2 = Anticipo por ítem (corresponde a la distribución de Anticipos facturados por ítem)

        Solo se implementó el anticipo global
        """
        return 1 if self.facturas_anticipo_asociadas else False

    def getdDesCondAnt(self):
        """
        D020
        Descripción de la condición del Anticipo
        """
        if self.getiCondAnt():
            return "Anticipo Global"
        else:
            False

    
    def tiene_descuento_global(self):
        # TODO: Se comento esta funcion porque el descuento y anticipo se manejó de otra forma
        # Queda comentado temporalmente hasta asegurar que no se va a usar mas 02-08-24

        #     tiene_desc_linea = any(self.get_lineas_facturables().filtered(lambda x: x.discount > 0))
        #     tiene_desc_global = any(self.get_lineas_facturables().filtered(lambda x: x.price_total < 0)) and not self.factura_anticipo_id
        #     if tiene_desc_linea and tiene_desc_global:
        #         raise exceptions.ValidationError("No se puede tener descuentos en las lineas y y también un descuento global")
        #     if tiene_desc_linea:
        #         return 2
        #     else:
        #         if tiene_desc_global:
        #             return 1
        #         else:
        #             return False
        
        lineas = self.get_lineas_descuentos_globales()
        if lineas:
            return True
        else:
            return False

    def getGlobalDiscAntPercent(self):
        """
        Retorna el porcentaje que se debe utilizar para calcular los descuentos y anticipos globales por cada linea de la factura
        """
        items = self.get_lineas_facturables().filtered(lambda x: x.price_total > 0)

        # Suma de todos los items iva incluido
        monto_items = sum([(line.quantity * line.price_unit) for line in items])

        # Obtenemos el total del descuento y/o anticipo
        # TODO: Ver si se puede hacer con mas de una factura de anticipo
        monto_negativo = 0 

        # Total de los anticipos
        lineas_anticipo = self.get_lineas_anticipo()
        if lineas_anticipo:
            monto_negativo += abs(sum(lineas_anticipo.mapped('price_total')))

        # Total de los descuentos globales
        lineas_descuentos = self.get_lineas_descuentos_globales()
        if lineas_descuentos:
            monto_negativo += abs(sum(lineas_descuentos.mapped('price_total')))

        anticipo_porc = (monto_negativo * 100) / monto_items

        return anticipo_porc

    def getgOpeCom(self):
        """
        D1. Campos inherentes a la operación comercial (D010-D099)
        """
        # EN CASO DE QUE SEA UNA NOTA DE REMISIÓN NO INFORMAR
        gOpeCom = {}

        if self.getiTiDE() == 1 or self.getiTiDE() == 4:
            gOpeCom['iTipTra'] = self.getiTipTra()  # NO INFORMAR EN CASO DE LAS NOTAS
            gOpeCom['dDesTipTra'] = self.getdDesTipTra()  # NO INFORMAR EN CASO DE LAS NOTAS

        gOpeCom['iTImp'] = self.getiTImp()
        gOpeCom['dDesTImp'] = self.getdDesTImp()
        gOpeCom['cMoneOpe'] = self.getcMoneOpe()
        gOpeCom['dDesMoneOpe'] = self.getdDesMoneOpe()
        # OBLIGATORIO SI LA MONEDA ES DIFERENTE A PYG
        if self.currency_id.name != 'PYG':
            gOpeCom['dCondTiCam'] = self.getdCondTiCam()
            gOpeCom['dTiCam'] = self.getdTiCam()

        if self.getiCondAnt():
            gOpeCom['iCondAnt'] = self.getiCondAnt()  # SOLO SI HAY ANTICIPO
            gOpeCom['dDesCondAnt'] = self.getdDesCondAnt()  # SOLO SI HAY ANTICIPO

        return gOpeCom

    ### GRUPO FACTURA ELECTRÓNICA ###

    def getiIndPres(self):
        if self.indicador_presencia:
            return self.indicador_presencia
        else:
            raise exceptions.ValidationError('Debe definir el indicador de presencia de la Factura Electrónica')

    def getdDesIndPres(self):
        if self.indicador_presencia:
            if self.getiIndPres() == '1':
                return 'Operación presencial'
            elif self.getiIndPres() == '2':
                return 'Operación electrónica'
            elif self.getiIndPres() == '3':
                return 'Operación telemarketing'
            elif self.getiIndPres() == '4':
                return 'Venta a domicilio'
            elif self.getiIndPres() == '5':
                return 'Operación bancaria'
            elif self.getiIndPres() == '5':
                return 'Operación cíclica'
        else:
            raise exceptions.ValidationError('Debe definir el indicador de presencia de la Factura Electrónica')

    def getdFecEmNR(self):
        return self.fecha_remision.strftime('%Y-%m-%d') if self.fecha_remision else ""

    def getdModCont(self):
        """
        E021:
        Modalidad - Código emitido por la DNCP
        longitud 2
        """
        codigo = self.dncp_cod_modalidad or "11"
        return codigo.zfill(2)

    def getdEntCont(self):
        """
        E022:
        Entidad - Código emitido por la DNCP
        longitud 5
        """
        codigo = self.dncp_cod_entidad or "11111"
        return codigo.zfill(5)

    def getdAnoCont(self):
        """
        E023:
        Año - Código emitido por la DNCP
        longitud 2
        """
        codigo = self.dncp_cod_anho or "11"
        return codigo.zfill(2)

    def getdSecCont(self):
        """
        E024:
        Secuencia - emitido por la DNCP
        longitud 7
        """
        codigo = self.dncp_cod_sec or "1111111"
        return codigo.zfill(7)

    def getdFeCodCont(self):
        """
        E025:
        Fecha de emisión del código de contratación por la DNCP
        Fecha en el formato: AAAA-MM-DD.
        Esta fecha debe ser anterior a la fecha de emisión de la FE
        longitud 10
        """
        invoice_date = (self.invoice_date - timedelta(days=1))
        fecha_emision = self.dncp_fecha_emision or invoice_date
        fecha_str = fecha_emision.strftime('%Y-%m-%d')

        return fecha_str


    def getgCamFE(self):
        gCamFE = {  # FACTURA ELECTRONICA
            'iIndPres': self.getiIndPres(),
            'dDesIndPres': self.getdDesIndPres(),
            # 'dFecEmNR': self.getdFecEmNR(),
        }
        if self.getiTiOpe() == '3':
            gCompPub = {  # OBLIGATORIO SI EL TIPO DE OPERACION ES B2G
                'dModCont': self.getdModCont(),
                'dEntCont': self.getdEntCont(),
                'dAnoCont': self.getdAnoCont(),
                'dSecCont': self.getdSecCont(),
                'dFeCodCont': self.getdFeCodCont(),
            }
            gCamFE['gCompPub'] = gCompPub
        return gCamFE

    ### FIN DEL GRUPO FACTURA ELECTRÓNICA ###

    # def getgTransp(self):
    #     """
    #     E10. Campos que describen el transporte de las mercaderías (E900-E999)
    #     """
    #     gTransp = {
    #         'iTipTrans': self.getiTipTrans(),
    #         'dDesTipTrans': self.getdDesTipTrans(),
    #         'iModTrans': self.getiModTrans(),
    #         'dDesModTrans': self.getdDesModTrans(),
    #         'iRespFlete': self.getiRespFlete(),
    #         'cCondNeg': self.getcCondNeg(),
    #         'dNuManif': self.getdNuManif(),
    #         'dNuDespImp': self.getdNuDespImp(),
    #         'dIniTras': self.getdIniTras(),
    #         'dFinTras': self.getdFinTras(),
    #         'cPaisDest': self.getcPaisDest(),
    #         'dDesPaisDest': self.getdDesPaisDest(),
    #         'gCamSal': self.getgCamSal(),
    #         'gCamEnt': self.getgCamEnt(),
    #         'gVehTras': self.getgVehTras(),
    #         'gCamTrans': self.getgCamTrans(),
    #     }
    #     return gTransp

    # def getgCamSal(self):
    #     """
    #     E10.1. Campos que identifican el local de salida de las mercaderías (E920-E939)
    #     """
    #     gCamSal = {
    #         'dDirLocSal': self.getdDirLocSal(),
    #         'dNumCasSal': self.getdNumCasSal(),
    #         'dComp1Sal': self.getdComp1Sal(),
    #         'dComp2Sal': self.getdComp2Sal(),
    #         'cDepSal': self.getcDepSal(),
    #         'dDesDepSal': self.getdDesDepSal(),
    #         'cDisSal': self.getcDisSal(),
    #         'dDesDisSal': self.getdDesDisSal(),
    #         'cCiuSal': self.getcCiuSal(),
    #         'dDesCiuSal': self.getdDesCiuSal(),
    #         'dTelSal': self.getdTelSal(),
    #     }
    #     return gCamSal

    # def getgCamEnt(self):
    #     """
    #     E10.2. Campos que identifican el local de entrega de las mercaderías (E940-E959)
    #     """
    #     gCamEnt = {
    #         'dDirLocEnt': self.getdDirLocEnt(),
    #         'dNumCasEnt': self.getdNumCasEnt(),
    #         'dComp1Ent': self.getdComp1Ent(),
    #         'dComp2Ent': self.getdComp2Ent(),
    #         'cDepEnt': self.getcDepEnt(),
    #         'dDesDepEnt': self.getdDesDepEnt(),
    #         'cDisEnt': self.getcDisEnt(),
    #         'dDesDisEnt': self.getdDesDisEnt(),
    #         'cCiuEnt': self.getcCiuEnt(),
    #         'dDesCiuEnt': self.getdDesCiuEnt(),
    #         'dTelEnt': self.getdTelEnt(),
    #     }
    #     return gCamEnt

    # def getgVehTras(self):
    #     gVehTras = {
    #         'dTiVehTras': self.getdTiVehTras(),
    #         'dMarVeh': self.getdMarVeh(),
    #         'dTipIdenVeh': self.getdTipIdenVeh(),
    #         'dNroIDVeh': self.getdNroIDVeh(),
    #         'dAdicVeh': self.getdAdicVeh(),
    #         'dNroMatVeh': self.getdNroMatVeh(),
    #         'dNroVuelo': self.getdNroVuelo(),
    #     }
    #     return gVehTras

    # def getgCamTrans(self):
    #     gCamTrans = {
    #         'iNatTrans': self.getiNatTrans(),
    #         'dNomTrans': self.getdNomTrans(),
    #         'dRucTrans': self.getdRucTrans(),
    #         'dDVTrans': self.getdDVTrans(),
    #         'iTipIDTrans': self.getiTipIDTrans(),
    #         'dDTipIDTrans': self.getdDTipIDTrans(),
    #         'dNumIDTrans': self.getdNumIDTrans(),
    #         'cNacTrans': self.getcNacTrans(),
    #         'dDesNacTrans': self.getdDesNacTrans(),
    #         'dNumIDChof': self.getdNumIDChof(),
    #         'dNomChof': self.getdNomChof(),
    #         'dDomFisc': self.getdDomFisc(),
    #         'dDirChof': self.getdDirChof(),
    #         'dNombAg': self.getdNombAg(),
    #         'dRucAg': self.getdRucAg(),
    #         'dDVAg': self.getdDVAg(),
    #         'dDirAge': self.getdDirAge(),
    #     }
    #     return gCamTrans

    ### CONDICIÓN DE LA OPERACIÓN ###
    def getiCondOpe(self):
        """
        E601:
        1= Contado 2= Crédito
        """
        if self.invoice_date == self.invoice_date_due:
            return 1
        elif self.invoice_payment_term_id.id != self.env.ref('account.account_payment_term_immediate').id:
            return 2
        else:
            return 2

    def getdDCondOpe(self):
        """
        E602:
        Referente al campo E601
        1= “Contado”
        2= “Crédito
        """
        if self.invoice_date == self.invoice_date_due:
            return 'Contado'
        elif self.invoice_payment_term_id.id != self.env.ref('account.account_payment_term_immediate').id:
            return 'Crédito'
        else:
            return 'Crédito'

    ### FIN DE LA CONDICIÓN DE LA OPERACIÓN ###

    def getgDtipDE_factura(self):
        xml = {}
        xml['gCamFE'] = self.getgCamFE()
        xml['gCamCond'] = {'iCondOpe': self.getiCondOpe(), 'dDCondOpe': self.getdDCondOpe()}

        xml['gCamItem'] = []

        lineas_facturables = self.get_lineas_facturables()
        for line in lineas_facturables:
            xml['gCamItem'].append(line.getgCamItem())

        # 1 = Contado, 2 = Crédito
        if self.getiCondOpe() == 1:
            xml['gCamCond']['gPaConEIni'] = self.getgPaConEIni()
        else:
            xml['gCamCond']['gPagCred'] = self.getgPagCred()

        """if self.getgCamEsp():  # Campos complementarios comerciales de uso especifico
            xml['gCamEsp'] = self.getgCamEsp()

        if self.getgCamGen():
            xml['gCamGen'] = self.getgCamGen()"""

        return xml
