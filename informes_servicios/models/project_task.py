from odoo import api, fields, models

class Task(models.Model):
    _inherit = "project.task"

    descripcion_falla = fields.Text(string="Descripción de falla")
    descripcion_trabajo = fields.Text(string="Descripción del trabajo realizado")
    materiales_reemplazado = fields.Text(string="Materiales reemplazados")