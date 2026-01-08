# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions
import random, math

letters = 'abcdefghijklmnopqrstuvwxyz'
letters += letters.upper()
numbers = '1234567890'


class DEVBaseReportWizard(models.TransientModel):
    _name = 'dev.base.report.wizard'
    _description = 'Wizard para generar plantillas de reportes'

    company_ids = fields.Many2many('res.company', default=lambda self: self.env.companies)
    item_qty = fields.Integer('Cantidad de ítems', required=True, default=50)
    date_from = fields.Date('Desde', required=True, default=fields.Date.today().replace(month=1, day=1))
    date_to = fields.Date('Hasta', required=True, default=fields.Date.today().replace(month=12, day=31))
    report_type = fields.Selection([('compact', 'Compacto'), ('detailed', 'Detallado')], string='Tipo de reporte', default='compact', required=True)
    sections = fields.Boolean('Múltiples secciones', default=False)
    pages = fields.Boolean('Múltiples páginas', default=False)

    def basic_checks(self):
        if self.item_qty < 1:
            raise exceptions.ValidationError('La cantidad de ítems debe ser un número positivo')
        if self.date_from > self.date_to:
            date_aux = self.date_from
            self.date_from = self.date_to
            self.date_to = date_aux

    def print_report_pdf(self):
        self.basic_checks()
        if self.report_type == 'compact':
            return self.env.ref('dev_base_report.dev_base_report_compact_pdf').report_action(self)
        if self.report_type == 'detailed':
            return self.env.ref('dev_base_report.dev_base_report_detailed_pdf').report_action(self)

    def print_report_xlsx(self):
        self.basic_checks()
        return self.env.ref('dev_base_report.dev_base_report_xlsx').report_action(self)


def base_get_report_values(wizard):
    def generate_random_data(base_characters, max_lenght=10):
        random_data_lenght = random.randint(5, max_lenght)
        random_data = ''
        for i in range(1, random_data_lenght):
            random_data += random.choice(base_characters)
        return random_data

    available_cities = [generate_random_data(letters, 5) for city in range(1, math.ceil(wizard.item_qty / 10) + 1)]
    report_lines = [{
        'company_id': random.choice(wizard.company_ids),
        'name': generate_random_data(letters),
        'city': random.choice(available_cities),
        'identification_id': generate_random_data(numbers),
        'amount': int(generate_random_data(numbers, 10)),
    } for i in range(1, wizard.item_qty + 1)]

    extra_columns = 0
    if wizard.report_type == 'compact':
        extra_columns = 5
    if wizard.report_type == 'detailed':
        extra_columns = 10
    report_extra_columns = {}
    for extra_column in range(1, extra_columns + 1):
        report_extra_columns.update({
            'extra_column_' + str(extra_column): random.choice([int, str]),
        })
    for report_line in report_lines:
        for report_extra_column in report_extra_columns:
            report_extra_column_content = False
            if report_extra_columns[report_extra_column] == int:
                report_extra_column_content = int(generate_random_data(numbers, 8))
            if report_extra_columns[report_extra_column] == str:
                report_extra_column_content = generate_random_data(letters, 8)
            report_line.update({report_extra_column: report_extra_column_content})
    report_lines = sorted(report_lines, key=lambda x: x['name'])
    return {
        'wizard': wizard,
        'available_cities': available_cities,
        'report_extra_columns': report_extra_columns,
        'report_lines': report_lines,
    }


class DEVBaseReportPDFCompact(models.AbstractModel):
    _name = 'report.dev_base_report.dev_base_report_pdf_compact'
    _description = 'Dev Base Report PDF Compact'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['dev.base.report.wizard'].browse(docids)
        return base_get_report_values(wizard)


class DEVBaseReportPDFDetailed(models.AbstractModel):
    _name = 'report.dev_base_report.dev_base_report_pdf_detailed'
    _description = 'Dev Base Report PDF Detailed'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['dev.base.report.wizard'].browse(docids)
        return base_get_report_values(wizard)


