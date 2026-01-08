from odoo import models, api, exceptions, fields, _

import uuid, base64, qrcode, hashlib
from _io import BytesIO
from datetime import datetime
from calendar import monthrange
import json

MESES = [('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'), ('5', 'Mayo'), ('6', 'Junio'),
         ('7', 'Julio'),
         ('8', 'Agosto'), ('9', 'Setiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')]
DIA_SEMANA = ['lun', 'mar', 'mie', 'jue', 'vie', 'sab', 'dom']


class InformeAsistenciasWizard(models.TransientModel):
    _name = 'informe_asistencias.informe_asistencias_wizard'

    anho = fields.Integer(string="Año", default=lambda self: fields.Datetime.now().year)
    mes = fields.Selection(string="Mes del año", selection=MESES,
                           default=lambda self: str(fields.Datetime.now().month))
    departamento_id = fields.Many2one('hr.department', string="Departamento")
    # company_id = fields.Many2one('res.company', string="Compañia")

    # def impreso_por(self):
    #     context = self._context
    #     current_uid = context.get('uid')
    #     user = self.env['res.users'].browse(current_uid)
    #     self.usuario = user.name

    def button_print_pdf(self):
        # print(f"self.departamento_id: {self.departamento_id.id}")
        # print(f"self.env.user.company_id: {self.env.user.company_id}")
        # print(f"self.ids: {self.ids}")
        docargs = {
            'ids': self.ids,
            'model': 'informe_asistencias.informe_asistencias_wizard',
            'data': {
                'mes': self.mes,
                'anho': self.anho,
                'departamento': self.departamento_id.id if self.departamento_id else 0,
                # 'company': self.company_id.id

            }
        }
        # nombre archivo de reporte xml, y id del <report>
        return self.env.ref('informe_asistencias.reporte_informe_asistencias').report_action(self,
                                                                                             data=docargs)

    def button_print_xlsx(self):
        docargs = {
            'ids': self.ids,
            'model': 'informe_asistencias.informe_asistencias_wizard',
            'data': {
                'mes': self.mes,
                'anho': self.anho,
                'departamento': self.departamento_id.id if self.departamento_id else 0
            }
        }
        return self.env.ref('informe_asistencias.reporte_xlsx_action').report_action(self, data=docargs)


class InformeAsistenciasReport(models.TransientModel):
    _name = 'report.informe_asistencias.informe_asistencias_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        anho = int(data['data']['anho'])
        mes = int(data['data']['mes'])
        departamento_id = int(data['data']['departamento'])
        # company_1 = (data['data']['company'])
        # print("company_1: ", company_1)
        # departamentos_sql_ids = []
        ultimo_dia_mes = monthrange(anho, mes)[1]
        primer_dia = monthrange(anho, mes)[0]
        company = self.env.user.company_id.id
        print("company: ", company)
        print("departamento_id: ", departamento_id)
        if departamento_id < 1:
            departamentos = self.env['hr.department'].search([('company_id.id', '=', (company))])
            print("departamentos: ", departamentos)
        else:
            departamentos = self.env['hr.department'].browse(departamento_id)
    



        contratos = self.env['hr.contract'].search([('employee_id','!=',False),('department_id', 'in', departamentos.ids)])
        contratos = contratos.sorted(key=lambda x: x.employee_id.name)
        print("contratos: ", contratos)

        asistencias = self.env['hr.attendance'].search([
            ('contract_id', 'in', contratos.ids),
            ('date', '>=', str(anho)+ '-' + str(mes) + '-' + '1'),
            ('date', '<=', str(anho) + '-' + str(mes) + '-' + str(ultimo_dia_mes)),
        ])
        # asistencias = self.env['hr.attendance'].search([
        #     ('contract_id', 'in', contratos.ids),
        #     ('date', '>=', '1-' + str(mes) + '-' + str(anho)),
        #     ('date', '<=', str(ultimo_dia_mes) + '-' + str(mes) + '-' + str(anho)),
        # ])
        print(asistencias)
        lineas = []

        dias_mes = []
        first_day = primer_dia

        for dia in range(1, ultimo_dia_mes + 1):
            if dia < 10:
                dias_mes.append(DIA_SEMANA[first_day] + '0' + str(dia))
            else:
                dias_mes.append(DIA_SEMANA[first_day] + str(dia))
            first_day += 1
            if first_day == 7:
                first_day = 0

        for cont in contratos:
            print("cont: ", cont)
            asis_cont = asistencias.filtered(lambda x: x.contract_id.id == cont.id)
            horarios = []
            for dia in range(1, ultimo_dia_mes + 1):

                asis = asis_cont.filtered(lambda x: str(int(x.date.strftime('%d'))) == str(dia)).sorted(
                    key=lambda s: s.id)
                if not asis:
                    fecha = datetime.strptime(str(anho) + '-' + str(mes) + '-' + str(dia), '%Y-%m-%d').date()
                    ausencias = self.env['hr.leave'].search(
                        [('contract_id', '=', cont.id), ('request_date_from', '<=', fecha),
                         ('request_date_to', '>=', fecha)])
                    if not ausencias:
                        horarios.append(['--:--', '--:--'])
                    else:
                        horarios.append([ausencias[0].holiday_status_id.code])
                else:
                    h_aux = []
                    for i in asis:
                        h_aux.append(self.convertToHours(i.entrada_marcada))
                        h_aux.append(self.convertToHours(i.salida_marcada))
                    horarios.append(h_aux)

            lineas.append(
                [[cont.employee_id.id], [cont.employee_id.name], [cont.department_id.id], horarios])
        print("lineas: ", lineas)
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'dias_mes': dias_mes,
            'mes': mes,
            'MESES': MESES,
            'ultimo_dia_mes': ultimo_dia_mes,
            'departamentos': departamentos,
            'lineas': lineas
        }

    def convertToHours(self, float_time):
        t_mili = float_time * 3600000
        t_str = str(datetime.fromtimestamp(t_mili / 1000).time()).split(':')
        return ":".join([t_str[0], t_str[1]])


