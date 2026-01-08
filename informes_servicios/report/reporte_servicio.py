from odoo import api, models

class TaskCustomReport(models.AbstractModel):
    _name = 'report.informes_servicios.reporte_servicios'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['project.task'].browse(docids).sudo()
        tags = self.env['helpdesk.tag'].search([])

        worksheet_map = {}
        if docs.worksheet_template_id:
            x_model = docs.worksheet_template_id.model_id.model
            worksheet = self.env[x_model].search([('x_project_task_id', '=', docs.id)], limit=1, order="create_date DESC")
            worksheet_map[docs.id] = worksheet

        return {
            'doc_ids': docids,
            'doc_model': 'project.task',
            'tags': tags,
            'doc': docs,
            'worksheet_map': worksheet_map,
        }
