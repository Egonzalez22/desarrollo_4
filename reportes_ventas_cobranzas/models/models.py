# -*- coding: utf-8 -*-
from odoo import api, fields, models, exceptions
from datetime import datetime
import json
from odoo.tools import float_round


class AccountMove(models.Model):
    _inherit = 'account.move'

    cotizacion_ventas_cobranzas = fields.Float(string='Cotizacion', compute="compute_cotizacion_monedas_ventas_cobranzas")

    @api.onchange('currency_id', 'invoice_date')
    @api.depends('currency_id', 'invoice_date')
    def compute_cotizacion_monedas_ventas_cobranzas(self):
        for r in self:
            present = fields.Date.today()
            # currency_rate = self.env['res.currency.rate'].search([ ('currency_id','=',r.currency_id.id),('name','=',r.invoice_date or present) ])
            currency_rate = r.currency_id._get_rates(r.company_id, r.invoice_date or present)

            if r.currency_id.name != 'PYG' and currency_rate:
                # coti_compra = currency_rate.cotizacion
                coti_compra = 1 / currency_rate.get(r.currency_id.id)
                if r.move_type in ['out_invoice', 'out_refund']:
                    r.cotizacion_ventas_cobranzas = coti_compra
                elif r.move_type == 'entry' and not r.payment_id:
                    r.cotizacion_ventas_cobranzas = coti_compra

            if r.currency_id.name != 'PYG' and currency_rate:
                coti_venta = 1 / currency_rate.get(r.currency_id.id)
                if r.move_type in ['in_invoice', 'in_refund']:
                    r.cotizacion_ventas_cobranzas = coti_venta
            else:
                coti_compra = 1
                coti_venta = 1

            # if r.currency_id.name == "PYG":
            #     r.currency_default = True
            # else:
            #     r.currency_default = False
            if not r.cotizacion_ventas_cobranzas:
                r.cotizacion_ventas_cobranzas = 0.0


class ReportesVentasCobranzas(models.TransientModel):
    _name = 'reportes_ventas_cobranzas.reporte'

    fecha = fields.Date(string="Fecha de inicio", required=True)
    fecha_fin = fields.Date(string="Fecha de fin", required=True)
    tipo_reporte = fields.Selection(
        [
            ('ventas_contado', 'Ventas al Contado'),
            # ('ventas_acumuladas', 'Ventas Acumuladas'),
            ('ventas_credito', 'Ventas a Crédito'),
            ('reporte_cobranzas', 'Reporte de Cobranzas'),
        ],
        string="Reporte", required=True)

    def button_generar(self):

        data = {
            'fecha': self.fecha,
            'fecha_fin': self.fecha_fin,
            'tipo_reporte': self.tipo_reporte,
        }
        if self.tipo_reporte == 'ventas_contado':
            return self.env.ref('reportes_ventas_cobranzas.ventas_contado_action').report_action(self, data=data)

        if self.tipo_reporte == 'ventas_credito':
            return self.env.ref('reportes_ventas_cobranzas.ventas_credito_action').report_action(self, data=data)

        # if self.tipo_reporte == 'ventas_acumuladas':
        #     return self.env.ref('reportes_ventas_cobranzas.ventas_acumuladas_action').report_action(self, data=data)

        if self.tipo_reporte == 'reporte_cobranzas':
            return self.env.ref('reportes_ventas_cobranzas.reporte_cobranzas_action').report_action(self, data=data)

    def button_generar_xlsx(self):
        return self.env.ref('reportes_ventas_cobranzas.reporte_cobranzas_xlsx_action').report_action(self)


class ReportCobranzas(models.AbstractModel):
    _name = 'report.reportes_ventas_cobranzas.reporte_cobranzas'

    def _get_report_values(self, docids, data=None):
        # print(f"EMPIEZA**********************")
        pagos_gs = self.env['account.payment'].search([
            ('payment_type', '=', 'inbound'),
            ('date', '>=', data.get('fecha')),
            ('date', '<=', data.get('fecha_fin')),
            ('currency_id', '=', 'PYG'),
            ('state', '=', 'posted')
        ])

        pagos_us = self.env['account.payment'].search([
            ('payment_type', '=', 'inbound'),
            ('date', '>=', data.get('fecha')),
            ('date', '<=', data.get('fecha_fin')),
            ('currency_id', '=', 'USD'),
            ('state', '=', 'posted')
        ])
       

        pagos = self.env['account.payment'].search([
            ('payment_type', '=', 'inbound'),
            ('date', '>=', data.get('fecha')),
            ('date', '<=', data.get('fecha_fin')),
            ('state', '=', 'posted')
        ])

        

        return {
            'fecha': data.get('fecha'),
            'fecha_fin': data.get('fecha_fin'),
            'pagos_gs': pagos_gs,
            'pagos_us': pagos_us,
            'pagos': pagos,
            'company': self.env.user.company_id
        }


