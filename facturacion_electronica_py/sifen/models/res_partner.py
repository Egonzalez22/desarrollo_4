import datetime
import logging

from odoo import _, exceptions, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fecha_verificacion_sifen = fields.Date(string="Fecha de verificación SIFEN")

    recibe_de = fields.Boolean(string="Recibe documento electronico", default=False, copy=False)

    def init(self):
        result = super().init()
        if not self.sudo().search([('recibe_de', '=', True)], limit=1):
            partners_a_actualizar = self.sudo().search([('parent_id', 'in', [False, None])])
            self.env.cr.execute('update res_partner set recibe_de=true where id in (%s)' % ','.join(str(x) for x in partners_a_actualizar.ids))
        return result

    def save(self):
        # Si se cambian los datos del contacto debe pasar por la validacion de SIFEN
        if self.is_contact:
            self.fecha_verificacion_sifen = None

        return super(ResPartner, self).save()

    def action_validar_ruc_sifen(self):
        for rec in self:
            rec.validar_ruc_sifen(True)

        return True

    def validar_ruc_sifen(self, force=False):
        """
        Se valida el nro de documento del contacto contra SIFEN.
        Hasta la fecha 10/10/2024, solo se valida si el contacto es un contribuyente o no segun SIFEN. 
        No se valida el estado del RUC (Cancelado, Activo, etc).
        """

        # Si esta obviada la validacion, retornamos porque al tener macado como obviar es porque no es un RUC
        if self.obviar_validacion:
            return

        # Si no se fuerza la validación, se continua normalmente el flujo inicial
        if not force:
            # Si existe el parametro, no se valida
            if self.env['ir.config_parameter'].sudo().get_param('fe_de.obviar_validar_ruc_sifen'):
                return

            # Si ya se verifico hace menos de 2 semanas, no se vuelve a verificar
            two_weeks_ago = datetime.date.today() - datetime.timedelta(days=14)
            if self.fecha_verificacion_sifen and self.fecha_verificacion_sifen > two_weeks_ago:
                return

        # Verificamos si esta cargado como contribuyente o no en contacto
        nro_documento = None
        if self.vat:
            nro_documento = self.vat
            if nro_documento and "-" in nro_documento:
                nro_documento = nro_documento.split('-')[0]
        elif self.nro_documento:
            nro_documento = self.nro_documento

        # Si no existe nro de documento o ruc, no se puede generar una factura
        if not nro_documento:
            raise exceptions.ValidationError(_('Debe completar el RUC o Nro de Documento del cliente'))

        nro_documento = nro_documento.replace(".", "").replace(" ", "")
        res_ruc = self.env['fe.de'].consultar_ruc(nro_documento)

        # Si no se pudo consultar al servicio de SIFEN, se retorna
        if not res_ruc:
            _logger.error('No se pudo consultar al servicio de consultar RUC de SIFEN')
            return

        vat = f'{nro_documento}-{self.env["fe.de"].get_digito_verificador(nro_documento)}'
        if res_ruc:
            rResEnviConsRUC = res_ruc['env:Envelope']['env:Body']['ns2:rResEnviConsRUC']
            es_contribuyente = rResEnviConsRUC['ns2:dCodRes'] in ['0502']
            if es_contribuyente:
                ruc = rResEnviConsRUC['ns2:xContRUC']['ns2:dRUCCons']

                # Si es contribuyente segun SIFEN, y no tiene cargado vat se genera el digito verificador
                # vat = self.vat
                self.write(
                    {
                        'contribuyente': True,
                        'vat': vat,
                        'fecha_verificacion_sifen': datetime.date.today(),
                    }
                )
            else:
                self.obviar_validacion = True
                self.contribuyente = False
                self.vat = False
                self.tipo_documento = '1'
                self.nro_documento = nro_documento
                self.fecha_verificacion_sifen = datetime.date.today()
