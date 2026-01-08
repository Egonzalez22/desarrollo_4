import json
import logging
import datetime

from odoo import models, fields

_logger = logging.getLogger(__name__)


class Cron(models.AbstractModel):
    _inherit = 'fe.de'

    def get_companies(self):
        """
        Se obtienen todas las compañias que tienen habilitado el FE
        """
        domain = [('facturador_electronico', '=', True)]
        companies = self.env['res.company'].search(domain)
        return companies

    def preparar_lote(self):
        """
        Se obtienen todos los documentos en estado pendientes y se agrupan en lotes de 50
        """

        # Cuando se ejecuta el cron se obtienen todas las compañias que tienen habilitado el FE
        companies = self.get_companies()
        for company in companies:
            self = self.with_company(company.id)

            # Por cada tipo de documento disponible, iteramos y preparamos un lote hasta 50 documentos
            tipos_documentos = ['out_invoice', 'out_refund', 'autofactura', 'nota_debito', 'nota_remision']
            for tipo_documento in tipos_documentos:
                is_remision = tipo_documento == "nota_remision"

                # 1 - Obtenemos todos los documentos validos, en estado posted y con estado set pendiente
                domain = [
                    ('company_id', '=', company.id),
                    ('state', '=', 'posted'),
                    ('estado_set', '=', 'pendiente'),
                    ('fe_valida', '=', True),
                    ('xml_file', '!=', False),
                    ('tipo_documento', '=', tipo_documento),  # Extiende de de.py
                ]

                # Obtenemos los documentos dependiendo del tipo de documento
                if is_remision:
                    documentos = self.env['notas_remision_account.nota.remision'].search(domain)
                else:
                    documentos = self.env['account.move'].search(domain)

                if documentos:
                    # Iteramos en grupos de 50 facturas
                    for i in range(0, len(documentos), 50):
                        invoices_group = documentos[i: i + 50]

                        # 2 - Creamos un lote
                        lote = self.env['fe.lote'].sudo().create({'tipo_documento_electronico': tipo_documento, 'company_id': company.id})

                        # 3 - Cambiamos el estado del documento para saber que el documento puede ser enviado y asociamos el lote
                        for invoice in invoices_group:
                            invoice.write(
                                {
                                    'estado_set': 'preparado',
                                    'lote_id': lote.id if not is_remision else False,
                                    'lote_nr_id': lote.id if is_remision else False,
                                }
                            )

            self.controlar_lotes_vacios()

    def controlar_lotes_vacios(self):
        """
        Cuando un lote se queda sin documentos, se debe pasar al estado finalizado
        """

        # TODO: Queda comentada esta porcion temporalmente hasta validar el nuevo código: 06-07-24
        # Obtenemos todos los lotes que no tengan documentos y esten en estado creado o en_proceso
        # domain = [
        #     ('estado_lote', 'in', ['creado', 'en_proceso']),
        #     '&',
        #     ('invoice_ids', '=', False),
        #     ('remision_ids', '=', False),
        # ]
        # lotes = self.env['fe.lote'].search(domain)
        # for lote in lotes:
        #     lote.sudo().write({'estado_lote': 'finalizado'})

        # Obtenemos todos los lotes en estado creado y en proceso
        domain = [('estado_lote', 'in', ['creado', 'en_proceso'])]
        lotes = self.env['fe.lote'].search(domain)
        for lote in lotes:
            # Verificamos si el lote es del tipo invoice y no tiene documentos asociados
            if lote.tipo_documento_electronico != 'nota_remision' and not lote.invoice_ids:
                lote.sudo().write({'estado_lote': 'finalizado'})

            # Verificamos si el lote es del tipo nota_remision y no tiene documentos asociados
            if lote.tipo_documento_electronico == 'nota_remision' and not lote.remision_ids:
                lote.sudo().write({'estado_lote': 'finalizado'})

            # Verificamos si todos los invoices_ids estan en estado aprobado
            if lote.invoice_ids:
                if lote.tipo_documento_electronico != 'nota_remision' and all([invoice.estado_set == 'aprobado' for invoice in lote.invoice_ids]):
                    lote.sudo().write({'estado_lote': 'finalizado'})

            # Verificamos si todos los remision_ids estan en estado aprobado
            if lote.remision_ids:
                if lote.tipo_documento_electronico == 'nota_remision' and all([remision.estado_set == 'aprobado' for remision in lote.remision_ids]):
                    lote.sudo().write({'estado_lote': 'finalizado'})

    def enviar_lote(self):
        """
        Enviamos los lotes pendientes
        """
        companies = self.get_companies()
        for company in companies:
            self = self.with_company(company.id)
            INTENTO_REENVIO = self.env.company.fe_intento_reenvio or 3

            # 1 - Obtenemos los lotes pendientes y rechazados con un intento de reenvio maximo de 3 veces
            domain = [
                '|',
                '&',
                ('estado_set', 'in', ['pendiente', 'error']),
                ('estado_lote', '=', 'creado'),
                '&',
                ('estado_set', '=', 'reenviar'),
                ('intento_envio', '<=', INTENTO_REENVIO),
            ]
            lotes = self.env['fe.lote'].search(domain)

            for lote in lotes:
                # 2 - Enviamos el lote
                response = self.env['fe.de'].enviar_lote_individual(lote)

                # 3 - Procesamos la respuesta del lote
                self.env['fe.de'].procesar_enviar_lote(lote, response)

    def consultar_lote(self):
        """
        Se consulta el estado del lote de facturas
        """

        companies = self.get_companies()
        for company in companies:
            self = self.with_company(company.id)
            # 1 - Obtenemos los lotes pendientes y con error, que esten en proceso de analisis
            domain = [
                '&',
                ('estado_set', 'in', ['en_proceso', 'error']),
                ('estado_lote', '=', 'en_proceso'),
                ('numero_lote', '!=', False),
            ]
            lotes = self.env['fe.lote'].search(domain)

            for lote in lotes:
                # 2 - Consultamos el estado del lote
                response = self.env['fe.de'].consultar_lote_individual(lote)

                # 3 - Procesamos la respuesta de la consulta del lote
                self.env['fe.de'].procesar_consultar_lote(lote, response)

    def consultar_cdc(self):
        """
        Se consulta el estado de cada factura pendiente de procesamiento.
        Los lotes solo se pueden consultar hasta 48 horas y puede tener problemas en algun momento
        """

        companies = self.get_companies()
        for company in companies:
            self = self.with_company(company.id)
            domain = [('estado_set', '=', 'ingresado')]

            # 1 - Obtenemos todos los documentos del tipo account.move con estado set ingresado
            invoices = self.env['account.move'].search(domain)
            for invoice in invoices:
                # Creamos un logger del invoice
                de_logger = self.env['fe.de_loggers'].sudo().create({"invoice": invoice.id, "accion": "consultar CDC"})

                response = invoice.consultar_cdc_individual(de_logger, invoice.cdc)
                invoice.procesar_consultar_cdc(response)

            # 2 - Obtenemos todos los documentos del tipo account.move con estado set ingresado
            notas_remision = self.env['notas_remision_account.nota.remision'].search(domain)
            for nr in notas_remision:
                # Creamos un logger del nr
                de_logger = self.env['fe.de_loggers'].sudo().create({"remision_id": nr.id, "accion": "consultar CDC"})

                response = nr.consultar_cdc_individual(de_logger, nr.cdc)
                nr.procesar_consultar_cdc(response)

    def enviar_mails(self):
        """
        Se envian los documentos electronicos por mail de los aprobados
        """
        companies = self.get_companies()
        domain = [('documento_enviado_mail', '=', False), ('estado_set', '=', 'aprobado')]

        limit = self.env['ir.config_parameter'].sudo().get_param('cron_enviar_mail_limite_registros')
        if not limit: return
        limit = int(limit)

        domain_desactivar_envio = domain + [('invoice_date', '<', str(fields.Date.today() - datetime.timedelta(days=7)))]
        self.env['account.move'].search(domain_desactivar_envio).write({'documento_enviado_mail': True})
        for company in companies:
            self = self.with_company(company.id)
            domain_company = domain + [('company_id', '=', company.id)]

            # 1 - Obtenemos todos los documentos del tipo account.move
            domain_invoices = domain_company + [('documento_procesado_mail', '=', False)]
            invoices = self.env['account.move'].search(domain_invoices, limit=limit)
            if not invoices:
                domain_invoices = domain_company + [('documento_procesado_mail', '=', True)]
                invoices = invoices.search(domain_invoices, limit=limit)
            for invoice in invoices:
                # Enviamos el mail
                invoice.send_email_de()
                invoice.write({'documento_procesado_mail': True})

            # 2 - Obtenemos todos los documentos del notas_remision_account
            domain_nr = domain_company + [('documento_procesado_mail', '=', False)]
            notas_remision = self.env['notas_remision_account.nota.remision'].search(domain_nr, limit=limit)
            if not notas_remision:
                domain_nr = domain_company + [('documento_procesado_mail', '=', True)]
                notas_remision = notas_remision.search(domain_nr, limit=limit)
            for nr in notas_remision:
                # Enviamos el mail
                nr.send_email_de()
                nr.write({'documento_procesado_mail': True})