class ReportVentasContado(models.AbstractModel):
    _name = 'report.reportes_ventas_cobranzas.ventas_contado'

    def _get_report_values(self, docids, data=None):
        list_facts_contado = []  # listado de facturas de ventas al contado

        # se buscan todas las facturas al contado
        facturas = self.env['account.move'].search(
            [('company_id', '=', self.env.user.company_id.id),
             ('invoice_date_due', '=', data.get('fecha')),
             ('move_type', '=', 'out_invoice'),
             ('state', 'in', ['posted']),
             ('invoice_date', '>=', data.get('fecha')),
             ('invoice_date', '<=', data.get('fecha_fin'))])

        for f in facturas:
            invoice_payment = json.loads(f.invoice_payments_widget)  # lista de pagos conciliados a la factura
            if invoice_payment:
                detalle = invoice_payment['content']  # en content se encuentran los detalles del pago 
                for dt in detalle:
                    # buscamos en account.payment el pago relacionado a la factura
                    payment = self.env['account.payment'].search([('id', '=', dt['account_payment_id'])])
                    if payment:
                        list_facts_contado.append([f, payment])  # se agrega la instancia de factura y pago
                    else:
                        list_facts_contado.append([f, 'x'])  # se agrega una bandera x para denotar que no hay pago
            else:
                list_facts_contado.append([f, 'x'])  # se agrega una bandera x para denotar que no hay pago

        return {
            'fecha': data.get('fecha'),
            'facturas': list_facts_contado,
            'company': self.env.user.company_id
        }


class ReportVentasCredito(models.AbstractModel):
    _name = 'report.reportes_ventas_cobranzas.ventas_credito'

    def _get_report_values(self, docids, data=None):
        facturas = self.env['account.move'].search(
            [('company_id', '=', self.env.user.company_id.id),
             ('invoice_date_due', '!=', data.get('fecha')),
             ('move_type', '=', 'out_invoice'),
             ('state', 'in', ['posted']),
             ('invoice_date', '>=', data.get('fecha')),
             ('invoice_date', '<=', data.get('fecha_fin'))])

        rate = 0
        for factura in facturas:
            if factura.currency_id.name == 'USD':
                rate = factura.currency_id._get_conversion_rate(factura.currency_id, self.env.user.company_id.currency_id, self.env.user.company_id,
                                                                factura.invoice_date)

        return {
            'fecha': data.get('fecha'),
            'facturas': facturas,
            'company': self.env.user.company_id,
            'rate_usd': round(rate, 0)
        }


