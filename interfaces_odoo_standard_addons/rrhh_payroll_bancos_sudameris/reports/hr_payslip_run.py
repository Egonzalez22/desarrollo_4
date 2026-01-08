from odoo import models, fields, api, exceptions
import datetime


class HRPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    referencia_generada = fields.Char(string='Referencia generada en TXT')
    importe_generado = fields.Integer(string='Importe generado en TXT')
    cant_documentos_generados = fields.Char(string='Cantidad de documentos generados en TXT')

    def get_values_for_report_bancos_sudameris(self):
        def get_formatted_string_left(text, lenght, fill_character=' '):
            text = text or ' '
            return text

        def get_formatted_string_right(text, lenght, fill_character='0'):
            text = text or '0'
            return text

        final_text = ''

        payslips_all = self.slip_ids.filtered(
            lambda x: x.state in ['done', 'paid'] and x.employee_id.bank_id == self.env.ref('reportes_ministerio_trabajo_py.banco_sudameris')
        )
        if not payslips_all:
            return final_text

        c = 0
        fecha_servicio = max(payslips_all.mapped('date_to'))
        referencia = str(fecha_servicio.year)
        referencia += str(fecha_servicio.month).rjust(2, '0')
        referencia += str(fecha_servicio.day)[0]
        referencia += str(datetime.datetime.now().hour)
        referencia += str(datetime.datetime.now().minute)
        referencia += str(datetime.datetime.now().second)
        referencia += '1'
        referencia += '0'
        referencia += self.env.user.company_id.banco_sudameris_cod_contrato
        referencia = referencia[:18]
        fecha_servicio = datetime.date.strftime(fecha_servicio, '%d/%m/%y')
        Modalidad = str(self.env.user.company_id.sudameris_modalidad_pago)
        Sucursal = self.env.user.company_id.sudameris_num_sucursal
        monto_ = 0
        for contract in payslips_all.mapped('contract_id'):
            payslips_contract = payslips_all.filtered(lambda payslip: payslip.contract_id == contract)
            total_linea = int(sum(payslips_contract.line_ids.filtered(lambda x: x.code in ['NET']).mapped('total')))
            if contract.employee_id.modalidad_pago_sudamedis:
                Modalidad = str(contract.employee_id.modalidad_pago_sudamedis)

            if total_linea:
                date_end_ = contract.date_end
                c += 1
                final_text += '\n'
                final_text += 'D;'
                final_text += get_formatted_string_left('PAGO DE SALARIO VIA BANCO', 30)
                final_text += ';'
                final_text += get_formatted_string_left(
                    (' '.join(contract.employee_id.apellido.split(' ')[:1]) if len(contract.employee_id.apellido.split(' ')) > 0 else ''),
                    15)  # Primer Apellido
                final_text += ';'
                final_text += get_formatted_string_left(
                    (' '.join(contract.employee_id.apellido.split(' ')[1:]) if len(contract.employee_id.apellido.split(' ')) > 1 else ''),
                    15)  # Segundo Apellido
                final_text += ';'
                final_text += get_formatted_string_left(
                    (' '.join(contract.employee_id.nombre.split(' ')[:1]) if len(contract.employee_id.nombre.split(' ')) > 0 else ''), 15)  # Primer Apellido
                final_text += ';'
                final_text += get_formatted_string_left(
                    (' '.join(contract.employee_id.nombre.split(' ')[1:]) if len(contract.employee_id.nombre.split(' ')) > 1 else ''), 15)  # Segundo Apellido
                final_text += ';'
                final_text += get_formatted_string_right('586', 3)  # País
                final_text += ';'
                final_text += get_formatted_string_right('1', 2)  # Tipo de Documento
                final_text += ';'
                final_text += get_formatted_string_left(contract.employee_id.identification_id, 15)  # Número de Documento
                final_text += ';'
                final_text += get_formatted_string_right('6900', 4)  # Moneda
                final_text += ';'
                final_text += get_formatted_string_right((str(total_linea) + '.00'), 18)  # Importe
                final_text += ';'
                final_text += get_formatted_string_left(datetime.date.strftime(max(payslips_contract.mapped('date_to')), '%d/%m/%y'), 8)  # Fecha de Pago
                final_text += ';'
                final_text += (Modalidad)  # Modalidad de Pago
                final_text += ';'
                final_text += get_formatted_string_right(contract.employee_id.bank_account, 9)  # Número de Cuenta
                final_text += ';'
                final_text += str(Sucursal)  # Sucursal Empleado
                final_text += ';'
                final_text += get_formatted_string_right('6900', 4)  # Moneda Empleado
                final_text += ';'
                final_text += get_formatted_string_right('', 9)  # Operación Empleado
                final_text += ';'
                final_text += get_formatted_string_right('', 3)  # Tipo de Operación Empleado
                final_text += ';'
                final_text += get_formatted_string_right('', 3)  # Suboperación Empleado
                final_text += ';'
                final_text += get_formatted_string_left(referencia, 18)  # REFERENCIA
                final_text += ';'
                if date_end_:  # Tipo de Contrato
                    final_text += get_formatted_string_right('2', 3)
                else:
                    final_text += get_formatted_string_right('1', 3)
                final_text += ';'
                final_text += get_formatted_string_right((str(total_linea) + '.00'), 18)  # Sueldo Bruto
                final_text += ';'
                if date_end_:  # Fecha Fin de Contrato
                    final_text += get_formatted_string_left(datetime.date.strftime(contract.date_end, '%d/%m/%y'), 8)
                else:
                    final_text += ('//')
                final_text += ';'
                final_text += get_formatted_string_left(datetime.date.strftime(contract.date_start, '%d/%m/%y'), 8)  # Fecha de Ing. a la emp.
                montox_ = int(sum(payslips_contract.line_ids.filtered(lambda x: x.code in ['NET']).mapped('total')))
                print(f"monto_: {montox_}")
                monto_ += montox_
                final_text = final_text.replace(' ', '')

        first_line = 'H'
        first_line += ';'
        first_line += get_formatted_string_right(self.env.user.company_id.banco_sudameris_cod_contrato, 9)  # Código de Contrato
        first_line += ';'
        first_line += get_formatted_string_left(self.env.user.company_id.banco_sudameris_email_asociado, 50)  # E-mail asociado al Servicio
        first_line += ';'
        first_line += get_formatted_string_right('6900', 4)
        first_line += ';'
        if monto_:  # Importe
            first_line += get_formatted_string_left((str(int(monto_)) + '.00'), 18)
        else:
            first_line += ('//')
        first_line += ';'
        first_line += get_formatted_string_right(str(c), 5)  # Cantidad de Documentos
        first_line += ';'
        first_line += get_formatted_string_left(fecha_servicio, 8)  # Fecha de Pago
        first_line += ';'
        first_line += get_formatted_string_left(referencia, 18)  # REFERENCIA
        first_line += ';'
        first_line += get_formatted_string_right('1', 3)  # Tipo de Cobro
        first_line += ';'
        first_line += get_formatted_string_right('1', 1)  # Debito Crédito
        first_line += ';'
        first_line += get_formatted_string_right(self.env.user.company_id.banco_sudameris_nro_cuenta, 9)  # Cuenta Débito
        first_line += ';'
        first_line += str(Sucursal)  # Sucursal Débito
        first_line += ';'
        first_line += get_formatted_string_right('20', 3)  # Módulo Débito
        first_line += ';'
        first_line += get_formatted_string_right('6900', 4)  # Moneda Débito
        first_line += ';'
        first_line += get_formatted_string_right('0', 9)  # Operación Débito
        first_line += ';'
        first_line += get_formatted_string_right('0', 3)  # Sub Operación Débito
        first_line += ';'
        first_line += get_formatted_string_right('0', 3)  # Tipo Operación Débito
        first_line = first_line.replace(' ', '')
        final_text = first_line + final_text

        self.referencia_generada = referencia
        self.importe_generado = monto_
        self.cant_documentos_generados = str(c)

        return final_text
