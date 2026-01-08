from odoo import _, api, exceptions, fields, models


class DocumentoElectronico(models.AbstractModel):
    _inherit = "fe.de"

    def getgOpeDE(self):
        # facturas_exportacion/models/de.py

        res = super().getgOpeDE()

        # si es out_invoice y si es de exportacion
        if self.tipo_documento == "out_invoice" and self.es_factura_exportacion:
            res["dInfoFisc"] = self.getInfoFiscExportacion()

        return res

    def debug_mode(self, xmldict):
        # facturas_exportacion/models/de.py

        DE = xmldict['rDE']['DE']

        # Solamente si no es factura de exportacion
        if self.tipo_documento == "out_invoice" and not self.es_factura_exportacion:
            DE['gOpeDE']["dInfoFisc"] = "Información de interés del Fisco respecto al DE"

        DE['gDatGralOpe']['gEmis']['dNomEmi'] = 'DE generado en ambiente de prueba - sin valor comercial ni fiscal'

        items = DE['gDtipDE']["gCamItem"]
        for item in items:
            item["dDesProSer"] = 'DE generado en ambiente de prueba - sin valor comercial ni fiscal'

    def getInfoFiscExportacion(self):
        """
        En caso de realizar Factura
        Exportación, en este campo en
        la FE se debe completar con los
        siguientes datos y en este orden
        de conformidad al Art 20
        numeral 15 del Decreto N°
        """
        txt = ""
        txt += self.export_tipo_operacion or ""
        txt += ";"
        txt += self.export_condicion_negociacion or ""
        txt += ";"
        txt += self.export_pais_destino.name or ""
        txt += ";"
        txt += self.export_exportador_nacional.name or ""
        txt += ";"
        txt += self.export_agente_transporte.name or ""
        txt += ";"
        txt += self.export_instruccion_pago or ""
        txt += ";"
        txt += self.export_numero_embarque or ""
        txt += ";"
        txt += self.export_numero_manifiesto or ""
        txt += ";"
        txt += self.export_numero_barcaza or ""
        txt += ";"
        txt += self.export_informacion_adicional or ""

        return txt
