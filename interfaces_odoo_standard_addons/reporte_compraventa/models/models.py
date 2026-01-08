# -*- coding: utf-8 -*-

from odoo import models, fields, api
import xlsxwriter
import base64


class WizardReporteCompra(models.TransientModel):
    _name = "reporte_compraventa.wizardcompra"

    fecha_inicio = fields.Date(string="Fecha Inicio", required=True)
    fecha_fin = fields.Date(string="Fecha Fin", required=True)

    def print_report(self):
        datas = {
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
        }

        return self.env.ref("reporte_compraventa.account_invoices_compras_action").report_action(self, data=datas)

    def print_report_xlsx(self):
        return self.env.ref("reporte_compraventa.reporte_compra_xlsx_action").report_action(self)


class ReporteComprasXLSX(models.AbstractModel):
    _name = "report.reporte_compraventa.reporte_compra_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def get_facturas_libro_compra(self, fecha_inicio, fecha_fin):
        return self.env["account.move"].search(
            [
                ("move_type", "=", "in_invoice"),
                ("state", "in", ["posted"]),
                ("invoice_date", ">=", fecha_inicio),
                ("invoice_date", "<=", fecha_fin),
                ("line_ids.tax_ids", "!=", False),
            ]
        )

    def get_proveedor(self, invoice, campo):
        if campo == "name":
            return invoice.partner_id.name
        if campo == "vat":
            return invoice.partner_id.vat

    def get_impuestos(self, invoice_line):
        """
        Retorna un diccionario con los valores de los impuestos de la factura.
        Solo se suman los montos si la factura no esta cancelada.
        En el caso de que la factura no tenga impuestos, se retorna 0 para todos los valores.
        """
        base10 = 0
        iva10 = 0
        base5 = 0
        iva5 = 0
        exentas = 0

        # Solo se suman los montos si la factura no esta cancelada
        if invoice_line.move_id.state != "cancel":
            # Suma de exentas
            if (invoice_line.tax_ids and invoice_line.tax_ids[0].amount == 0) or not invoice_line.tax_ids:
                exentas += invoice_line.price_total

            # Suma de IVA 5
            if invoice_line.tax_ids and invoice_line.tax_ids[0].amount == 5:
                base5 += invoice_line.price_total / 1.05
                iva5 += invoice_line.price_total / 21

            # Suma de IVA 10
            if invoice_line.tax_ids and invoice_line.tax_ids[0].amount == 10:
                base10 += invoice_line.price_total / 1.1
                iva10 += invoice_line.price_total / 11

        result = {
            "base10": base10,
            "iva10": iva10,
            "base5": base5,
            "iva5": iva5,
            "exentas": exentas,
            "imponible_importaciones": 0,
        }

        return result

    def generate_xlsx_report(self, workbook, data, datas):

        facturas = self.get_facturas_libro_compra(datas.fecha_inicio, datas.fecha_fin)
        global sheet
        global bold
        global num_format
        global position_x
        global position_y
        sheet = workbook.add_worksheet("Hoja 1")
        bold = workbook.add_format({"bold": True})
        numerico = workbook.add_format({"num_format": True, "align": "right"})
        numerico.set_num_format("#,##0")
        numerico_total = workbook.add_format({"num_format": True, "align": "right", "bold": True})
        numerico_total.set_num_format("#,##0")
        wrapped_text = workbook.add_format()
        wrapped_text.set_text_wrap()
        wrapped_text_bold = workbook.add_format({"bold": True})
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

        def breakAndWrite(to_write, format=None):
            global sheet
            addSalto()
            sheet.write(position_y, position_x, to_write, format)

        def simpleWrite(to_write, format=None):
            global sheet
            sheet.write(position_y, position_x, to_write, format)

        def rightAndWrite(to_write, format=None):
            global sheet
            addRight()
            sheet.write(position_y, position_x, to_write, format)

        simpleWrite("Razon social:", bold)
        rightAndWrite(self.env.company.name)
        breakAndWrite("RUC:", bold)
        rightAndWrite(self.env.company.partner_id.vat)
        breakAndWrite("Periodo:", bold)
        rightAndWrite("Del " + datas.fecha_inicio.strftime("%d/%m/%Y") + " al " + datas.fecha_fin.strftime("%d/%m/%Y"))
        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        simpleWrite("Libro de compras - Ley 125/91", bold)
        breakAndWrite("Nro", bold)
        rightAndWrite("Fecha", bold)
        rightAndWrite("Proveedor", bold)
        rightAndWrite("RUC del Proveedor", wrapped_text_bold)
        rightAndWrite("Tipo doc.", bold)
        rightAndWrite("Nro. doc.", bold)
        rightAndWrite("Timbrado", bold)
        rightAndWrite("Importe sin IVA 10%", wrapped_text_bold)
        rightAndWrite("Crédito fiscal 10%", wrapped_text_bold)
        rightAndWrite("Importe sin IVA 5%", wrapped_text_bold)
        rightAndWrite("Crédito fiscal 5%", wrapped_text_bold)
        rightAndWrite("Importes exentos", wrapped_text_bold)
        rightAndWrite("Total", wrapped_text_bold)
        rightAndWrite("Base Imponible Importaciones", wrapped_text_bold)

        cont = 0
        total_gral_base10 = 0
        total_gral_iva10 = 0
        total_gral_base5 = 0
        total_gral_iva5 = 0
        total_gral_exentas = 0
        total_gral_total = 0
        total_imponible_importaciones = 0
        for i in facturas.sorted(key=lambda r: r.invoice_date):
            cont += 1
            """
            if not i.es_gasto:
                total_factura = i.amount_total_signed
            elif i.es_gasto and not i.tipo_gasto == 'despacho':
                total_factura = i.amount_total_signed
            elif i.es_gasto and i.tipo_gasto == 'despacho':
                total_factura = 0
            else:
            """
            base10 = 0
            iva10 = 0
            base5 = 0
            iva5 = 0
            exentas = 0
            imponible_importaciones = 0
            for invoice_line in i.invoice_line_ids.filtered(
                lambda x: not x.product_id.categ_id.excluir_reporte_compraventa and x.display_type not in ["line_note", "line_section"]
            ):
                impuestos = self.get_impuestos(invoice_line)
                base10 += impuestos["base10"]
                iva10 += impuestos["iva10"]
                base5 += impuestos["base5"]
                iva5 += impuestos["iva5"]
                exentas += impuestos["exentas"]
                imponible_importaciones += impuestos["imponible_importaciones"]

            total_factura = base10 + iva10 + base5 + iva5 + exentas

            if i.currency_id != self.env.company.currency_id:
                balance = 1
                amount_currency = 1
                balance = sum(abs(line.balance) for line in i.line_ids.filtered(lambda x: x.currency_id == i.currency_id))
                amount_currency = sum(abs(line.amount_currency) for line in i.line_ids.filtered(lambda x: x.currency_id == i.currency_id))
                if balance > 0 and amount_currency > 0:
                    currency_rate = balance / amount_currency
                    currency_rate = i.currency_id.round(currency_rate)
                else:
                    currency_rate = 1

                base10 = base10 * currency_rate
                iva10 = iva10 * currency_rate
                base5 = base5 * currency_rate
                iva5 = iva5 * currency_rate
                exentas = exentas * currency_rate
                total_factura = base10 + iva10 + base5 + iva5 + exentas

            total_gral_base10 += base10
            total_gral_iva10 += iva10
            total_gral_base5 += base5
            total_gral_iva5 += iva5
            total_gral_exentas += exentas
            total_gral_total += total_factura
            total_imponible_importaciones += imponible_importaciones

            breakAndWrite(cont)
            rightAndWrite(i.invoice_date.strftime("%d/%m/%Y"))
            # rightAndWrite(i.partner_id.name)
            rightAndWrite(self.get_proveedor(i, "name"))
            # rightAndWrite(i.partner_id.vat)
            rightAndWrite(self.get_proveedor(i, "vat"))

            if i.invoice_date < i.invoice_date_due:
                rightAndWrite("Credito")
            else:
                rightAndWrite("Contado")
            rightAndWrite(i.ref)
            rightAndWrite(i.timbrado_proveedor or "")
            rightAndWrite(base10, numerico)
            rightAndWrite(iva10, numerico)
            rightAndWrite(base5, numerico)
            rightAndWrite(iva5, numerico)
            rightAndWrite(exentas, numerico)
            rightAndWrite(total_factura, numerico)
            rightAndWrite(imponible_importaciones, numerico)

        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        rightAndWrite(total_gral_base10, numerico_total)
        rightAndWrite(total_gral_iva10, numerico_total)
        rightAndWrite(total_gral_base5, numerico_total)
        rightAndWrite(total_gral_iva5, numerico_total)
        rightAndWrite(total_gral_exentas, numerico_total)
        rightAndWrite(total_gral_total, numerico_total)
        rightAndWrite(total_imponible_importaciones, numerico_total)

        notas = self.env["account.move"].search(
            [
                ("move_type", "=", "out_refund"),
                ("state", "in", ["posted", "cancel"]),
                ("invoice_date", ">=", datas.fecha_inicio),
                ("invoice_date", "<=", datas.fecha_fin),
                ("line_ids.tax_ids", "!=", False),
            ]
        )

        breakAndWrite("Notas de crédito emitidas", bold)
        breakAndWrite("Nro", bold)
        rightAndWrite("Fecha", bold)
        rightAndWrite("Cliente", bold)
        rightAndWrite("RUC o CI del Cliente", wrapped_text_bold)
        rightAndWrite("Tipo doc.", bold)
        rightAndWrite("Nro. doc.", bold)
        rightAndWrite("Timbrado", bold)  # Se agrega el timbrado
        rightAndWrite("Importe sin IVA 10%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 10%", wrapped_text_bold)
        rightAndWrite("Importe sin IVA 5%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 5%", wrapped_text_bold)
        rightAndWrite("Importes exentos", wrapped_text_bold)
        rightAndWrite("Importe total con IVA incluido", wrapped_text_bold)

        cont = 0
        total_gral_total = 0
        total_gral_base10 = 0
        total_gral_base5 = 0
        total_gral_iva10 = 0
        total_gral_iva5 = 0
        total_gral_exentas = 0
        for i in notas.sorted(key=lambda x: x.name):
            cont += 1
            if i.state != "cancel":
                total_factura = abs(i.amount_total_signed)
            else:
                total_factura = 0

            base10 = 0
            iva10 = 0
            base5 = 0
            iva5 = 0
            exentas = 0
            imponible_importaciones = 0
            for invoice_line in i.invoice_line_ids.filtered(
                lambda x: not x.product_id.categ_id.excluir_reporte_compraventa and x.display_type not in ["line_note", "line_section"]
            ):
                impuestos = self.get_impuestos(invoice_line)
                base10 += impuestos["base10"]
                iva10 += impuestos["iva10"]
                base5 += impuestos["base5"]
                iva5 += impuestos["iva5"]
                exentas += impuestos["exentas"]
                imponible_importaciones += impuestos["imponible_importaciones"]

            if i.currency_id != self.env.company.currency_id:
                balance = 1
                amount_currency = 1
                balance = sum(abs(line.balance) for line in i.line_ids.filtered(lambda x: x.currency_id == i.currency_id))
                amount_currency = sum(abs(line.amount_currency) for line in i.line_ids.filtered(lambda x: x.currency_id == i.currency_id))
                if balance > 0 and amount_currency > 0:
                    currency_rate = balance / amount_currency
                    currency_rate = i.currency_id.round(currency_rate)
                else:
                    currency_rate = 1

                base10 = base10 * currency_rate
                iva10 = iva10 * currency_rate
                base5 = base5 * currency_rate
                iva5 = iva5 * currency_rate
                exentas = exentas * currency_rate
                total_factura = base10 + iva10 + base5 + iva5 + exentas

            total_gral_total += total_factura
            total_gral_base10 += base10
            total_gral_base5 += base5
            total_gral_iva10 += iva10
            total_gral_iva5 += iva5
            total_gral_exentas += exentas

            breakAndWrite(cont)
            if i.state != "cancel":
                rightAndWrite(i.invoice_date.strftime("%d/%m/%Y"))
            else:
                rightAndWrite("")
            if i.state != "cancel":
                rightAndWrite(i.partner_id.name)
            else:
                rightAndWrite("Anulado")
            if i.state != "cancel":
                rightAndWrite(i.partner_id.vat)
            else:
                rightAndWrite("")

            if i.state != "cancel":

                rightAndWrite("Nota de crédito")
            else:
                rightAndWrite("")
            rightAndWrite(i.name)
            # valor del timbrado Libro Compra
            if i.state != "cancel":
                rightAndWrite(i.timbrado if i.timbrado else "")
            else:
                rightAndWrite("")
            if i.state != "cancel":
                rightAndWrite(base10, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(iva10, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(base5, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(iva5, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(exentas, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(total_factura, numerico)
            else:
                rightAndWrite(0)
        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        rightAndWrite(total_gral_base10, numerico_total)
        rightAndWrite(total_gral_iva10, numerico_total)
        rightAndWrite(total_gral_base5, numerico_total)
        rightAndWrite(total_gral_iva5, numerico_total)
        rightAndWrite(total_gral_exentas, numerico_total)
        rightAndWrite(total_gral_total, numerico_total)


class WizardReporteVenta(models.TransientModel):
    _name = "reporte_compraventa.wizardventa"

    fecha_inicio = fields.Date(string="Fecha Inicio", required=True)
    fecha_fin = fields.Date(string="Fecha Fin", required=True)

    def print_report(self):
        datas = {
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
        }

        return self.env.ref("reporte_compraventa.account_invoices_ventas_action").report_action(self, data=datas)

    def print_report_xlsx(self):
        return self.env.ref("reporte_compraventa.reporte_venta_xlsx_action").report_action(self)


class ReporteVentasXLSX(models.AbstractModel):
    _name = "report.reporte_compraventa.reporte_venta_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def get_impuestos(self, invoice):
        """
        Retorna un diccionario con los valores de los impuestos de la factura.
        Solo se suman los montos si la factura no esta cancelada.
        En el caso de que la factura no tenga impuestos, se retorna 0 para todos los valores.
        """
        base10 = 0
        iva10 = 0
        base5 = 0
        iva5 = 0
        exentas = 0
        sumar_impuestos = True

        # Solo se suman los montos si la factura no esta cancelada
        if invoice.state == "cancel":
            sumar_impuestos = False

        # Obtenemos las lineas de la factura, filtrando que sean lineas facturables
        lineas = invoice.invoice_line_ids.filtered(lambda x: x.display_type not in ["line_note", "line_section"])
        if not lineas:
            sumar_impuestos = False

        if sumar_impuestos:
            # Verificamos si tiene grupos de impuestos creados, caso contrario obtenemos los impuestos de la forma antigua

            for l in lineas:
                # Suma de exentas
                if (l.tax_ids and l.tax_ids[0].amount == 0) or not l.tax_ids:
                    exentas += l.price_total

                # Suma de IVA 5
                if l.tax_ids and l.tax_ids[0].amount == 5:
                    base5 += l.price_total / 1.05
                    iva5 += l.price_total / 21

                # Suma de IVA 10
                if l.tax_ids and l.tax_ids[0].amount == 10:
                    base10 += l.price_total / 1.1
                    iva10 += l.price_total / 11

        result = {"base10": base10, "iva10": iva10, "base5": base5, "iva5": iva5, "exentas": exentas}

        return result

    def generate_xlsx_report(self, workbook, data, datas):

        facturas = self.env["account.move"].search(
            [
                ("move_type", "=", "out_invoice"),
                ("state", "in", ["posted", "cancel"]),
                ("invoice_date", ">=", datas.fecha_inicio),
                ("invoice_date", "<=", datas.fecha_fin),
            ]
        )
        global sheet
        global bold
        global num_format
        global position_x
        global position_y
        sheet = workbook.add_worksheet("Hoja 1")
        bold = workbook.add_format({"bold": True})
        numerico = workbook.add_format({"num_format": True, "align": "right"})
        numerico.set_num_format("#,##0")
        numerico_total = workbook.add_format({"num_format": True, "align": "right", "bold": True})
        numerico_total.set_num_format("#,##0")
        wrapped_text = workbook.add_format()
        wrapped_text.set_text_wrap()
        wrapped_text_bold = workbook.add_format({"bold": True})
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

        def breakAndWrite(to_write, format=None):
            global sheet
            addSalto()
            sheet.write(position_y, position_x, to_write, format)

        def simpleWrite(to_write, format=None):
            global sheet
            sheet.write(position_y, position_x, to_write, format)

        def rightAndWrite(to_write, format=None):
            global sheet
            addRight()
            sheet.write(position_y, position_x, to_write, format)

        simpleWrite("Razon social:", bold)
        rightAndWrite(self.env.company.name)
        breakAndWrite("RUC:", bold)
        rightAndWrite(self.env.company.partner_id.vat)
        breakAndWrite("Periodo:", bold)
        rightAndWrite("Del " + datas.fecha_inicio.strftime("%d/%m/%Y") + " al " + datas.fecha_fin.strftime("%d/%m/%Y"))
        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        simpleWrite("Libro de ventas - Ley 125/91", bold)
        breakAndWrite("Nro", bold)
        rightAndWrite("Fecha", bold)
        rightAndWrite("Cliente", bold)
        rightAndWrite("RUC o CI del Cliente", wrapped_text_bold)
        rightAndWrite("Tipo doc.", bold)
        rightAndWrite("Nro. doc.", bold)
        rightAndWrite("Timbrado", bold)  # Se agrega el timbrado
        rightAndWrite("Importe sin IVA 10%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 10%", wrapped_text_bold)
        rightAndWrite("Importe sin IVA 5%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 5%", wrapped_text_bold)
        rightAndWrite("Importes exentos", wrapped_text_bold)
        rightAndWrite("Importe total facturado con IVA incluido", wrapped_text_bold)

        cont = 0
        total_gral_total = 0
        total_gral_base10 = 0
        total_gral_base5 = 0
        total_gral_iva10 = 0
        total_gral_iva5 = 0
        total_gral_exentas = 0
        for i in facturas.sorted(key=lambda x: x.name):
            cont += 1
            if i.state != "cancel":
                total_factura = i.amount_total
            else:
                total_factura = 0

            impuestos = self.get_impuestos(i)
            base10 = impuestos["base10"]
            iva10 = impuestos["iva10"]
            base5 = impuestos["base5"]
            iva5 = impuestos["iva5"]
            exentas = impuestos["exentas"]

            if i.currency_id != self.env.company.currency_id:
                balance = 1
                amount_currency = 1
                balance = sum(abs(line.balance) for line in i.line_ids.filtered(lambda x: x.currency_id == i.currency_id))
                amount_currency = sum(abs(line.amount_currency) for line in i.line_ids.filtered(lambda x: x.currency_id == i.currency_id))
                if balance > 0 and amount_currency > 0:
                    currency_rate = balance / amount_currency
                    currency_rate = i.currency_id.round(currency_rate)
                else:
                    currency_rate = 1

                base10 = base10 * currency_rate
                iva10 = iva10 * currency_rate
                base5 = base5 * currency_rate
                iva5 = iva5 * currency_rate
                exentas = exentas * currency_rate
                total_factura = base10 + iva10 + base5 + iva5 + exentas

            total_gral_total += total_factura
            total_gral_base10 += base10
            total_gral_base5 += base5
            total_gral_iva10 += iva10
            total_gral_iva5 += iva5
            total_gral_exentas += exentas

            breakAndWrite(cont)
            if i.state != "cancel":
                rightAndWrite(i.invoice_date.strftime("%d/%m/%Y"))
            else:
                rightAndWrite("")
            if i.state != "cancel":
                rightAndWrite(i.partner_id.name)
            else:
                rightAndWrite("Anulado")
            if i.state != "cancel":
                rightAndWrite(i.partner_id.vat)
            else:
                rightAndWrite("")

            if i.state != "cancel":
                if i.invoice_date < i.invoice_date_due:
                    rightAndWrite("Credito")
                else:
                    rightAndWrite("Contado")
            else:
                rightAndWrite("")
            rightAndWrite(i.name)

            # valor del timbrado
            if i.state != "cancel":
                rightAndWrite(i.timbrado if i.timbrado else "")
            else:
                rightAndWrite("")

            if i.state != "cancel":
                rightAndWrite(base10, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(iva10, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(base5, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(iva5, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(exentas, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(total_factura, numerico)
            else:
                rightAndWrite(0)

        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        rightAndWrite(total_gral_base10, numerico_total)
        rightAndWrite(total_gral_iva10, numerico_total)
        rightAndWrite(total_gral_base5, numerico_total)
        rightAndWrite(total_gral_iva5, numerico_total)
        rightAndWrite(total_gral_exentas, numerico_total)
        rightAndWrite(total_gral_total, numerico_total)

        notas = self.env["account.move"].search(
            [
                ("move_type", "=", "in_refund"),
                ("state", "in", ["posted"]),
                ("invoice_date", ">=", datas.fecha_inicio),
                ("invoice_date", "<=", datas.fecha_fin),
            ]
        )

        breakAndWrite("Notas de crédito recibidas", bold)
        breakAndWrite("Nro", bold)
        rightAndWrite("Fecha", bold)
        rightAndWrite("Proveedor", bold)
        rightAndWrite("RUC o CI del Proveedor", wrapped_text_bold)
        rightAndWrite("Tipo doc.", bold)
        rightAndWrite("Nro. doc.", bold)
        rightAndWrite("Timbrado", bold)  # Se agrega el timbrado
        rightAndWrite("Importe sin IVA 10%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 10%", wrapped_text_bold)
        rightAndWrite("Importe sin IVA 5%", wrapped_text_bold)
        rightAndWrite("Debito fiscal 5%", wrapped_text_bold)
        rightAndWrite("Importes exentos", wrapped_text_bold)
        rightAndWrite("Importe total con IVA incluido", wrapped_text_bold)

        cont = 0
        total_gral_total = 0
        total_gral_base10 = 0
        total_gral_base5 = 0
        total_gral_iva10 = 0
        total_gral_iva5 = 0
        total_gral_exentas = 0
        for i in notas.sorted(key=lambda x: x.invoice_date):
            cont += 1
            if i.state != "cancel":
                total_factura = i.amount_total
            else:
                total_factura = 0

            impuestos = self.get_impuestos(i)
            base10 = impuestos["base10"]
            iva10 = impuestos["iva10"]
            base5 = impuestos["base5"]
            iva5 = impuestos["iva5"]
            exentas = impuestos["exentas"]

            if i.currency_id != self.env.company.currency_id:
                balance = 1
                amount_currency = 1
                balance = sum(abs(line.balance) for line in i.line_ids.filtered(lambda x: x.currency_id == i.currency_id))
                amount_currency = sum(abs(line.amount_currency) for line in i.line_ids.filtered(lambda x: x.currency_id == i.currency_id))
                if balance > 0 and amount_currency > 0:
                    currency_rate = balance / amount_currency
                    currency_rate = i.currency_id.round(currency_rate)
                else:
                    currency_rate = 1

                base10 = base10 * currency_rate
                iva10 = iva10 * currency_rate
                base5 = base5 * currency_rate
                iva5 = iva5 * currency_rate
                exentas = exentas * currency_rate
                total_factura = base10 + iva10 + base5 + iva5 + exentas

            total_gral_total += total_factura
            total_gral_base10 += base10
            total_gral_base5 += base5
            total_gral_iva10 += iva10
            total_gral_iva5 += iva5
            total_gral_exentas += exentas

            breakAndWrite(cont)
            if i.state != "cancel":
                rightAndWrite(i.invoice_date.strftime("%d/%m/%Y"))
            else:
                rightAndWrite("")
            if i.state != "cancel":
                rightAndWrite(i.partner_id.name)
            else:
                rightAndWrite("Anulado")
            if i.state != "cancel":
                rightAndWrite(i.partner_id.vat)
            else:
                rightAndWrite("")

            if i.state != "cancel":

                rightAndWrite("Nota de crédito")
            else:
                rightAndWrite("")
            rightAndWrite(i.ref)

            # valor del timbrado
            if i.state != "cancel":
                rightAndWrite(i.timbrado_id.name if i.timbrado_id else "")

            else:
                rightAndWrite("")

            if i.state != "cancel":
                rightAndWrite(base10, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(iva10, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(base5, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(iva5, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(exentas, numerico)
            else:
                rightAndWrite(0)
            if i.state != "cancel":
                rightAndWrite(total_factura, numerico)
            else:
                rightAndWrite(0)

        addSalto()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        rightAndWrite(total_gral_base10, numerico_total)
        rightAndWrite(total_gral_iva10, numerico_total)
        rightAndWrite(total_gral_base5, numerico_total)
        rightAndWrite(total_gral_iva5, numerico_total)
        rightAndWrite(total_gral_exentas, numerico_total)
        rightAndWrite(total_gral_total, numerico_total)