class DEVBaseReportWizardXLSX(models.AbstractModel):
    _name = 'report.dev_base_report.dev_base_report_xlsx_t'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        global sheet
        global position_x
        global position_y
        format_bold = workbook.add_format({'bold': True})
        format_numeric = workbook.add_format({'num_format': True, 'align': 'right'})
        format_numeric.set_num_format('#,##0')
        format_numeric_total = workbook.add_format({'num_format': True, 'align': 'right', 'bold': True})
        format_numeric_total.set_num_format('#,##0')
        format_wrapped_text = workbook.add_format()
        format_wrapped_text.set_text_wrap()
        format_wrapped_text_bold = workbook.add_format({'bold': True})
        format_wrapped_text_bold.set_text_wrap()
        format_date = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        format_datetime = workbook.add_format({'num_format': 'dd/mm/yyyy hh:mm'})

        def addBreak(positions=1):
            global position_x
            global position_y
            position_x = 0
            position_y += positions

        def addRight(positions=1):
            global position_x
            position_x += positions

        def simpleWrite(to_write, format=None):
            global sheet
            if isinstance(to_write, int) or isinstance(to_write, float):
                to_write = int(to_write)
            sheet.write(position_y, position_x, to_write or ('' if type(to_write) != int else 0), format)

        def breakAndWrite(to_write, format=None):
            global sheet
            addBreak()
            simpleWrite(to_write, format)

        def rightAndWrite(to_write, format=None):
            global sheet
            addRight()
            simpleWrite(to_write, format)

        # sheet.set_column(0, 0, 30)
        # sheet.set_column(1, 50, 20)

        wizard, available_cities, report_extra_columns, report_lines = base_get_report_values(wizard).values()

        for company_id in wizard.company_ids:
            sheet = workbook.add_worksheet(company_id.name)
            position_x = 0
            position_y = 0

            simpleWrite(fields.Datetime.now(), format_datetime)
            rightAndWrite(company_id.name, format_bold)

            breakAndWrite('Desde', format_bold)
            rightAndWrite(wizard.date_from, format_date)
            rightAndWrite('Hasta', format_bold)
            rightAndWrite(wizard.date_to, format_date)

            breakAndWrite('Cantidad de Items', format_bold)
            rightAndWrite(wizard.item_qty)
            rightAndWrite('Tipo de reporte', format_bold)
            rightAndWrite({'compact': 'Compacto', 'detailed': 'Detallado'}.get(wizard.report_type))

            breakAndWrite('Secciones', format_bold)
            rightAndWrite({True: 'Si', False: 'No'}.get(wizard.sections), format_numeric)
            rightAndWrite('Páginas', format_bold)
            rightAndWrite({True: 'Si', False: 'No'}.get(wizard.pages), format_numeric)

            addBreak(2)

            simpleWrite('Nombre', format_bold)
            rightAndWrite('Ciudad', format_bold)
            rightAndWrite('Identificación', format_bold)
            rightAndWrite('Monto', format_bold)
            for report_extra_column in report_extra_columns:
                rightAndWrite(report_extra_column, format_bold)

            total_amount = 0
            report_extra_columns_totals = {}
            for report_extra_column in report_extra_columns:
                if report_extra_columns[report_extra_column] == int:
                    report_extra_columns_totals.update({report_extra_column: 0})

            for report_line in filter(lambda x: x['company_id'] == company_id, report_lines):
                breakAndWrite(report_line['name'])
                rightAndWrite(report_line['city'])
                rightAndWrite(report_line['identification_id'])
                total_amount += report_line['amount']
                rightAndWrite(report_line['amount'], format_numeric)
                for report_extra_column in report_extra_columns:
                    if report_extra_columns[report_extra_column] == int:
                        report_extra_columns_totals.update(
                            {report_extra_column: report_extra_columns_totals[report_extra_column] + report_line[report_extra_column]})
                        rightAndWrite(report_line[report_extra_column], format_numeric)
                    if report_extra_columns[report_extra_column] == str:
                        rightAndWrite(report_line[report_extra_column])

            addBreak()
            addRight(2)
            simpleWrite('Total', format_bold)
            rightAndWrite(total_amount, format_numeric_total)
            for report_extra_column in report_extra_columns:
                if report_extra_columns[report_extra_column] == int:
                    rightAndWrite(report_extra_columns_totals[report_extra_column], format_numeric_total)
                if report_extra_columns[report_extra_column] == str:
                    addRight()

            if wizard.sections:
                workbook_sheet_name = company_id.name + ' - cities'
                workbook_sheet_created = False
                for available_city in available_cities:
                    if wizard.pages:
                        workbook_sheet_created = False
                        workbook_sheet_name = company_id.name + ' - ' + available_city
                    if not workbook_sheet_created:
                        workbook_sheet_created = True
                        sheet = workbook.add_worksheet(workbook_sheet_name)
                        position_x = 0
                        position_y = 0
                    elif not wizard.pages:
                        addBreak(4)

                    report_lines_company_city = filter(lambda x: x['company_id'] == company_id and x['city'] == available_city, report_lines)
                    if report_lines_company_city:
                        simpleWrite(available_city)

                    addBreak(2)

                    simpleWrite('Nombre', format_bold)
                    rightAndWrite('Identificación', format_bold)
                    rightAndWrite('Monto', format_bold)
                    for report_extra_column in report_extra_columns:
                        rightAndWrite(report_extra_column, format_bold)

                    total_amount = 0
                    report_extra_columns_totals = {}
                    for report_extra_column in report_extra_columns:
                        if report_extra_columns[report_extra_column] == int:
                            report_extra_columns_totals.update({report_extra_column: 0})

                    for report_line in report_lines_company_city:
                        breakAndWrite(report_line['name'])
                        rightAndWrite(report_line['identification_id'])
                        total_amount += report_line['amount']
                        rightAndWrite(report_line['amount'], format_numeric)
                        for report_extra_column in report_extra_columns:
                            if report_extra_columns[report_extra_column] == int:
                                report_extra_columns_totals.update(
                                    {report_extra_column: report_extra_columns_totals[report_extra_column] + report_line[report_extra_column]})
                                rightAndWrite(report_line[report_extra_column], format_numeric)
                            if report_extra_columns[report_extra_column] == str:
                                rightAndWrite(report_line[report_extra_column])

                    addBreak()
                    addRight()
                    simpleWrite('Total', format_bold)
                    rightAndWrite(total_amount, format_numeric_total)
                    for report_extra_column in report_extra_columns:
                        if report_extra_columns[report_extra_column] == int:
                            rightAndWrite(report_extra_columns_totals[report_extra_column], format_numeric_total)
                        if report_extra_columns[report_extra_column] == str:
                            addRight()