class ReportVentasAcumuladas(models.AbstractModel):
    _name = 'report.reportes_ventas_cobranzas.ventas_acumuladas'

    def _get_report_values(self, docids, data=None):
        inicio_mes = data.get('fecha')[:-2] + str('01')
        data_facturas = []
        facturas = self.env['account.move'].search(
            [('company_id', '=', self.env.user.company_id.id),
             ('move_type', '=', 'out_invoice'),
             ('state', 'in', ['posted']),
             ('invoice_date', '>=', data.get('fecha')),
             ('invoice_date', '<=', data.get('fecha_fin'))
             ])

        acumuladas = self.env['account.move'].search(
            [('company_id', '=', self.env.user.company_id.id),
             ('move_type', '=', 'out_invoice'),
             ('state', 'in', ['posted']),
             ('invoice_date', '>=', inicio_mes),
             ('invoice_date', '<=', data.get('fecha_fin'))
             ])

        total_base10 = 0
        total_iva10 = 0
        total_base5 = 0
        total_iva5 = 0
        total_exentas = 0
        total_facturas = 0

        acumulado_total = 0
        acumulado_base10 = 0
        acumulado_iva10 = 0
        acumulado_base5 = 0
        acumulado_iva5 = 0
        acumulado_exentas = 0

        for a in acumuladas.sorted(key=lambda x: x.name):
            base10 = 0
            base5 = 0
            exentas = 0
            iva10 = 0
            iva5 = 0

            if a.state != 'cancel':
                acumulado_total += abs(a.amount_total_signed)

            for t in a.filtered(lambda x: x.state != 'cancel').invoice_line_ids:
                if t.tax_ids and t.tax_ids[0].amount == 10:
                    base10 += t.price_total / 1.1
                    iva10 += t.price_total / 11
                if t.tax_ids and t.tax_ids[0].amount == 5:
                    base5 += t.price_total / 1.05
                    iva5 += t.price_total / 21
                if (t.tax_ids and t.tax_ids[0].amount == 0) or not t.tax_ids:
                    exentas += t.price_total

            # obtener valor de cotizacion
            coti = a.line_ids[0].credit / abs(a.line_ids[0].amount_currency)
            coti = float_round(coti, precision_digits=2, rounding_method='HALF-UP')
            print(coti)

            # CONVERTIR TODO A GS
            if a.currency_id != self.env.company.currency_id:
                base10 = a.currency_id._convert(
                    round(base10, 2), self.env.company.currency_id, self.env.company, a.invoice_date, cotizacion=coti)
                iva10 = a.currency_id._convert(
                    round(iva10, 2), self.env.company.currency_id, self.env.company, a.invoice_date, cotizacion=coti)
                base5 = a.currency_id._convert(
                    round(base5, 2), self.env.company.currency_id, self.env.company, a.invoice_date, cotizacion=coti)
                iva5 = a.currency_id._convert(
                    round(iva5, 2), self.env.company.currency_id, self.env.company, a.invoice_date, cotizacion=coti)
                exentas = a.currency_id._convert(
                    round(exentas, 2), self.env.company.currency_id, self.env.company, a.invoice_date, cotizacion=coti)

            # if a.currency_id.name == "USD":
            #     base10 = base10*a.cotizacion
            #     iva10 = iva10*a.cotizacion
            #     base5 = base5*a.cotizacion
            #     iva5 = iva5*a.cotizacion
            #     exentas = exentas*a.cotizacion

            base10 = int(round(base10, 0))
            iva10 = int(round(iva10, 0))
            base5 = int(round(base5, 0))
            iva5 = int(round(iva5, 0))
            exentas = int(round(exentas, 0))

            acumulado_base10 += base10
            acumulado_iva10 += iva10
            acumulado_base5 += base5
            acumulado_iva5 += iva5
            acumulado_exentas += exentas

        for i in facturas.sorted(key=lambda x: x.name):
            base10 = 0
            base5 = 0
            exentas = 0
            iva10 = 0
            iva5 = 0
            # i.amount_untaxed_signed
            # i.amount_tax_signed
            # i.amount_total_signed

            if i.state != 'cancel':
                total_facturas += abs(i.amount_total_signed)

            for t in i.filtered(lambda x: x.state != 'cancel').invoice_line_ids:
                if t.tax_ids and t.tax_ids[0].amount == 10:
                    base10 += t.price_total / 1.1
                    iva10 += t.price_total / 11
                if t.tax_ids and t.tax_ids[0].amount == 5:
                    base5 += t.price_total / 1.05
                    iva5 += t.price_total / 21
                if (t.tax_ids and t.tax_ids[0].amount == 0) or not t.tax_ids:
                    exentas += t.price_total

            # obtener valor de cotizacion
            coti = i.line_ids[0].credit / abs(i.line_ids[0].amount_currency)
            coti = float_round(coti, precision_digits=2, rounding_method='HALF-UP')
            print(coti)

            # CONVERTIR TODO A GS
            if i.currency_id != self.env.company.currency_id:
                base10 = i.currency_id._convert(
                    round(base10, 2), self.env.company.currency_id, self.env.company, i.invoice_date, cotizacion=coti)
                iva10 = i.currency_id._convert(
                    round(iva10, 2), self.env.company.currency_id, self.env.company, i.invoice_date, cotizacion=coti)
                base5 = i.currency_id._convert(
                    round(base5, 2), self.env.company.currency_id, self.env.company, i.invoice_date, cotizacion=coti)
                iva5 = i.currency_id._convert(
                    round(iva5, 2), self.env.company.currency_id, self.env.company, i.invoice_date, cotizacion=coti)
                exentas = i.currency_id._convert(
                    round(exentas, 2), self.env.company.currency_id, self.env.company, i.invoice_date, cotizacion=coti)

            # if i.currency_id.name == "USD":
            #     base10 = base10*i.cotizacion
            #     iva10 = iva10*i.cotizacion
            #     base5 = base5*i.cotizacion
            #     iva5 = iva5*i.cotizacion
            #     exentas = exentas*i.cotizacion

            base10 = int(round(base10, 0))
            iva10 = int(round(iva10, 0))
            base5 = int(round(base5, 0))
            iva5 = int(round(iva5, 0))
            exentas = int(round(exentas, 0))

            total_base10 += base10
            total_iva10 += iva10
            total_base5 += base5
            total_iva5 += iva5
            total_exentas += exentas

            data_facturas.append({
                'numero': i.name,
                'fecha': i.invoice_date,
                'razon_social': i.partner_id.name,
                'ruc': i.partner_id.vat,
                'base10': base10,
                'iva10': iva10,
                'base5': base5,
                'iva5': iva5,
                'exentas': exentas
            })

        return {
            'fecha': data.get('fecha'),
            'facturas': data_facturas,
            'total_base10': total_base10,
            'total_iva10': total_iva10,
            'total_base5': total_base5,
            'total_iva5': total_iva5,
            'total_exentas': total_exentas,
            'total_facturas': int(round(total_facturas, 0)),
            'acumulado_total': int(round(acumulado_total, 0)),
            'acumulado_base10': acumulado_base10,
            'acumulado_iva10': acumulado_iva10,
            'acumulado_base5': acumulado_base5,
            'acumulado_iva5': acumulado_iva5,
            'acumulado_exentas': acumulado_exentas,
            'company': self.env.user.company_id,
        }


