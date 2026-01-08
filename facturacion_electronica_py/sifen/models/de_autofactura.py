from odoo import _, api, exceptions, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    naturaleza_vendedor = fields.Selection(
        string="Naturaleza del vendedor",
        selection=[
            ('1', 'No contribuyente'),
            ('2', 'Extranjero'),
        ],
    )

    # def action_post(self):
    #     res = super(AccountMove, self).action_post()
    #     for rec in self:
    #         # Si es documento electronico, agregamos las validaciones para autofactura
    #         # if rec.es_documento_electronico() and rec.move_type in ['in_invoice'] and rec.tipo_documento == 'autofactura':
    #         if rec.move_type in ['in_invoice'] and rec.tipo_documento == 'autofactura':
    #             self.preparar_documento_electronico()

    #     return res

    def getgCamAE(self):
        gCamAE = {}

        # E301: Naturaleza del vendedor 1:1
        gCamAE['iNatVen'] = self.getiNatVen()

        # E302: Descripción de la naturaleza del vendedor 1:1
        gCamAE['dDesNatVen'] = self.getdDesNatVen()

        # E304: Tipo de documento de identidad del vendedor 1:1
        gCamAE['iTipIDVen'] = self.getiTipIDVen()

        # E305: Descripción del tipo de documento de identidad del vendedor 1:1
        gCamAE['dDTipIDVen'] = self.getdDTipIDVen()

        # E306: Número de documento de identidad del vendedor 1:1
        gCamAE['dNumIDVen'] = self.getdNumIDVen()

        # E307: Nombre y apellido del vendedor 1:1
        gCamAE['dNomVen'] = self.getdNomVen()

        # E308: Dirección del vendedor 1:1
        gCamAE['dDirVen'] = self.getdDirVen()

        # E309: Número de casa del vendedor 1:1
        gCamAE['dNumCasVen'] = self.getdNumCasVen()

        # E310: Código de departamento del vendedor 1:1
        gCamAE['cDepVen'] = self.getcDepVen()

        # E311: Descripción del departamento del vendedor 1:1
        gCamAE['dDesDepVen'] = self.getdDesDepVen()

        # E312: Código de distrito del vendedor 0:1
        gCamAE['cDisVen'] = self.getcDisVen()

        # E313: Descripción del distrito del vendedor 0:1
        gCamAE['dDesDisVen'] = self.getdDesDisVen()

        # E314: Código de ciudad del vendedor 1:1
        gCamAE['cCiuVen'] = self.getcCiuVen()

        # E315: Descripción de la ciudad del vendedor 1:1
        gCamAE['dDesCiuVen'] = self.getdDesCiuVen()

        # E316: Lugar de la transacción, dirección donde se provee el servicio o producto 1:1
        gCamAE['dDirProv'] = self.getdDirProv()

        # E317: Código de departamento donde se provee el servicio o producto 1:1
        gCamAE['cDepProv'] = self.getcDepProv()

        # E318: Descripción del departamento donde se realiza la transacción 1:1
        gCamAE['dDesDepProv'] = self.getdDesDepProv()

        # E319: Código de distrito donde se realiza la transacción 0:1
        gCamAE['cDisProv'] = self.getcDisProv()

        # E320: Descripción del distrito donde se realiza la transacción 0:1
        gCamAE['dDesDisProv'] = self.getdDesDisProv()

        # E321: Código de ciudad donde se realiza la transacción 1:1
        gCamAE['cCiuProv'] = self.getcCiuProv()

        # E322: Descripción de la ciudad donde se realiza la transacción 1:1
        gCamAE['dDesCiuProv'] = self.getdDesCiuProv()

        return gCamAE

    def getiNatVen(self):
        if self.naturaleza_vendedor:
            return int(self.naturaleza_vendedor)

    def getdDesNatVen(self):
        if self.naturaleza_vendedor:
            if self.naturaleza_vendedor == '1':
                return "No contribuyente"
        elif self.naturaleza_vendedor == '2':
            return "Extranjero"
        return False

    def getiTipIDVen(self):
        if self.partner_id and self.partner_id.tipo_documento:
            return int(self.partner_id.tipo_documento)
        return 1

    def getdDTipIDVen(self):
        tipo_documento = self.getiTipIDVen()
        if tipo_documento == 1:
            return "Cédula paraguaya"
        elif tipo_documento == 2:
            return "Pasaporte"
        elif tipo_documento == 3:
            return "Cédula extranjera"
        elif tipo_documento == 4:
            return "Carnet de residencia"
        return "Cédula paraguaya"

    def getdNumIDVen(self):
        """
        Número de documento de identidad del vendedor
        """
        if self.partner_id and self.partner_id.nro_documento:
            return self.partner_id.nro_documento

        msg = "El número de documento de identidad del vendedor es obligatorio"
        self.log_errors(None, "getdNumIDVen", True, msg)

    def getdNomVen(self):
        if self.partner_id:
            return self.partner_id.name
        return

    def getdDirVen(self):
        # TODO: En caso de extranjeros, colocar la dirección en donde se realizó la transacción
        if self.partner_id and self.partner_id.street:
            return self.partner_id.street
        else:
            return self.company_id.street

    def getdNumCasVen(self):
        return 0

    def getcDepVen(self):
        if self.partner_id and self.partner_id.state_id and self.partner_id.country_id.code == 'PY':
            return self.partner_id.state_id.code
        else:
            return self.company_id.state_id.code

    def getdDesDepVen(self):
        if self.partner_id and self.partner_id.state_id and self.partner_id.country_id.code == 'PY':
            return self.partner_id.state_id.name
        else:
            return self.company_id.state_id.name

    def getcDisVen(self):
        if self.partner_id and self.partner_id.city_id and self.partner_id.country_id.code == 'PY':
            return self.partner_id.city_id.district_id.code
        else:
            return self.company_id.city_id.district_id.code

    def getdDesDisVen(self):
        if self.partner_id and self.partner_id.city_id and self.partner_id.country_id.code == 'PY':
            return self.partner_id.city_id.district_id.name
        else:
            return self.company_id.city_id.district_id.name

    def getcCiuVen(self):
        if self.partner_id and self.partner_id.city_id and self.partner_id.country_id.code == 'PY':
            return self.partner_id.city_id.code
        else:
            return self.company_id.city_id.code

    def getdDesCiuVen(self):
        if self.partner_id and self.partner_id.city_id and self.partner_id.country_id.code == 'PY':
            return self.partner_id.city_id.name
        else:
            return self.company_id.city_id.name

    def getdDirProv(self):
        return self.company_id.street

    def getcDepProv(self):
        return self.company_id.state_id.code

    def getdDesDepProv(self):
        return self.company_id.state_id.name

    def getcDisProv(self):
        return self.company_id.city_id.district_id.code

    def getdDesDisProv(self):
        return self.company_id.city_id.district_id.name

    def getcCiuProv(self):
        return self.company_id.city_id.code

    def getdDesCiuProv(self):
        return self.company_id.city_id.name

    def getgDtipDE_autofactura(self):
        xml = {}
        xml['gCamAE'] = self.getgCamAE()
        xml['gCamCond'] = {'iCondOpe': self.getiCondOpe(), 'dDCondOpe': self.getdDCondOpe()}

        xml['gCamItem'] = []
        for line in self.get_lineas_facturables().sorted(key=lambda r: r.price_total):
            if line.quantity > 0 and line.price_unit > 0:
                xml['gCamItem'].append(line.getgCamItem())

        # 1 = Contado, 2 = Crédito
        if self.getiCondOpe() == 1:
            # Factura Contado
            xml['gCamCond']['gPaConEIni'] = self.getgPaConEIni()
        else:
            raise exceptions.ValidationError("La autofactura sólo permite término Contado")

        """if self.getgCamEsp():  # Campos complementarios comerciales de uso especifico
            xml['gCamEsp'] = self.getgCamEsp()

        if self.getgCamGen():
            xml['gCamGen'] = self.getgCamGen()"""

        return xml