from odoo import models, fields, api, exceptions
import re


class AccountMove(models.Model):
    _inherit = 'account.move'


    def action_post(self):
        res = super(AccountMove, self).action_post()
        for record in self:
            record.validar_timbrado_autofactura()
        return res

    def validar_timbrado_autofactura(self):
        if self.move_type in ['in_invoice', 'in_refund'] and self.name and self.name != '/':
            if self.journal_id.timbrado_autofactura and self.res90_tipo_comprobante == '101':
                timbrado = self.journal_id.timbrados_ids.filtered(
                    lambda x: x.active and x.tipo_documento == 'autofactura')
                if len(timbrado) > 1:
                    raise exceptions.ValidationError(
                        'Tiene más de 1 timbrado activo para éste Diario. Favor verificar')
                if timbrado:
                    self.validarnrofactura(self.name)
                    numero = int(self.name.split('-')[-1])
                    nro_establecimiento = self.name.split('-')[0]
                    nro_pto_expedicion = self.name.split('-')[1]
                    if nro_pto_expedicion != timbrado.nro_punto_expedicion:
                        raise exceptions.ValidationError(
                            'El numero de punto de expedicion no coincide con el del timbrado activo')
                    if nro_establecimiento != timbrado.nro_establecimiento:
                        raise exceptions.ValidationError(
                            'El numero de establecimiento no coincide con el del timbrado activo')
                    if numero > timbrado.rango_final:
                        raise exceptions.ValidationError(
                            'El timbrado activo ha llegado a su número final')
                    fecha = self.invoice_date or fields.Date.today()
                    if fecha > timbrado.fin_vigencia:
                        raise exceptions.ValidationError(
                            'La fecha de la factura no puede ser mayor a la fecha de fin de vigencia del timbrado')
                    if fecha < timbrado.inicio_vigencia:
                        raise exceptions.ValidationError(
                            'La fecha de la factura no puede ser menor a la fecha de fin de vigencia del timbrado')
                    self.res90_nro_timbrado = timbrado.name
                    self.timbrado_proveedor = timbrado.name
                    self.ref = self.name
                    # self.write({
                    #     'res90_nro_timbrado': timbrado.name,
                    #     'timbrado_proveedor': timbrado.name,
                    #     'ref': self.name
                    # })
                else:
                    raise exceptions.ValidationError(
                        'No existe un timbrado activo')
        else:
            return