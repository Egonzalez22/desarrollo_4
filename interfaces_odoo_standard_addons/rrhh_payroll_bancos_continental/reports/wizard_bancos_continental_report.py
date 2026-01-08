from odoo import api, fields, models
import datetime


class WizardBancoContinental(models.TransientModel):
    _name = 'wizard_bancos_continental'
    _description = 'Wizard Banco CONTINENTAL'

    name = fields.Char(string='Nombre', required=True)
    date_from = fields.Date(string='Fecha Desde', required=True)
    date_to = fields.Date(string='Fecha Hasta', required=True)
    tipo_novedades_ids = fields.Many2many('hr.novedades.tipo', string='Tipos de Novedades', required=True)

    def print_wizard_bancos_continental_report(self):
        return self.env.ref('rrhh_payroll_bancos_continental.wizard_bancos_continental_report').report_action(self)

    def get_values_for_report_bancos_continental(self):
        def filter_characters(text):
            if not text: return ''
            allowed_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ .,1234567890'
            for character_pair in [('á', 'a'), ('é', 'e'), ('í', 'i'), ('ó', 'o'), ('ú', 'u'), ('ñ', 'n')]:
                text = text.replace(character_pair[0], character_pair[1])
                text = text.replace(character_pair[0].upper(), character_pair[1].upper())
            for character in text:
                if character not in allowed_characters:
                    text = text.replace(character, ' ')
            while '  ' in text:
                text = text.replace('  ', ' ')
            return text

        final_text = []

        novedades_all = self.env['hr.novedades'].search([
            ('state', 'in', ['done', 'procesado']),
            ('tipo_id', 'in', self.tipo_novedades_ids.ids),
            ('fecha', '>=', self.date_from),
            ('fecha', '<=', self.date_to),
        ]).filtered(lambda x: x.employee_id.bank_id == self.env.ref('reportes_ministerio_trabajo_py.banco_continental'))
        if not novedades_all:
            return final_text

        payslip_dates = novedades_all.mapped('fecha')
        payslip_dates.append(datetime.date.today())

        for contract in novedades_all.mapped('contract_id'):
            line_final_text = []
            novedades_contract = novedades_all.filtered(lambda payslip: payslip.contract_id == contract)
            novedades_contract_amount = int(sum(novedades_contract.mapped('monto')))
            if novedades_contract_amount:
                description = ' - '.join([payslip.name for payslip in novedades_contract])
                line_final_text.append(filter_characters(contract.employee_id.identification_id))
                line_final_text.append(filter_characters(contract.company_id.banco_continental_nro_cuenta))
                line_final_text.append(filter_characters(description))
                line_final_text.append(filter_characters(str(novedades_contract_amount)))
                line_final_text.append(filter_characters('NO'))
                line_final_text.append(filter_characters(''))
                line_final_text.append(filter_characters(datetime.date.strftime(max(payslip_dates), '%Y%m%d')))
                line_final_text.append(filter_characters(contract.employee_id.banco_continental_tipo_cuenta))
                final_text.append(line_final_text)

        return final_text
