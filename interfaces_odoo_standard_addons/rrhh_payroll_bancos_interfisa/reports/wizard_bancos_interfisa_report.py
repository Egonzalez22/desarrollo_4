from odoo import api, fields, models
import datetime


class WizardBancoInterfisa(models.TransientModel):
    _name = 'wizard_bancos_interfisa'
    _description = 'Wizard Banco Interfisa'

    name = fields.Char(string='Nombre', required=True)
    date_from = fields.Date(string='Fecha Desde', required=True)
    date_to = fields.Date(string='Fecha Hasta', required=True)
    tipo_novedades_ids = fields.Many2many('hr.novedades.tipo', string='Tipos de Novedades', required=True)

    def print_wizard_bancos_interfisa_report(self):
        return self.env.ref('rrhh_payroll_bancos_interfisa.wizard_bancos_interfisa_report').report_action(self)

    def get_values_for_report_bancos_interfisa(self):
        def get_formatted_string_left(text, lenght, fill_character=' '):
            text = text or ''
            return text[:lenght].ljust(lenght, fill_character)

        def get_formatted_string_right(text, lenght, fill_character='0'):
            text = text or ''
            return text[:lenght].rjust(lenght, fill_character)

        novedades_all = self.env['hr.novedades'].search([
            ('state', 'in', ['done', 'procesado']),
            ('tipo_id', 'in', self.tipo_novedades_ids.ids),
            ('fecha', '>=', self.date_from),
            ('fecha', '<=', self.date_to),
        ]).filtered(lambda x: x.employee_id.bank_id == self.env.ref('reportes_ministerio_trabajo_py.banco_interfisa'))

        final_text = ''

        if not novedades_all:
            return final_text

        c = 0

        for contract in novedades_all.mapped('contract_id'):
            novedades_contract = novedades_all.filtered(lambda novedad: novedad.contract_id == contract)
            total_linea = int(sum(novedades_contract.mapped('monto')))
            if total_linea:
                c += 1
                nombre_completo = (contract.employee_id.nombre + ' ' + contract.employee_id.apellido).upper() 
                final_text += get_formatted_string_left(contract.employee_id.identification_id, 15)
                final_text += get_formatted_string_left(nombre_completo, 80)
                final_text += get_formatted_string_right(str(total_linea), 18)
                final_text += get_formatted_string_left(str(contract.employee_id.bank_account), 18)
        return final_text
