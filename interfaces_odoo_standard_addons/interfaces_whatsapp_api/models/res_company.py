from odoo import _, api, fields, models,exceptions



class ResCompany(models.Model):
    _inherit = 'res.company'


    wha_business_id=fields.Char(string="Business ID",copy=False,default="151043592278721")
    wha_user_access_token=fields.Char(string="Access token",copy=False,default="EAAKmtegVkZCEBO5ZACQdIXmGkBtVTdJghd5oruh774EKaCdIvYXZBZAPOZAyCBwx5MG2eIQ2T0YV3rQnT5nNobSn4xP3oH9derfcZCZAP4tZALBeFxEUgZB1IC02IWnESwTxAtL3pYV6tT7BZBvrZAdxEdyPlSdXMZAI4HrTLDHt5ryEoqmrsvXp01pCNZA6iKDtUBq7GaZCcTnGdosvKSu5Y9osQZD")
    wha_waba_id=fields.Char(string="WABA ID",copy=False,default="")
    wha_version=fields.Char(string="Version",copy=False,default="v17.0")
    wha_phone_number_id=fields.Char(string="ID Nro. de teléfono",copy=False,default="107945308717423")
