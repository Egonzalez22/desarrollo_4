from odoo import models, fields, api, exceptions
import datetime


class HRPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def get_values_for_report_bancos_interfisa(self):
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

        payslips_all = self.slip_ids.filtered(
            lambda x: x.state in ['done', 'paid'] and x.employee_id.bank_id == self.env.ref('reportes_ministerio_trabajo_py.banco_interfisa'))
        if not payslips_all:
            return final_text

        payslip_dates = payslips_all.mapped('date_to')
        payslip_dates.append(datetime.date.today())

        for contract in payslips_all.mapped('contract_id'):
            line_final_text = []
            payslips_contract = payslips_all.filtered(lambda payslip: payslip.contract_id == contract)
            payslips_contract_amount = int(sum(payslips_contract.line_ids.filtered(lambda x: x.code in ['NET']).mapped('total')))
            if payslips_contract_amount:
                description = ' - '.join([payslip.name for payslip in payslips_contract])
                nombre_completo = (contract.employee_id.nombre + ' ' + contract.employee_id.apellido).upper() 
                line_final_text.append(filter_characters(contract.employee_id.identification_id))
                line_final_text.append(filter_characters(nombre_completo))
                line_final_text.append(filter_characters(str(payslips_contract_amount)))
                line_final_text.append(filter_characters(contract.employee_id.bank_account))
                final_text.append(line_final_text)

        return final_text
