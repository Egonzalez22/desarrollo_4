# -*- coding: utf-8 -*-
# from odoo import http


# class FePyPos(http.Controller):
#     @http.route('/fe_py_pos/fe_py_pos', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fe_py_pos/fe_py_pos/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('fe_py_pos.listing', {
#             'root': '/fe_py_pos/fe_py_pos',
#             'objects': http.request.env['fe_py_pos.fe_py_pos'].search([]),
#         })

#     @http.route('/fe_py_pos/fe_py_pos/objects/<model("fe_py_pos.fe_py_pos"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fe_py_pos.object', {
#             'object': obj
#         })
