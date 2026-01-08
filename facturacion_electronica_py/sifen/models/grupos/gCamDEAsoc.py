import datetime

import json,pytz
from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    doc_asociado=fields.Char(string="Documento asociado",readonly=True,copy=False)

    ### DOCUMENTO ASOCIADO ###
    def getdNTimDI(self, factura):
        timbrado = factura.journal_id.timbrados_ids.filtered(lambda x: x.active and x.tipo_documento == factura.tipo_documento)
        dNTimDI = timbrado.name
        return dNTimDI

    def getdEstDocAso(self, factura):
        timbrado = factura.journal_id.timbrados_ids.filtered(lambda x: x.active and x.tipo_documento == factura.tipo_documento)
        dEst = timbrado.nro_establecimiento  # Establecimiento
        return dEst

    def getdPExpDocAso(self, factura):
        timbrado = factura.journal_id.timbrados_ids.filtered(lambda x: x.active and x.tipo_documento == factura.tipo_documento)
        dPunExp = timbrado.nro_punto_expedicion  # Establecimiento
        return dPunExp

    def getdNumDocAso(self, factura):
        return str(factura.name.split('-')[2]).zfill(7)

    def getiTipoDocAso(self, factura):
        if factura.tipo_documento == 'out_invoice':
            iTipoDocAso = 1
        elif factura.tipo_documento == 'out_refund':
            iTipoDocAso = 2
        elif factura.tipo_documento == 'nota_debito':
            iTipoDocAso = 3
        return iTipoDocAso

    def getiTipoDocAso(self, factura):
        if factura.tipo_documento == 'out_invoice':
            iTipoDocAso = 1
        elif factura.tipo_documento == 'out_refund':
            iTipoDocAso = 2
        elif factura.tipo_documento == 'nota_debito':
            iTipoDocAso = 3
        return iTipoDocAso

    def getdDTipoDocAso(self, factura):
        if factura.tipo_documento == 'out_invoice':
            dDTipoDocAso = 'Factura'
        elif factura.tipo_documento == 'out_refund':
            dDTipoDocAso = 'Nota de crédito'
        elif factura.tipo_documento == 'nota_debito':
            dDTipoDocAso = 'Nota de débito'
        return dDTipoDocAso

    def getiTipDocAso(self, factura):  # Tipo de documento asociado
        """
        H002
        1 = Electrónico
        2 = Impreso
        3 = Constancia Electrónica
        """
        if factura.cdc:
            iTipDocAso = 1
        else:
            iTipDocAso = 2
        return iTipDocAso

    def getdDesTipDocAso(self, iTipDocAso):  # Descripción tipo de documento asociado
        """
        H003
        1 = Electrónico
        2 = Impreso
        3 = Constancia Electrónica
        """
        if iTipDocAso == 1:
            return 'Electrónico'
        elif iTipDocAso == 2:
            return 'Impreso'
        elif iTipDocAso == 3:
            return 'Constancia Electrónica'

    def getdCdCDERef(self, factura):
        dCdCDERef = factura.cdc
        return dCdCDERef

    def getgCamDEAsoc(self):
        """
        H. Campos que identifican al documento asociado (H001-H049)
        gCamDEAsoc: Se puede agregar de 0 a 99 documentos
        """
        gCamDEAsoc = False
        facturas = False

        # Si es autofactura, retornamos directo 
        if self.tipo_documento == 'autofactura':
            # TODO: Esto falta revisar cuando iTipCons es para microproductores
            gCamDEAsoc = [{
                'iTipDocAso': 3,
                'dDesTipDocAso': "Constancia Electrónica",
                'iTipCons': 1,
                'dDesTipCons': "Constancia de no ser contribuyente",
            }]
            return gCamDEAsoc
            
        # Facturas asociadas para NC - ND (Esto no se usa, se usa el campo nro_factura_asociada)
        # TODO: Verificar si se puede eliminar
        if self.reversed_entry_id:
            facturas = [self.reversed_entry_id]
        # Anticipo para facturas de venta
        elif self.facturas_anticipo_asociadas:
            facturas = self.facturas_anticipo_asociadas
        # Facturas asociadas para NC - ND
        elif self.nro_factura_asociada:
            facturas = [self.nro_factura_asociada]
        # Notas de remisión asociadas a facturas de venta
        elif self.nota_remision_asociadas:
            facturas = self.nota_remision_asociadas
        
        # Si hay facturas iteramos para poder generar el documento asociado
        if facturas:
            gCamDEAsoc = []

            for factura in facturas:
                iTipDocAso = self.getiTipDocAso(factura)
                gCamDEAsoc_dict = {
                    'iTipDocAso': iTipDocAso,
                    'dDesTipDocAso': self.getdDesTipDocAso(iTipDocAso),
                    # 'dNumComRet':self.getdNumComRet(), Es Opcional informar Numero de Comprobante de Retención
                }

                # Si el documento asociado es un DE, le pasamos su CDC
                if factura.fe_valida:
                    gCamDEAsoc_dict['dCdCDERef'] = self.getdCdCDERef(factura)
                # Si no es, le pasamos los datos de la factura
                else:
                    gCamDEAsoc_dict['dNTimDI'] = self.getdNTimDI(factura)
                    gCamDEAsoc_dict['dEstDocAso'] = self.getdEstDocAso(factura)
                    gCamDEAsoc_dict['dPExpDocAso'] = self.getdPExpDocAso(factura)
                    gCamDEAsoc_dict['dNumDocAso'] = self.getdNumDocAso(factura)
                    gCamDEAsoc_dict['iTipoDocAso'] = self.getiTipoDocAso(factura)
                    gCamDEAsoc_dict['dDTipoDocAso'] = self.getdDTipoDocAso(factura)
                    gCamDEAsoc_dict['dFecEmiDI'] = factura.invoice_date.strftime('%Y-%m-%d')
                if self.getiTipTra() == 12:
                    gCamDEAsoc_dict['dNumResCF'] = self.getdNumResCF(factura)

                gCamDEAsoc.append(gCamDEAsoc_dict)
        elif not facturas and self.doc_asociado:
            gCamDEAsoc = []
            gCamDEAsoc_dict=json.loads(self.doc_asociado)
            gCamDEAsoc.append(gCamDEAsoc_dict)
           
        return gCamDEAsoc

    ### FIN DOCUMENTO ASOCIADO ###
