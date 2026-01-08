from odoo import _, api, fields, models, exceptions


class NotasRemision(models.Model):
    _inherit = 'notas_remision_account.nota.remision'

    @api.onchange('chofer_id')
    def onchange_chofer(self):
        self.iTipTrans = self.chofer_id.tipo_transporte
        self.iRespFlete = self.chofer_id.responsable_flete
        self.marca_vehiculo = self.chofer_id.marca_vehiculo
        self.dTipIdenVeh = self.chofer_id.identidad_vehiculo
        self.matricula = self.chofer_id.matricula