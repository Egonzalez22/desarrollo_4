from odoo import _, api, fields, models, exceptions
import re

class NotasRemisionAccount(models.Model):
    _name = 'notas_remision_account.nota.remision'
    _inherit = ['notas_remision_account.nota.remision', 'fe.de']

    iMotEmiNR = fields.Selection(string="Motivo de traslado", selection=[
        ('1', 'Traslado por venta'),
        ('2', 'Traslado por consignación'),
        ('3', 'Exportación'),
        ('4', 'Traslado por compra'),
        ('5', 'Importación'),
        ('6', 'Traslado por devolución'),
        ('7', 'Traslado entre locales de la empresa'),
        ('8', 'Traslado de bienes por transformación'),
        ('9', 'Traslado de bienes por reparación'),
        ('10', 'Traslado por emisor móvil'),
        ('11', 'Exhibición o demostración'),
        ('12', 'Participación en ferias'),
        ('13', 'Traslado de encomienda'),
        ('14', 'Decomiso'),
        ('99', 'Otro'),

    ],)
    iRespEmiNR = fields.Selection(string="Responsable de la emisión", selection=[
        ('1', 'Emisor de la factura'),
        ('2', 'Poseedor de la factura y bienes'),
        ('3', 'Empresa transportista'),
        ('4', 'Despachante de Aduanas'),
        ('5', 'Agente de transporte o intermediario'),
    ])
    kmr = fields.Integer(string="Kms recorridos", default=0)
    dFecEm = fields.Date(string="Fecha futura de la emision de la factura", default=lambda self:fields.Date.today())
    iTipTrans = fields.Selection(string="Tipo de transporte", selection=[
                                 ('1', 'Propio'), ('2', 'Tercero')])
    iModTrans = fields.Selection(string="Modalidad del transporte", selection=[
        ('1', 'Terrestre'),
        ('2', 'Fluvial'),
        ('3', 'Aereo'),
        ('4', 'Multimodal'),
    ], default='1')
    iRespFlete = fields.Selection(string="Responsable del costo del flete", selection=[
        ('1', 'Emisor de la Factura Electrónica'),
        ('2', 'Receptor de la Factura Electrónica'),
        ('3', 'Tercero'),
        ('4', 'Agente intermediario del transporte'),
    ], default='1')

    dTipIdenVeh = fields.Selection(string="Tipo de ident. del vehiculo", selection=[('1', 'Número de identificación del vehículo'),
                                                                                    ('2', 'Número de matrícula del vehículo')])
    dNroIDVeh = fields.Char(string="Nro. de identificación del vehículo")
    dNroVuelo = fields.Char(string="Nro. de vuelo")

    transportista_id = fields.Many2one('res.partner', string="Transportista")
    chofer_id = fields.Many2one('res.partner', string="Chofer")
    # transportista_contribuyente=fields.Boolean(string="Es contribuyente",related="transportista_id.contribuyente")
    ruc_transportista = fields.Char(
        string="RUC del transportista", related="transportista_id.vat")
    direccion_transportista=fields.Char(string="Dirección del transportista",compute="compute_direccion_transp",store=True)
    ruc_chofer = fields.Char(
        string="RUC del chofer", compute="compute_documento_chofer",store=True)
    
    @api.depends('transportista_id')
    def compute_direccion_transp(self):
        if self.transportista_id:
            self.direccion_transportista=self.transportista_id.street

    @api.depends('chofer_id')
    def compute_documento_chofer(self):
        for i in self:
            if i.chofer_id:
                i.ruc_chofer=i.chofer_id.vat or i.chofer_id.nro_documento
            else:
                i.ruc_chofer=False

    @api.onchange('iTipTrans')
    def onchange_iTipTrans(self):
        if self.iTipTrans and self.iTipTrans=='1':
            self.transportista_id=self.env.company.partner_id
            if self.direccion_partida in ["", False]:
                self.direccion_partida=self.env.company.partner_id.street

    @api.onchange('dFecEm')
    def onchange_dFecEm(self):
        if self.dFecEm:
            self.fecha_inicio_traslado = self.dFecEm
            self.fecha_fin_traslado = self.dFecEm

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.direccion_entrega = self.partner_id.street
            self.ciudad_entrega = self.partner_id.city_id.name if self.partner_id.city_id else False
            self.departamento_entrega = self.partner_id.state_id.name if self.partner_id.state_id else False

    def button_inutilizar_remision(self):
        numero=self.name.split('-')
        if len(numero)==3:
            numero=numero[2]
            self.inutilizar_factura(numero, numero,'Inutilizar nr')

        return

    def cItems(self):
        if self.line_ids:
            return len(self.line_ids)
        return 0

    def button_cancelar(self):
        res=super(NotasRemisionAccount,self).button_cancelar()
  
        for i in self:
            if i.es_documento_electronico():
                if i.estado_set == 'aprobado': 
                    i.cancelar_factura('Cancelacion de remision')

                    # Si tiene invoice_id, eliminamos la relacion
                    if i.invoice_id:
                        i.invoice_id.write({"nota_remision_asociadas": [(3, i.id)]})

                else:
                    raise exceptions.ValidationError('Solo se pueden cancelar documentos aprobados')

        return res


    def button_confirmar(self):
        if not self.line_ids:
            raise exceptions.ValidationError("Debe cargar las lineas de la Nota de remisión")
        res = super(NotasRemisionAccount, self).button_confirmar()
        if self.es_documento_electronico():
            for rec in self:
                rec.tipo_documento = "nota_remision"
                rec.preparar_documento_electronico()

                # Si tiene invoice_id, agregamos en el campo de nota_remision_asociadas
                if rec.invoice_id:
                    rec.invoice_id.write({"nota_remision_asociadas": [(4, rec.id)]})

        return res


    def getgOpeCom(self):
        return False

    def es_documento_electronico(self):
        """
        Retorna una bandera indicando si el diario del invoice es un documento electronico
        """
        diario = self.journal_id
        if diario:
            return diario.es_documento_electronico

        return False

    def getiTiDE(self):
        return 7

    def getdNumDoc(self):
        return str(self.name.split('-')[2]).zfill(7)

    def getdEst(self):
        timbrado = self.obtener_timbrado_de(move_type="nota_remision")
        if timbrado:
            establecimiento = timbrado.nro_establecimiento
            return establecimiento
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido')

    def getdPunExp(self):
        timbrado = self.obtener_timbrado_de(move_type="nota_remision")
        if timbrado:
            punto_expedicion = timbrado.nro_punto_expedicion
            return punto_expedicion
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido')

    def getdNumTim(self):
        timbrado = self.obtener_timbrado_de(move_type="nota_remision")
        if timbrado:
            nro_timbrado = timbrado.name
            return nro_timbrado
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido')

    def getdSerieNum(self):
        timbrado = self.obtener_timbrado_de(move_type="nota_remision")
        if timbrado:
            serie = timbrado.serie
            return serie
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido')

    def getdFeIniT(self):
        timbrado = self.obtener_timbrado_de(move_type="nota_remision")
        if timbrado:
            fecha_vigencia = timbrado.inicio_vigencia.strftime('%Y-%m-%d')
            return fecha_vigencia
        else:
            raise exceptions.ValidationError('Debe definir un timbrado válido')

    def getgDatRec(self):
        gDatRec = {}
        # TODO: Se sobreescriben todos los campos temporalmente por problemas del orden, verificar si se puede mejorar
        gDatRec['iNatRec'] = self.getiNatRec()
        gDatRec['iTiOpe'] = self.getiTiOpe()
        gDatRec['cPaisRec'] = self.getcPaisRec()
        gDatRec['dDesPaisRe'] = self.getdDesPaisRe()
        # INFORMAR SOLO SI EL CLIENTE ES CONTRIBUYENTE
        if self.getiNatRec() == 1:
            gDatRec['iTiContRec'] = self.getiTiContRec()
            gDatRec['dRucRec'] = self.getdRucRec()
            gDatRec['dDVRec'] = self.getdDVRec()
        else:
            gDatRec['iTipIDRec'] = self.getiTipIDRec()
            gDatRec['dDTipIDRec'] = self.getdDTipIDRec()
            gDatRec['dNumIDRec'] = self.getdNumIDRec()
        gDatRec['dNomRec'] = self.getdNomRec()

        gDatRec['dDirRec'] = self.direccion_entrega or 'Sin dirección'
        gDatRec['dNumCasRec'] = 0
        if self.partner_id.state_id:
            gDatRec['cDepRec'] = self.partner_id.state_id.code
            gDatRec['dDesDepRec'] = self.partner_id.state_id.name
        else:
            gDatRec['cDepRec'] = 1
            gDatRec['dDesDepRec'] = 'CAPITAL'
        if self.partner_id.city_id:
            gDatRec['cCiuRec'] = self.partner_id.city_id.code
            gDatRec['dDesCiuRec'] = self.partner_id.city_id.name
        else:
            gDatRec['cCiuRec'] = 1
            gDatRec['dDesCiuRec'] = 'ASUNCION (DISTRITO)'

        if self.getdCelRec():
            gDatRec['dCelRec'] = self.getdCelRec()
        if self.getdEmailRec():
            gDatRec['dEmailRec'] = self.getdEmailRec()
        gDatRec['dCodCliente'] = self.getdCodCliente()

        return gDatRec

    def getgDtipDE(self):

        xml = {
            'gCamNRE': self.getgCamNRE(),
            'gCamItem': self.getgCamItem(),
            # E900
            'gTransp': self.getgTransp(),
        }
        return xml

    def getgTransp(self):
        # E900
        gTransp = {
            'iTipTrans': self.getiTipTrans(),
            'dDesTipTrans': self.getdDesTipTrans(),
            'iModTrans': self.getiModTrans(),
            'dDesModTrans': self.getdDesModTrans(),
            'iRespFlete': self.getiRespFlete(),
            # TODO: Se debe agregar opciones de importacion y los siguientes 3 campos
            # 'cCondNeg': self.getcCondNeg(),
            # 'dNuManif': self.getdNuManif(),
            # 'dNuDespImp': self.getdNuDespImp(),
            'dIniTras': self.getdIniTras(),
            'dFinTras': self.getdFinTras(),
            # TODO: Se debe agregar opcion de pais de destino
            # 'cPaisDest': self.getcPaisDest(),
            # 'dDesPaisDest': self.getdDesPaisDest(),
            # E920
            'gCamSal': self.getgCamSal(),

            # E940
            'gCamEnt': self.getgCamEnt(),
            # E960
            'gVehTras': self.getgVehTras(),
            #
            'gCamTrans': self.getgCamTrans()

        }

        return gTransp

    def getiTipTrans(self):
        if self.iTipTrans:
            return int(self.iTipTrans)
        return 1

    def getdDesTipTrans(self):
        if self.iTipTrans and self.iTipTrans == '1':
            return 'Propio'
        if self.iTipTrans and self.iTipTrans == '2':
            return 'Tercero'
        return 'Propio'

    def getiModTrans(self):
        if self.iModTrans:
            return int(self.iModTrans)
        return 1

    def getdDesModTrans(self):
        if self.iModTrans and self.iModTrans == '1':
            return 'Terrestre'
        if self.iModTrans and self.iModTrans == '2':
            return'Fluvial'
        if self.iModTrans and self.iModTrans == '3':
            return 'Aereo'
        if self.iModTrans and self.iModTrans == '4':
            return 'Multimodal'
        return 'Terrestre'

    def getiRespFlete(self):
        if self.iRespFlete:
            return int(self.iRespFlete)
        return 1

    def getdIniTras(self, kude=False):
        if self.fecha_inicio_traslado:
            fecha = self.fecha_inicio_traslado
        else:
            fecha =fields.Date.today()

        # Si se consulta desde el kude, retornamos en formato dd/mm/yyyy
        if kude:
            return fecha.strftime("%d/%m/%Y")
        else:
            return fecha.strftime("%Y-%m-%d")

    def getdFinTras(self, kude=False):
        if self.fecha_fin_traslado:
            fecha = self.fecha_fin_traslado
        else:
            fecha =fields.Date.today()

        # Si se consulta desde el kude, retornamos en formato dd/mm/yyyy
        if kude:
            return fecha.strftime("%d/%m/%Y")
        else:
            return fecha.strftime("%Y-%m-%d")

    def getgCamTrans(self):
        gCamTrans = {
            'iNatTrans': self.getiNatTrans(),
            'dNomTrans': self.getdNomTrans(),
            'dRucTrans': self.getdRucTrans(),
            'dDVTrans': self.getdDVTrans(),
            'iTipIDTrans': self.getiTipIDTrans(),
            'dDTipIDTrans': self.getdDTipIDTrans(),
            'dNumIDTrans': self.getdNumIDTrans(),
            #'cNacTrans': self.getcNacTrans(),
            #'dDesNacTrans': self.getdDesNacTrans(),
            'dNumIDChof': self.getdNumIDChof(),
            'dNomChof': self.getdNomChof(),
            'dDomFisc': self.getdDomFisc(),
            'dDirChof': self.getdDirChof(),
            #'dNombAg': self.getdNombAg(),
            #'dRucAg': self.getdRucAg(),
            #'dDVAg': self.getdDVAg(),
            #'dDirAge': self.getdDirAge()
        }
        if self.getiNatTrans() == 2:
            gCamTrans.pop('dRucTrans')
            gCamTrans.pop('dDVTrans')
        if self.getiNatTrans() == 1:
            gCamTrans.pop('iTipIDTrans')
            gCamTrans.pop('dDTipIDTrans')
            gCamTrans.pop('dNumIDTrans')

        return gCamTrans
    
    def getdDirChof(self):
        if self.chofer_id.street:
            return self.chofer_id.street
        return "Asuncion"

    def getdDomFisc(self):
        if self.transportista_id.street:
            return self.transportista_id.street
        return "Asuncion"
    def getdNumIDChof(self):
        return self.ruc_chofer or '111111'
    
    def getdNomChof(self):
        if self.chofer_id:
            return self.chofer_id.name
        else:
            return 'Generico'

    def getiNatTrans(self):
        if self.transportista_id.contribuyente:
            return 1
        return 2

    def getdNomTrans(self):
        return self.transportista_id.name

    def getdRucTrans(self):
        if self.getiNatTrans() == 1:
            return self.transportista_id.vat.split('-')[0]
        return False

    def getdDVTrans(self):
        if self.getdRucTrans():
            return int(self.env["fe.de"].get_digito_verificador(self.getdRucTrans()))
        return False

    def getiTipIDTrans(self):
        if self.getiNatTrans() == 2:
            tipo = int(self.transportista_id.tipo_documento)
            if tipo > 4:
                return 1
            else:
                return tipo
        return False

    def getdDTipIDTrans(self):
        tipo = self.getiTipIDTrans()
        if tipo == 1:
            return "Cédula paraguaya"
        if tipo == 2:
            return "Pasaporte"
        if tipo == 3:
            return "Cédula extranjera"
        if tipo == 4:
            return "Carnet de residencia"
        return False
    
    def getdNumIDTrans(self):
        return self.transportista_id.nro_documento or '111111'
    


    def getgVehTras(self):
        gVehTras = {
            'dTiVehTras': self.getdTiVehTras(),
            'dMarVeh': self.getdMarVeh(),
            'dTipIdenVeh': self.getdTipIdenVeh(),
            'dNroIDVeh': self.getdNroIDVeh(),
            # 'dAdicVeh': self.getdAdicVeh(),
            'dNroMatVeh': self.getdNroMatVeh(),
            'dNroVuelo': self.getdNroVuelo()
        }
        if not self.getdMarVeh():
            gVehTras.pop('dMarVeh')
        if not self.getdTipIdenVeh():
            gVehTras.pop('dTipIdenVeh')
            gVehTras.pop('dNroIDVeh')
            gVehTras.pop('dNroMatVeh')
        if self.getdTipIdenVeh() and self.getdTipIdenVeh()==1:
            gVehTras.pop('dNroMatVeh')
        else:
            gVehTras.pop('dNroIDVeh')
        if not self.getdNroVuelo():
            gVehTras.pop('dNroVuelo')
        return gVehTras

    def getdTiVehTras(self):
        return self.getdDesModTrans()

    def getdMarVeh(self):
        if self.marca_vehiculo:
            return self.marca_vehiculo[0:10]
        else:
            return "Generico"

    def getdTipIdenVeh(self):
        if self.dTipIdenVeh:
            return int(self.dTipIdenVeh)
        return False

    def getdNroIDVeh(self):
        if self.dNroIDVeh:
            return self.dNroIDVeh
        return False

    def getdNroMatVeh(self):
        if self.matricula:
            return self.matricula
        return False

    def getdNroVuelo(self):
        if self.dNroVuelo:
            return self.dNroVuelo
        return False

    def getgCamSal(self):
        gCamSal = {
            'dDirLocSal': self.getdDirLocSal(),
            'dNumCasSal': self.getdNumCasSal(),
            # 'dComp1Sal': self.getdComp1Sal(),
            # 'dComp2Sal': self.getdComp2Sal(),
            # TODO: Completar datos de los siguientes 7 campos
            'cDepSal': self.getcDepSal(),
            'dDesDepSal': self.getdDesDepSal(),
            # 'cDisSal': self.getcDisSal(),
            # 'dDesDisSal': self.getdDesDisSal(),
            'cCiuSal': self.getcCiuSal(),
            'dDesCiuSal': self.getdDesCiuSal(),
            # 'dTelSal': self.getdTelSal(),
        }
        return gCamSal
    # TODO: Mirar tabla de departamentos

    def getcDepSal(self):
        return 12

    def getdDesDepSal(self):
        return "CENTRAL"

    def getcCiuSal(self):
        return 6040

    def getdDesCiuSal(self):
        return "SAN LORENZO (MUNICIPIO)"

    def getdDirLocSal(self):
        if self.direccion_partida:
            return self.direccion_partida
        return self.env.company.street

    def getdNumCasSal(self):
        return 0

    def getgCamEnt(self):
        gCamEnt = {
            'dDirLocEnt': self.getdDirLocEnt(),
            'dNumCasEnt': self.getdNumCasEnt(),
            # TODO: completar los siguientes 9 campos
            # 'dComp1Ent': self.getdComp1Ent(),
            # 'dComp2Ent': self.getdComp2Ent(),
            'cDepEnt': self.getcDepEnt(),
            'dDesDepEnt': self.getdDesDepEnt(),
            # 'cDisEnt': self.getcDisEnt(),
            # 'dDesDisEnt': self.getdDesDisEnt(),
            'cCiuEnt': self.getcCiuEnt(),
            'dDesCiuEnt': self.getdDesCiuEnt(),
            # 'dTelEnt': self.getdTelEnt(),

        }
        return gCamEnt

    def getcCiuEnt(self):
        return 6040

    def getdDesCiuEnt(self):
        return "SAN LORENZO (MUNICIPIO)"

    def getcDepEnt(self):
        return 12

    def getdDesDepEnt(self):
        return "CENTRAL"

    def getdDirLocEnt(self):
        if self.direccion_entrega:
            return self.direccion_entrega
        return self.partner_id.street or 'Asuncion'

    def getdNumCasEnt(self):
        return 0

    def getgCamItem(self):
        gCamItem = []
        for line in self.line_ids:
            gCamItem.append(line.getgCamItem())
        return gCamItem

    def getgCamNRE(self):

        xml = {
            'iMotEmiNR': self.getiMotEmiNR(),
            'dDesMotEmiNR': self.getdDesMotEmiNR(),
            'iRespEmiNR': self.getiRespEmiNR(),
            'dDesRespEmiNR': self.getdDesRespEmiNR(),
            'dKmR': self.getdKmR(),
            'dFecEm': self.getdFecEm(),

        }
        if not self.getdFecEm():
            xml.pop('dFecEm')

        return xml

    def getiMotEmiNR(self):
        if self.iMotEmiNR:
            return int(self.iMotEmiNR)
        return 1

    def getdDesMotEmiNR(self):
        if self.iMotEmiNR and self.iMotEmiNR == '1':
            return 'Traslado por ventas'
        elif self.iMotEmiNR and self.iMotEmiNR == '2':
            return 'Traslado por consignación'
        elif self.iMotEmiNR and self.iMotEmiNR == '3':
            return 'Exportación'
        elif self.iMotEmiNR and self.iMotEmiNR == '4':
            return 'Traslado por compra'
        elif self.iMotEmiNR and self.iMotEmiNR == '5':
            return 'Importación'
        elif self.iMotEmiNR and self.iMotEmiNR == '6':
            return 'Traslado por devolución'
        elif self.iMotEmiNR and self.iMotEmiNR == '7':
            return 'Traslado entre locales de la empresa'
        elif self.iMotEmiNR and self.iMotEmiNR == '8':
            return 'Traslado de bienes por transformación'
        elif self.iMotEmiNR and self.iMotEmiNR == '9':
            return 'Traslado de bienes por reparación'
        elif self.iMotEmiNR and self.iMotEmiNR == '10':
            return 'Traslado por emisor móvil'
        elif self.iMotEmiNR and self.iMotEmiNR == '11':
            return 'Exhibición o demostración'
        elif self.iMotEmiNR and self.iMotEmiNR == '12':
            return 'Participación en ferias'
        elif self.iMotEmiNR and self.iMotEmiNR == '13':
            return 'Traslado de encomienda'
        elif self.iMotEmiNR and self.iMotEmiNR == '14':
            return 'Decomiso'
        elif self.iMotEmiNR and self.iMotEmiNR == '99':
            return 'Otro'
        return 'Traslado por venta'

    def getiRespEmiNR(self):
        if self.iRespEmiNR:
            return int(self.iRespEmiNR)
        return 1

    def getdDesRespEmiNR(self):

        if self.iRespEmiNR and self.iRespEmiNR == '1':
            return 'Emisor de la factura'
        if self.iRespEmiNR and self.iRespEmiNR == '2':
            return 'Poseedor de la factura y bienes'
        if self.iRespEmiNR and self.iRespEmiNR == '3':
            return 'Empresa transportista'
        if self.iRespEmiNR and self.iRespEmiNR == '4':
            return 'Despachante de Aduanas'
        if self.iRespEmiNR and self.iRespEmiNR == '5':
            return 'Agente de transporte o intermediario'
        return 'Emisor de la factura'

    def getdKmR(self):
        if self.kmr:
            return self.kmr
        return 1

    def getdFecEm(self):
        if self.invoice_datetime:
            return self.invoice_datetime.strftime("%Y-%m-%d")
        elif self.dFecEm:
            return self.dFecEm.strftime("%Y-%m-%d")
        return False

    def get_valor_seleccionado(self, campo_seleccion):
        selecciones = self.env['notas_remision_account.nota.remision'].fields_get(campo_seleccion)[campo_seleccion]['selection']
        valor_seleccionado = self[campo_seleccion]
        valor_asociado = dict(selecciones).get(valor_seleccionado)
        return valor_asociado


class NotasRemisionAccountLine(models.Model):
    _inherit = 'notas_remision_account.nota.remision.line'

    def getgCamItem(self):
        line = self
        gCamItem = {
            'dCodInt': line.getdCodInt(),
            # 'dParAranc': line.getdParAranc(),
            # 'dNCM': line.getdNCM(),
            # 'dGtin': line.getdGtin(),
            # 'dGtinPq': line.getdGtinPq(),
            'dDesProSer': line.getdDesProSer(),
            'cUniMed': line.getcUniMed(),
            'dDesUniMed': line.getdDesUniMed(),
            'dCantProSer': line.getdCantProSer(),
            'dInfItem': line.getdDesProSer(),

        }
        return gCamItem

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
            name = re.sub('\W+',' ', name)
        else:
            name = ""

        return name

    # TODO : Se debe relacionar con tabla proporcionada con la SET
    def getcUniMed(self):
        return self.uom_id.cod_set if self.uom_id.cod_set else 77

    def getdDesUniMed(self):
        return self.uom_id.des_set if self.uom_id.des_set else "UNI"

    def getdCantProSer(self):
        return round(self.qty, 4)