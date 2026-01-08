from odoo import _, api, fields, models, exceptions


class AccountMove(models.Model):
    _inherit = 'account.move'

    condicion_credito = fields.Selection(
        string="Condición de Crédito",
        selection=[('1', 'Plazo'), ('2', 'Cuota')],
        default='1',
        copy=False,
    )

    # TODO: funcion para poner plazo o cuota
    # len(self.line_ids.filtered(lambda line: line.account_id.account_type in ('asset_receivable')))
    # Si hay mas de una linea es en cuotas, ordenar por fecha de vencimieto para obtener la primera cuota (date_maturity)

    cantidad_cuotas = fields.Integer(string='Cantidad de Cuotas')
    es_fact_credito = fields.Boolean(string='Es Factura a Crédito', default=False, compute='_compute_es_fact_credito')

    ### GRUPO QUE DEFINE LA CONDICIÓN DE PAGO CRÉDITO ###

    @api.depends('invoice_date', 'invoice_date_due', 'invoice_payment_term_id')
    @api.onchange('invoice_date', 'invoice_date_due', 'invoice_payment_term_id')
    def _compute_es_fact_credito(self):
        if self.move_type in ['out_invoice', 'out_refund']:
            if self.invoice_date == self.invoice_date_due:
                self.es_fact_credito = False
            else:
                self.es_fact_credito = True
        else:
            self.es_fact_credito = False

    def getiCondCred(self):
        """
        E641:
        Condición de la operación a crédito
        1= Plazo 2= Cuota
        """
        if self.condicion_credito:
            return int(self.condicion_credito)
        else:
            return

    def getdDCondCred(self):
        """
        E642:
        Descripción de la condición de la operación a crédito
        1= “Plazo”
        2= “Cuota”
        """
        if self.condicion_credito:
            if self.condicion_credito == '1':
                return 'Plazo'
            elif self.condicion_credito == '2':
                return 'Cuota'
        else:
            return

    def getdPlazoCre(self):
        """
        E643:
        Plazo del crédito
        Obligatorio si E641 = 1
        Ejemplo: 30 días, 12 meses
        """
        
        # Obtenemos la diferencia en dias
        if self.invoice_date and self.invoice_date_due:
            date1 = fields.Datetime.from_string(self.invoice_date)
            date2 = fields.Datetime.from_string(self.invoice_date_due)
            delta = date2 - date1
            return str(delta.days) + ' días'

        else:
            msg = 'No se puede obtener el plazo de crédito, verifique que la fecha de factura y la fecha de vencimiento estén completas.'
            raise exceptions.ValidationError(_(msg))

    def getdCuotas(self):
        """
        E644:
        Cantidad de cuotas
        Obligatorio si E641 = 2
        Ejemplo: 12, 24, 36
        """
        if self.cantidad_cuotas:
            return self.cantidad_cuotas
        else:
            return

    def getdMonEnt(self):
        return

    def getgCuotas(self):
        gCuotas = {  # OBLIGATORIO SI LA CONDICION DE CREDITO ES CUOTAS (iCondCred = 2)
            'cMoneCuo': self.getcMoneCuo(),
            'dDMoneCuo': self.getdDMoneCuo(),
            #'dMonCuota': self.getdMonCuota(), #Monto de cada cuota
            #'dVencCuo': self.getdVencCuo() #Fecha de Vencimiento de cada cuota
        }
        return gCuotas

    def getcMoneCuo(self):
        return self.currency_id.name

    def getdDMoneCuo(self):
        return self.currency_id.currency_unit_label

    def getdMonCuota(self):
        return

    def getdVencCuo(self):
        return

    def getgPagCred(self):
        """
        E7.2. Campos que describen la operación a crédito (E640-E649)
        """

        gPagCred = {  # PAGO A CRÉDITO
            'iCondCred': self.getiCondCred(),
            'dDCondCred': self.getdDCondCred(),
            #'dMonEnt': self.getdMonEnt(), #Monto entrega Inicial
        }

        if self.getiCondCred() == 1:
            gPagCred['dPlazoCre'] = self.getdPlazoCre()
        elif self.getiCondCred() == 2:
            gPagCred['dCuotas'] = self.getdCuotas()
            gPagCred['gCuotas'] = self.getgCuotas()

        return gPagCred

    ### FIN DE GRUPO QUE DEFINE LA CONDICIÓN DE PAGO CRÉDITO ###
