# -*- coding: utf-8 -*-

from odoo import models, fields, api, release
import xlsxwriter
import base64


class ReporteComprasXLSX(models.AbstractModel):
    _inherit = "report.reporte_compraventa.reporte_compra_xlsx"

    def get_impuestos(self, invoice):
        """
        Retorna un diccionario con los valores de los impuestos de la factura.
        Solo se suman los montos si la factura no esta cancelada.
        En el caso de que la factura no tenga impuestos, se retorna 0 para todos los valores.
        """
        result = super(ReporteComprasXLSX, self).get_impuestos(invoice)
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
            for l in lineas:
                for line_tax in l.tax_ids.compute_all(l.price_total, currency=invoice.currency_id)["taxes"]:

                    # Suma de exentas
                    if l.tax_ids.browse(line_tax.get("id")).tax_group_id == l.env.ref("l10n_py.tax_group_0"):
                        exentas += l.price_total / 100 * l.tax_ids.browse(line_tax.get("id")).porcentaje_sobre_base

                    # Suma de IVA 5
                    if l.tax_ids.browse(line_tax.get("id")).tax_group_id == l.env.ref("l10n_py.tax_group_5"):
                        base5 += l.price_total / 100 * l.tax_ids.browse(line_tax.get("id")).porcentaje_sobre_base
                        iva5 += line_tax.get("amount")

                    # Suma de IVA 10
                    if l.tax_ids.browse(line_tax.get("id")).tax_group_id == l.env.ref("l10n_py.tax_group_10"):
                        base10 += l.price_total / 100 * l.tax_ids.browse(line_tax.get("id")).porcentaje_sobre_base
                        iva10 += line_tax.get("amount")
        base10 -= iva10
        base5 -= iva5

        result = {"base10": base10, "iva10": iva10, "base5": base5, "iva5": iva5, "exentas": exentas}

        return result


class ReporteVentasXLSX(models.AbstractModel):
    _inherit = "report.reporte_compraventa.reporte_venta_xlsx"

    def get_impuestos(self, invoice):
        """
        Retorna un diccionario con los valores de los impuestos de la factura.
        Solo se suman los montos si la factura no esta cancelada.
        En el caso de que la factura no tenga impuestos, se retorna 0 para todos los valores.
        """
        result = super(ReporteVentasXLSX, self).get_impuestos(invoice)
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
            for l in lineas:
                for line_tax in l.tax_ids.compute_all(l.price_total, currency=invoice.currency_id)["taxes"]:

                    # Suma de exentas
                    if l.tax_ids.browse(line_tax.get("id")).tax_group_id == l.env.ref("l10n_py.tax_group_0"):
                        exentas += l.price_total / 100 * l.tax_ids.browse(line_tax.get("id")).porcentaje_sobre_base

                    # Suma de IVA 5
                    if l.tax_ids.browse(line_tax.get("id")).tax_group_id == l.env.ref("l10n_py.tax_group_5"):
                        base5 += l.price_total / 100 * l.tax_ids.browse(line_tax.get("id")).porcentaje_sobre_base
                        iva5 += line_tax.get("amount")

                    # Suma de IVA 10
                    if l.tax_ids.browse(line_tax.get("id")).tax_group_id == l.env.ref("l10n_py.tax_group_10"):
                        base10 += l.price_total / 100 * l.tax_ids.browse(line_tax.get("id")).porcentaje_sobre_base
                        iva10 += line_tax.get("amount")

        base10 -= iva10
        base5 -= iva5

        result = {"base10": base10, "iva10": iva10, "base5": base5, "iva5": iva5, "exentas": exentas}

        return result
