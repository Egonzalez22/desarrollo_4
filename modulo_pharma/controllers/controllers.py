import hashlib

from odoo import http
from odoo.http import request


class CertificateController(http.Controller):

    @http.route('/certificado_check', type='http', auth='public', website=True)
    def download_certificate(self, certificado_id, token):
        if token == self.genera_token(str(certificado_id)):
            record = request.env['certificados.laboratorio'].sudo().browse(int(certificado_id))
            if not record:
                return http.request.render('modulo_pharma.token_invalido')

            pdf_content = record._generate_certificate_pdf()
            pdf_name = f"{record.display_name}.pdf"
            return request.make_response(pdf_content, headers=[
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename={pdf_name}')
            ])
        else:
            return http.request.render('modulo_pharma.token_invalido')

    def genera_token(self, certificado_id):
        palabra = certificado_id + "amakakeruriunohirameki"
        return hashlib.sha256(bytes(palabra, 'utf-8')).hexdigest()