class ReporteXLSX(models.AbstractModel):
    _name = 'report.informe_asistencias.reporte_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, datas):
        anho = int(data['data']['anho'])
        mes = int(data['data']['mes'])
        departamento_id = int(data['data']['departamento'])

        ultimo_dia_mes = monthrange(anho, mes)[1]
        primer_dia = monthrange(anho, mes)[0]
        company = self.env.user.company_id
        if departamento_id < 1:
            departamentos = self.env['hr.department'].search([('company_id.id', '=', company.id)])
        else:
            departamentos = self.env['hr.department'].browse(departamento_id)

        contratos = self.env['hr.contract'].search([('employee_id','!=',False),('department_id', 'in', departamentos.ids)])
        contratos = contratos.sorted(key=lambda x: x.employee_id.name)

        asistencias = self.env['hr.attendance'].search([
            ('contract_id', 'in', contratos.ids),
            ('date', '>=', '1-' + str(mes) + '-' + str(anho)),
            ('date', '<=', str(anho) + '-' + str(mes) + '-' + str(ultimo_dia_mes)),
        ])

        lineas = []

        dias_mes = []
        first_day = primer_dia

        for dia in range(1, ultimo_dia_mes + 1):
            if dia < 10:
                dias_mes.append(DIA_SEMANA[first_day] + '0' + str(dia))
            else:
                dias_mes.append(DIA_SEMANA[first_day] + str(dia))
            first_day += 1
            if first_day == 7:
                first_day = 0

        for cont in contratos:
            asis_cont = asistencias.filtered(lambda x: x.contract_id.id == cont.id)
            horarios = []
            for dia in range(1, ultimo_dia_mes + 1):

                asis = asis_cont.filtered(lambda x: str(int(x.date.strftime('%d'))) == str(dia)).sorted(
                    key=lambda s: s.id)
                if not asis:
                    fecha = datetime.strptime(str(dia) + '-' + str(mes) + '-' + str(anho), '%d-%m-%Y').date()
                    ausencias = self.env['hr.leave'].search(
                        [('contract_id', '=', cont.id), ('request_date_from', '<=', fecha),
                         ('request_date_to', '>=', fecha)])
                    if not ausencias:
                        horarios.append(['--:--', '--:--'])
                    else:
                        horarios.append([ausencias[0].holiday_status_id.code])
                else:
                    h_aux = []
                    for i in asis:
                        h_aux.append(self.convertToHours(i.entrada_marcada))
                        h_aux.append(self.convertToHours(i.salida_marcada))
                    horarios.append(h_aux)

            lineas.append(
                [[cont.employee_id.id], [cont.employee_id.name], [cont.department_id.id], horarios])

        global sheet
        global bold
        global num_format
        global position_x
        global position_y
        sheet = workbook.add_worksheet('Hoja 1')
        bold = workbook.add_format({'bold': True})
        numerico = workbook.add_format({'num_format': True, 'align': 'right'})
        numerico.set_num_format('#,##0')
        numerico_total = workbook.add_format(
            {'num_format': True, 'align': 'right', 'bold': True})
        numerico_total.set_num_format('#,##0')
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

        def addBot():
            global position_y
            position_y += 1

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

        addSalto()
        rightAndWrite(datetime.now().strftime('%d-%m-%Y'), bold)
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        addRight()
        rightAndWrite("ENTRADA Y SALIDA DE EMPLEADOS DEL MES DE " + MESES[mes - 1][1].upper(), bold)
        addSalto()
        breakAndWrite("Cod.")
        rightAndWrite("Nombre")
        for dia in dias_mes:
            rightAndWrite(dia)
        for depa in departamentos:
            addSalto()
            breakAndWrite("Departamento: ", bold)
            rightAndWrite(depa.name, bold)
            line_bottom = 0
            origin_position_y = 0
            for line in lineas:
                if str(depa.id) == str(line[2][0]):
                    if origin_position_y > 0:
                        position_y = origin_position_y
                        position_y += line_bottom
                    position_x = 0
                    breakAndWrite(line[0][0])
                    origin_position_y = position_y
                    rightAndWrite(line[1][0])
                    line_bottom = 0
                    for hora_dia in line[3]:
                        addRight()
                        position_y = origin_position_y
                        c = 0
                        for tiempo in hora_dia:
                            simpleWrite(tiempo)
                            addBot()
                            c += 1
                            if c > line_bottom:
                                line_bottom = c

    def convertToHours(self, float_time):
        t_mili = float_time * 3600000
        t_str = str(datetime.fromtimestamp(t_mili / 1000).time()).split(':')
        return ":".join([t_str[0], t_str[1]])
