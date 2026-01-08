# -*- coding: utf-8 -*-
# from odoo import http


# class TxtInterfisa(http.Controller):
#     @http.route('/txt_interfisa/txt_interfisa', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/txt_interfisa/txt_interfisa/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('txt_interfisa.listing', {
#             'root': '/txt_interfisa/txt_interfisa',
#             'objects': http.request.env['txt_interfisa.txt_interfisa'].search([]),
#         })

#     @http.route('/txt_interfisa/txt_interfisa/objects/<model("txt_interfisa.txt_interfisa"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('txt_interfisa.object', {
#             'object': obj
#         })
