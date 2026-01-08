from odoo import api, fields, models, exceptions
import xlrd, pytz, datetime


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    novedades_ids = fields.Many2many("hr.novedades", string="Novedades")
    novedad_deuda_anterior_id = fields.Many2one("hr.novedades", string="Novedad deuda anterior")

    def numero_a_letras(self, monto):
        # rrhh_novedades/models/hr_payslip.py
        return self.env['interfaces_tools.tools'].numero_a_letra(monto)

    def get_novedades(self):
        # rrhh_liquidacion/models/hr_payslip.py
        domain = [
            ('state', '=', 'done'),
            ('employee_id', '=', self.employee_id.id),
            ('contract_id', '=', self.contract_id.id),
            ('fecha', '>=', self.date_from),
            ('fecha', '<=', self.date_to),
        ]
        if self.structure_type_tag in ['normal']:
            domain.append(('tipo_id.tipo_novedad_adelanto_aguinaldo', '!=', True))
            return self.env['hr.novedades'].search(domain)
        elif self.structure_type_tag in ['aguinaldo']:
            domain.append(('tipo_id.tipo_novedad_adelanto_aguinaldo', '=', True))
            return self.env['hr.novedades'].search(domain)
        else:
            return self.env['hr.novedades']

    def compute_sheet(self):
        # rrhh_novedades/models/hr_payslip.py
        for this in self:
            novedades = this.get_novedades()
            this.write({'novedades_ids': [(6, 0, novedades.ids)]})
        res = super(HRPayslip, self).compute_sheet()
        return res

    def action_payslip_done(self):
        # rrhh_novedades/models/hr_payslip.py
        res = super(HRPayslip, self).action_payslip_done()
        for this in self:
            this.novedades_ids.action_process(this)

        tipo_novedad_deuda_anterior = self.env['hr.novedades.tipo'].search([('name', 'ilike', 'deuda anterior')], limit=1)
        if tipo_novedad_deuda_anterior:
            for this in self:
                if this.net_wage < 0:
                    novedad = {
                        'employee_id': this.employee_id.id,
                        'fecha': this.date_to + datetime.timedelta(days=1),
                        'monto': abs(this.net_wage),
                        'tipo_id': tipo_novedad_deuda_anterior.id,
                        'comentarios': "Deuda anterior del empleado creada automaticamente"
                    }
                    novedad_id = self.env['hr.novedades'].create(novedad)
                    if novedad_id:
                        novedad_id.button_confirmar()
                    this.write({'novedad_deuda_anterior_id': novedad_id.id})

        return res

    @api.model
    def create(self, vals):
        # rrhh_novedades/models/hr_payslip.py
        result = super().create(vals)
        result.check_nominas_duplicadas()
        return result
    
    def write(self, vals):
        # rrhh_novedades/models/hr_payslip.py
        result = super().write(vals)
        self.check_nominas_duplicadas()
        return result
    
    def check_nominas_duplicadas(self):
        for this in self:
            nomina_duplicada = this.env["hr.payslip"].search(
                [
                    ("id", "!=", this.id),
                    ("employee_id", "=", this.employee_id.id),
                    ("date_from", "=", this.date_from),
                    ("date_to", "=", this.date_to),
                    ("contract_id", "=", this.contract_id.id),
                    ("struct_id", "=", this.struct_id.id),
                ]
            )
            if nomina_duplicada:
                raise exceptions.ValidationError(
                    "Ya existe una nómina para este empleado con éstos datos (Empleado: %s, Estructura: %s, Fecha desde: %s, Fecha hasta: %s)"
                    % (this.employee_id.name, this.struct_id.name, this.date_from, this.date_to)
                )

    def action_payslip_cancel(self):
        # rrhh_novedades/models/hr_payslip.py
        res = super(HRPayslip, self).action_payslip_cancel()
        for this in self:
            novedades = this.novedades_ids
            novedades |= this.novedades_ids.search([('state', '=', 'procesado'), ('payslip_id', '=', this.id)])
            for novedad in novedades:
                novedad.action_not_process()
            if this.novedad_deuda_anterior_id:
                this.novedad_deuda_anterior_id.button_cancelar()
        return res