class ReportVentasCobranzasXLSX(models.AbstractModel):
    _name = 'report.reportes_v_c.reporte_c_xlsx_action_t'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        global sheet
        global bold
        global num_format
        global position_x
        global position_y
        text_right = workbook.add_format({'align': 'right'})
        bold = workbook.add_format({'bold': True})
        numerico = workbook.add_format({'num_format': True, 'align': 'right'})
        numerico.set_num_format('#,##0')
        numerico_total = workbook.add_format({'num_format': True, 'align': 'right', 'bold': True})
        numerico_total.set_num_format('#,##0')
        date_only = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        wrapped_text = workbook.add_format()
        wrapped_text.set_text_wrap()
        wrapped_text_bold = workbook.add_format({'bold': True})
        wrapped_text_bold.set_text_wrap()

        position_x = 0
        position_y = 0

        def addSalto():
            global position_x
            global position_y
            position_x = 0
            position_y += 1

        def addRight():
            global position_x
            position_x += 1

        def simpleWrite(to_write, format=None):
            global sheet
            if isinstance(to_write, int) or isinstance(to_write, float):
                to_write = int(to_write)
            sheet.write(position_y, position_x, to_write or ('' if type(to_write) != int else 0), format)

        def breakAndWrite(to_write, format=None):
            global sheet
            addSalto()
            simpleWrite(to_write, format)

        def rightAndWrite(to_write, format=None):
            global sheet
            addRight()
            simpleWrite(to_write, format)

        if wizard.tipo_reporte == 'ventas_contado':
            sheet = workbook.add_worksheet('LISTADO DE VENTAS AL CONTADO')
            list_facts_contado = []  # listado de facturas de ventas al contado

            # se buscan todas las facturas al contado
            facturas = self.env['account.move'].search([
                ('company_id', '=', self.env.user.company_id.id),
                ('invoice_date_due', '=', wizard.fecha),
                ('move_type', '=', 'out_invoice'),
                ('state', 'in', ['posted']),
                ('invoice_date', '>=', wizard.fecha),
                ('invoice_date', '<=', wizard.fecha_fin)]
            )

            for f in facturas:
                invoice_payment = json.loads(f.invoice_payments_widget)  # lista de pagos conciliados a la factura
                if invoice_payment:
                    detalle = invoice_payment['content']  # en content se encuentran los detalles del pago
                    for dt in detalle:
                        # buscamos en account.payment el pago relacionado a la factura
                        payment = self.env['account.payment'].search([('id', '=', dt['account_payment_id'])])
                        if payment:
                            list_facts_contado.append([f, payment])  # se agrega la instancia de factura y pago
                        else:
                            list_facts_contado.append([f, 'x'])  # se agrega una bandera x para denotar que no hay pago
                else:
                    list_facts_contado.append([f, 'x'])  # se agrega una bandera x para denotar que no hay pago

            simpleWrite('LISTADO DE VENTAS AL CONTADO', bold)
            breakAndWrite('DESDE:', bold)
            rightAndWrite(wizard.fecha, date_only)
            breakAndWrite('HASTA:', bold)
            rightAndWrite(wizard.fecha_fin, date_only)

            addSalto()
            breakAndWrite('NOMBRE DEL CLIENTE', bold)
            rightAndWrite('TIPO', bold)
            rightAndWrite('FECHA DE PAGO', bold)
            rightAndWrite('NUMERO DE FACTURA', bold)
            rightAndWrite('MONTO', bold)
            rightAndWrite('NUMERO DE PAGO', bold)
            rightAndWrite('METODO', bold)

            total_usd = 0
            total_pyg = 0
            total_equivalente = 0

            total_contado = 0
            total_credito = 0

            total_efectivo = 0
            total_cheque = 0

            for factura in facturas:
                if factura[0].currency_id.name == 'USD':
                    total_usd = total_usd + factura[0].amount_total
                    total_equivalente = total_equivalente + round(
                        factura[0].currency_id._convert(factura[0].amount_total, self.env.company.currency_id, self.env.company, fecha, round=True), 0)
                    total_contado = total_contado + round(
                        factura[0].currency_id._convert(factura[0].amount_total, self.env.company.currency_id, self.env.company, fecha, round=True), 0)
                    if not factura[1] == 'x':
                        if factura[1].tipo_pago == 'Efectivo':
                            total_efectivo = total_efectivo + round(
                                factura[0].currency_id._convert(factura[0].amount_total, self.env.company.currency_id, self.env.company, fecha, round=True), 0)
                        if factura[1].tipo_pago == 'Cheque':
                            total_cheque = total_cheque + round(
                                factura[0].currency_id._convert(factura[0].amount_total, self.env.company.currency_id, self.env.company, fecha, round=True), 0)
                if factura[0].currency_id.name == 'PYG':
                    total_pyg = total_pyg + factura[0].amount_total
                    total_contado = total_contado + factura[0].amount_total
                    if not factura[1] == 'x':
                        if factura[1].tipo_pago == 'Efectivo':
                            total_efectivo = total_efectivo + factura[0].amount_total
                        if factura[1].tipo_pago == 'Cheque':
                            total_cheque = total_cheque + factura[0].amount_total
                breakAndWrite(factura[0].partner_id.name)
                rightAndWrite('Contado')
                rightAndWrite(factura[0].invoice_date)
                rightAndWrite(factura[0].name)
                rightAndWrite(factura[0].currency_id.name)
                if factura[0].currency_id.name == 'PYG':
                    rightAndWrite(int(factura[0].amount_total), numerico)
                else:
                    rightAndWrite(factura[0].amount_total, numerico)

                if not factura[1] == 'x':
                    rightAndWrite(factura[1].name)
                else:
                    addRight()

                if not factura[1] == 'x':
                    rightAndWrite(factura[1].tipo_pago)
                else:
                    addRight()

            addSalto()
            breakAndWrite('TOTAL GS:', bold)
            rightAndWrite(int(total_pyg), numerico)

            addSalto()
            breakAndWrite('TOTAL US:', bold)
            rightAndWrite(total_usd, numerico)

            addSalto()
            breakAndWrite('EQUIVALENTE DE LA VENTA EN USD::', bold)
            rightAndWrite(int(total_equivalente), numerico)

            addSalto()
            breakAndWrite('GRAN TOTAL:', bold)
            rightAndWrite(int(total_equivalente + total_pyg), numerico)

            addSalto()
            breakAndWrite('TOTAL CONTADO:', bold)
            rightAndWrite(int(total_contado), numerico)

            addSalto()
            breakAndWrite('TOTAL EFECTIVO:', bold)
            rightAndWrite(int(total_efectivo), numerico)

            addSalto()
            breakAndWrite('TOTAL NOTA DE CREDITO:', bold)
            rightAndWrite(int(total_credito), numerico)

            addSalto()
            breakAndWrite('TOTAL CHEQUE:', bold)
            rightAndWrite(int(total_cheque), numerico)
        if wizard.tipo_reporte == 'ventas_credito':
            sheet = workbook.add_worksheet('LISTADO DE VENTAS A CREDITO')
            facturas = self.env['account.move'].search([
                ('company_id', '=', self.env.user.company_id.id),
                ('invoice_date_due', '!=', wizard.fecha),
                ('move_type', '=', 'out_invoice'),
                ('state', 'in', ['posted']),
                ('invoice_date', '>=', wizard.fecha),
                ('invoice_date', '<=', wizard.fecha_fin)
            ])

            rate = 0
            for factura in facturas:
                if factura.currency_id.name == 'USD':
                    rate = factura.currency_id._get_conversion_rate(factura.currency_id, self.env.user.company_id.currency_id, self.env.user.company_id,
                                                                    factura.invoice_date)
            rate_usd = round(rate, 0)

            simpleWrite('LISTADO DE VENTAS AL CONTADO', bold)
            breakAndWrite('DESDE:', bold)
            rightAndWrite(wizard.fecha, date_only)
            breakAndWrite('HASTA:', bold)
            rightAndWrite(wizard.fecha_fin, date_only)

            addSalto()
            breakAndWrite('NOMBRE DEL CLIENTES', bold)
            rightAndWrite('TIPO DE PAGO', bold)
            rightAndWrite('FECHA DE FACTURA', bold)
            rightAndWrite('NUMERO DE FACTURA', bold)
            rightAndWrite('MONEDA DE LA FACTURA', bold)
            rightAndWrite('MONTO DE FACTURA', bold)

            total_usd = 0
            total_pyg = 0
            total_equivalente = 0

            for factura in facturas:
                if factura.currency_id.name == 'USD':
                    total_usd = total_usd + factura.amount_total
                    total_equivalente = total_equivalente + round(
                        factura.currency_id._convert(factura.amount_total, self.env.company.currency_id, self.env.company, wizard.fecha, round=True), 0)
                if factura.currency_id.name == 'PYG':
                    total_pyg = total_pyg + factura.amount_total

                breakAndWrite(factura.partner_id.name)
                rightAndWrite(factura.invoice_payment_term_id.name)
                rightAndWrite(factura.invoice_date, date_only)
                rightAndWrite(factura.name)
                rightAndWrite(factura.currency_id.name)
                if factura.currency_id.name == 'PYG':
                    rightAndWrite(int(factura.amount_total), numerico)
                else:
                    rightAndWrite(factura.amount_total, numerico)

            addSalto()
            breakAndWrite('TIPO DE CAMBIO:', bold)
            rightAndWrite(int(rate_usd), numerico)

            breakAndWrite('TOTAL GS:', bold)
            rightAndWrite(int(total_pyg), numerico)

            breakAndWrite('TOTAL US:', bold)
            rightAndWrite(int(total_usd), numerico)

            breakAndWrite('EQUIVALENTE DE LA VENTA EN USD:', bold)
            rightAndWrite(int(total_equivalente), numerico)

            breakAndWrite('GRAN TOTAL:', bold)
            rightAndWrite(int(total_equivalente + total_pyg), numerico)
        if wizard.tipo_reporte == 'reporte_cobranzas':
            sheet = workbook.add_worksheet('REPORTE DE COBRANZAS')
            pagos_gs = self.env['account.payment'].search([
                ('payment_type', '=', 'inbound'),
                ('date', '>=', wizard.fecha),
                ('date', '<=', wizard.fecha_fin),
                ('currency_id', '=', 'PYG'),
                ('state', '=', 'posted')
            ])

            pagos_us = self.env['account.payment'].search([
                ('payment_type', '=', 'inbound'),
                ('date', '>=', wizard.fecha),
                ('date', '<=', wizard.fecha_fin),
                ('currency_id', '=', 'USD'),
                ('state', '=', 'posted')
            ])

            pagos = self.env['account.payment'].search([
                ('payment_type', '=', 'inbound'),
                ('date', '>=', wizard.fecha),
                ('date', '<=', wizard.fecha_fin),
                ('state', '=', 'posted')
            ])

            for c in pagos:
                if c.tipo_pago == 'Retencion':
                    print(f"id: {c}")
            # print(f"pagos: {pagos}")
            company = self.env.user.company_id

            simpleWrite('REPORTE DE COBRANZAS GS', bold)
            breakAndWrite('DESDE:', bold)
            rightAndWrite(wizard.fecha, date_only)
            breakAndWrite('HASTA:', bold)
            rightAndWrite(wizard.fecha_fin, date_only)

            addSalto()
            breakAndWrite('CLIENTE', bold)
            rightAndWrite('CONDICION', bold)
            rightAndWrite('FECHA', bold)
            rightAndWrite('NRO FACTURA', bold)
            rightAndWrite('IMPORTE PYG', bold)
            rightAndWrite('FECHA RECIBO', bold)
            rightAndWrite('COMPROBANTE', bold)
            rightAndWrite('CHEQUE', bold)
            rightAndWrite('TRANSFERENCIA', bold)
            rightAndWrite('EFECTIVO', bold)
            rightAndWrite('RETENCIÓN', bold)
            rightAndWrite('TOTAL COBRADO', bold)

            total_cheque_gs = 0
            total_efectivo_gs = 0
            total_transferencia_gs = 0
            total_tc_gs = 0
            total_td_gs = 0
            total_retenciones_gs = 0
            total_general_gs = 0
            total_monto_efectivo = 0

            for pago in pagos_gs:
                for rec in pago.move_id._get_reconciled_invoices_partials():
                    for data in rec:
                        if isinstance(data, tuple):
                            amount = data[1]
                            inv = data[2].move_id
                            if inv.move_type != 'entry' and inv.currency_id.name == 'PYG':
                                if pago.tipo_pago == 'TCredito':
                                    total_tc_gs = total_tc_gs + amount
                                if pago.tipo_pago == 'TDebito':
                                    total_td_gs = total_td_gs + amount
                                if pago.tipo_pago == 'Retencion':
                                    total_retenciones_gs = total_retenciones_gs + amount
                                total_general_gs = total_general_gs + amount
                                total_monto_cheque = 0
                                total_monto_trans = 0
                                calculo_retencion = 0
                                for retencion in pago.move_id.line_ids:
                                    if retencion.account_id.name == 'Retención IVA':
                                        retencion1 = retencion.debit
                                        cal_div = (amount / 11)
                                        calculo_retencion = (int(cal_div) * float(0.3))
                                        total_retenciones_gs = total_retenciones_gs + calculo_retencion
                                        total_monto = amount - calculo_retencion
                                        if pago.tipo_pago == 'Cheque':
                                            total_monto_cheque = total_monto
                                        if pago.tipo_pago == 'Transferencia':
                                            total_monto_trans = total_monto
                                        if pago.tipo_pago == 'Efectivo':
                                            total_monto_efectivo = total_monto
                                if pago.tipo_pago == 'Cheque':
                                    if total_monto_cheque:
                                        total_cheque_gs = total_cheque_gs + total_monto_cheque
                                    else:
                                        total_cheque_gs = total_cheque_gs + amount

                                if pago.tipo_pago == 'Transferencia':
                                    if total_monto_trans:
                                        total_transferencia_gs = total_transferencia_gs + total_monto_trans
                                    else:
                                        total_transferencia_gs = total_transferencia_gs + amount

                                if pago.tipo_pago == 'Efectivo':
                                    if total_monto_efectivo:
                                        total_efectivo_gs = total_efectivo_gs + total_monto_efectivo
                                    else:
                                        total_efectivo_gs = total_efectivo_gs + amount

                                breakAndWrite(inv.partner_id.name)
                                if inv.invoice_date < inv.invoice_date_due:
                                    rightAndWrite('Crédito')
                                else:
                                    rightAndWrite('Contado')
                                rightAndWrite(inv.invoice_date, date_only)
                                rightAndWrite(inv.name)
                                if inv.currency_id.name == 'PYG':
                                    rightAndWrite(int(inv.amount_total), numerico)
                                else:
                                    rightAndWrite(inv.amount_total, numerico)
                                rightAndWrite(pago.date, date_only)
                                rightAndWrite(pago.nro_recibo, text_right)

                                if pago.tipo_pago == 'Cheque':
                                    if total_monto_cheque:
                                        rightAndWrite(int(total_monto_cheque), numerico)
                                    else:
                                        rightAndWrite(int(amount), numerico)
                                else:
                                    rightAndWrite(0, numerico)

                                if pago.tipo_pago == 'Transferencia':
                                    if total_monto_trans:
                                        rightAndWrite(int(total_monto_trans), numerico)
                                    else:
                                        rightAndWrite(int(amount), numerico)
                                else:
                                    rightAndWrite(0, numerico)

                                if pago.tipo_pago == 'Efectivo':
                                    if total_monto_efectivo:
                                        rightAndWrite(int(total_monto_efectivo), numerico)
                                    else:
                                        rightAndWrite(int(amount), numerico)
                                else:
                                    rightAndWrite(0, numerico)
                                valor_mostrar = 0

                                if pago.tipo_pago == 'Retencion':
                                    if amount:
                                        valor_mostrar = int(amount)

                                for retencion in pago.move_id.line_ids:
                                    if retencion.account_id.id == 2447:
                                        valor_mostrar = int(calculo_retencion)
                                        valor_retencion = calculo_retencion
                                rightAndWrite(valor_mostrar, numerico)
                                rightAndWrite(int(amount), numerico)

            addSalto(), addRight(), addRight(), addRight(), addRight(), addRight(), addRight()
            simpleWrite('TOTALES')
            rightAndWrite(int(total_cheque_gs), numerico)
            rightAndWrite(int(total_transferencia_gs), numerico)
            rightAndWrite(int(total_efectivo_gs), numerico)
            rightAndWrite(int(total_retenciones_gs), numerico)
            rightAndWrite(int(total_general_gs), numerico)

            addSalto()
            breakAndWrite('Total Cheque')
            rightAndWrite(int(total_cheque_gs), numerico)
            breakAndWrite('Total Efectivo')
            rightAndWrite(int(total_efectivo_gs), numerico)
            breakAndWrite('Total Transferencias')
            rightAndWrite(int(total_transferencia_gs), numerico)
            breakAndWrite('Total Tarjeta de Crédito')
            rightAndWrite(int(total_tc_gs), numerico)
            breakAndWrite('Total Tarjeta de Débito')
            rightAndWrite(int(total_td_gs), numerico)
            breakAndWrite('Total Retenciones')
            rightAndWrite(int(total_retenciones_gs), numerico)
            breakAndWrite('Total General')
            rightAndWrite(int(total_general_gs), numerico)

            sheet = workbook.add_worksheet('REPORTE DE COBRANZAS US')
            position_x = 0
            position_y = 0

            simpleWrite('REPORTE DE COBRANZAS', bold)
            breakAndWrite('DESDE:', bold)
            rightAndWrite(wizard.fecha, date_only)
            breakAndWrite('HASTA:', bold)
            rightAndWrite(wizard.fecha_fin, date_only)

            addSalto()
            breakAndWrite('CLIENTE', bold)
            rightAndWrite('CONDICION', bold)
            rightAndWrite('FECHA', bold)
            rightAndWrite('NRO FACTURA', bold)
            rightAndWrite('IMPORTE PYG', bold)
            rightAndWrite('FECHA RECIBO', bold)
            rightAndWrite('COMPROBANTE', bold)
            rightAndWrite('CHEQUE', bold)
            rightAndWrite('TRANSFERENCIA', bold)
            rightAndWrite('EFECTIVO', bold)
            rightAndWrite('RETENCIÓN', bold)
            rightAndWrite('DIFERENCIA DE CAMBIO', bold)
            rightAndWrite('TOTAL COBRADO', bold)

            total_cheque_us = 0
            total_efectivo_us = 0
            total_transferencia_us = 0
            total_tc_us = 0
            total_td_us = 0
            total_retenciones_us = 0
            total_diferencia = 0
            total_general_us = 0

            for pago in pagos_us:
                for rec in pago.move_id._get_reconciled_invoices_partials():
                    for data in rec:
                        if isinstance(data, tuple):
                            amount = data[1]
                            inv = data[2].move_id
                            if inv.move_type != 'entry':
                                if pago.tipo_pago == 'TCredito':
                                    total_tc_us = total_tc_us + amount
                                if pago.tipo_pago == 'TDebito':
                                    total_td_us = total_td_us + amount
                                if pago.tipo_pago == 'Retencion':
                                    total_retenciones_us = total_retenciones_us + amount
                                total_general_us = total_general_us + amount
                                total_monto_cheque_us = 0
                                total_monto_trans_us = 0
                                total_monto_efectivo_us = 0
                                calculo_diferencia = 0
                                for diferencia in pago.move_id.line_ids:
                                    if diferencia.account_id.name == 'Retención IVA':
                                        diferencia1 = diferencia.debit
                                        cal_div = (amount / 11)
                                        calculo_diferencia = (int(cal_div) * float(0.3))
                                        total_diferencia = total_diferencia + calculo_diferencia
                                        total_monto_us = amount - calculo_diferencia
                                        if pago.tipo_pago == 'Cheque':
                                            total_monto_cheque_us = total_monto_us
                                        if pago.tipo_pago == 'Transferencia':
                                            total_monto_trans_us = total_monto_us
                                        if pago.tipo_pago == 'Efectivo':
                                            total_monto_efectivo_us = total_monto_us
                                if pago.tipo_pago == 'Cheque':
                                    if total_monto_cheque_us:
                                        total_cheque_us = total_cheque_us + total_monto_cheque_us
                                    else:
                                        total_cheque_us = total_cheque_us + amount

                                if pago.tipo_pago == 'Transferencia':
                                    if total_monto_trans_us:
                                        total_transferencia_us = total_transferencia_us + total_monto_trans_us
                                    else:
                                        total_transferencia_us = total_transferencia_us + amount

                                if pago.tipo_pago == 'Efectivo':
                                    if total_monto_efectivo_us:
                                        total_efectivo_us = total_efectivo_us + total_monto_efectivo_us
                                    else:
                                        total_efectivo_us = total_efectivo_us + amount

                                breakAndWrite(inv.partner_id.name)
                                if inv.invoice_date < inv.invoice_date_due:
                                    rightAndWrite('Crédito')
                                else:
                                    rightAndWrite('Contado')
                                rightAndWrite(inv.invoice_date, date_only)
                                rightAndWrite(inv.name)
                                if inv.currency_id.name == 'PYG':
                                    rightAndWrite(int(inv.amount_total), numerico)
                                else:
                                    rightAndWrite(inv.amount_total, numerico)
                                rightAndWrite(pago.date, date_only)
                                rightAndWrite(pago.nro_recibo, text_right)

                                if pago.tipo_pago == 'Cheque':
                                    if total_monto_cheque:
                                        rightAndWrite(int(total_monto_cheque), numerico)
                                    else:
                                        rightAndWrite(int(amount), numerico)
                                else:
                                    rightAndWrite(0, numerico)

                                if pago.tipo_pago == 'Transferencia':
                                    if total_monto_trans_us:
                                        rightAndWrite(int(total_monto_trans_us), numerico)
                                    else:
                                        rightAndWrite(int(amount), numerico)
                                else:
                                    rightAndWrite(0, numerico)

                                if pago.tipo_pago == 'Efectivo':
                                    if total_monto_efectivo_us:
                                        rightAndWrite(int(total_monto_efectivo_us), numerico)
                                    else:
                                        rightAndWrite(int(amount), numerico)
                                else:
                                    rightAndWrite(0, numerico)

                                valor_mostrar = 0
                                if pago.tipo_pago == 'Retencion':
                                    if amount:
                                        valor_mostrar = int(amount)

                                for retencion in pago.move_id.line_ids:
                                    if retencion.account_id.id == 2740:
                                        valor_mostrar = int(calculo_diferencia)

                                rightAndWrite(valor_mostrar, numerico)
                                rightAndWrite(calculo_diferencia, numerico)
                                rightAndWrite(int(amount), numerico)

            addSalto(), addRight(), addRight(), addRight(), addRight(), addRight(), addRight()
            simpleWrite('TOTALES')
            rightAndWrite(int(total_cheque_us), numerico)
            rightAndWrite(int(total_transferencia_us), numerico)
            rightAndWrite(int(total_efectivo_us), numerico)
            rightAndWrite(int(total_retenciones_us), numerico)
            rightAndWrite(int(total_diferencia), numerico)
            rightAndWrite(int(total_general_us), numerico)

            addSalto()
            breakAndWrite('Total Cheque')
            rightAndWrite(int(total_cheque_us), numerico)
            breakAndWrite('Total Efectivo')
            rightAndWrite(int(total_efectivo_us), numerico)
            breakAndWrite('Total Transferencias')
            rightAndWrite(int(total_transferencia_us), numerico)
            breakAndWrite('Total Tarjeta de Crédito')
            rightAndWrite(int(total_tc_us), numerico)
            breakAndWrite('Total Tarjeta de Débito')
            rightAndWrite(int(total_td_us), numerico)
            breakAndWrite('Total Retenciones')
            rightAndWrite(int(total_retenciones_us), numerico)
            breakAndWrite('Total Diferencia de Cambio')
            rightAndWrite(int(total_diferencia), numerico)
            breakAndWrite('Total General')
            rightAndWrite(int(total_general_us), numerico)

            sheet = workbook.add_worksheet('REPORTE DE COBRANZAS CHEQUES')
            position_x = 0
            position_y = 0

            simpleWrite('REPORTE DE COBRANZAS', bold)
            breakAndWrite('DESDE:', bold)
            rightAndWrite(wizard.fecha, date_only)
            breakAndWrite('HASTA:', bold)
            rightAndWrite(wizard.fecha_fin, date_only)

            addSalto()
            breakAndWrite('CLIENTE', bold)
            rightAndWrite('COMPROBANTE', bold)
            rightAndWrite('BANCO', bold)
            rightAndWrite('NRO DE CHEQUE', bold)
            rightAndWrite('TRANSFERENCIA', bold)
            rightAndWrite('MONTO', bold)

            total_gs = 0
            total_us = 0

            for pago in pagos.filtered(lambda x: x.tipo_pago == 'Cheque'):
                breakAndWrite(pago.partner_id.name)
                rightAndWrite(pago.nro_recibo, text_right)
                rightAndWrite(pago.bank_id.name)
                rightAndWrite(pago.nro_cheque)
                if pago.currency_id.name == 'PYG':
                    total_gs = total_gs + pago.amount
                    rightAndWrite(int(pago.amount))
                if pago.currency_id.name == 'USD':
                    total_us = total_us + pago.amount
                    rightAndWrite(int(pago.amount))

            addSalto()
            breakAndWrite('TOTAL GUARANIES')
            rightAndWrite(int(int(total_gs)), numerico)
            breakAndWrite('TOTAL DOLARES')
            rightAndWrite(int(int(total_us)), numerico)

            for tipo_cobranza in ['Transferencia', 'Efectivo', 'TDebito', 'TCredito', 'Retencion']:

                sheet = workbook.add_worksheet('REPORTE DE COBRANZAS ' + tipo_cobranza.upper())
                position_x = 0
                position_y = 0

                simpleWrite('REPORTE DE COBRANZAS', bold)
                breakAndWrite('DESDE:', bold)
                rightAndWrite(wizard.fecha, date_only)
                breakAndWrite('HASTA:', bold)
                rightAndWrite(wizard.fecha_fin, date_only)

                addSalto()
                breakAndWrite('CLIENTE', bold)
                rightAndWrite('COMPROBANTE', bold)
                rightAndWrite('MONTO', bold)

                total_gs = 0
                total_us = 0

                for pago in pagos.filtered(lambda x: x.tipo_pago == tipo_cobranza):
                    breakAndWrite(pago.partner_id.name)
                    rightAndWrite(pago.nro_recibo, text_right)
                    if pago.currency_id.name == 'PYG':
                        total_gs = total_gs + pago.amount
                        rightAndWrite(int(pago.amount))
                    if pago.currency_id.name == 'USD':
                        total_us = total_us + pago.amount
                        rightAndWrite(int(pago.amount))

                addSalto()
                breakAndWrite('TOTAL GUARANIES')
                rightAndWrite(int(int(total_gs)), numerico)
                breakAndWrite('TOTAL DOLARES')
                rightAndWrite(int(int(total_us)), numerico)

        # sheet.set_column(0, 6, 30)
