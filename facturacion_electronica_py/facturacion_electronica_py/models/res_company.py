from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from OpenSSL import crypto
import base64
import os
import re


class ResCompany(models.Model):
    _inherit = 'res.company'

    tipo_contribuyente = fields.Selection(
        string="Tipo de Contribuyente",
        selection=[('1', 'Persona Física'), ('2', 'Persona Jurídica')],
        default="2",
        copy=False,
        required=False,
    )
    tipo_regimen = fields.Selection(
        string="Tipo de Régimen",
        selection=[
            ('1', 'Régimen de Turismo'),
            ('2', 'Importador'),
            ('3', 'Exportador'),
            ('4', 'Maquila'),
            ('5', 'Ley N° 60/90'),
            ('6', 'Régimen del Pequeño Productor'),
            ('7', 'Régimen del Mediano Productor'),
            ('8', 'Régimen Contable'),
        ],
        default="8",
        copy=False,
        required=False,
    )
    cod_actividad_economica = fields.Char('Código de la Actividad Económica', copy=False, required=False)
    des_actividad_economica = fields.Char('Descripción de la Actividad Económica', copy=False, required=False)

    facturador_electronico = fields.Boolean(string="Es facturador electrónico", default=False)

    nombre_contribuyente = fields.Char(string="Razón Social del Contribuyente")
    nombre_fantasia = fields.Char(string="Nombre de fantasía del Contribuyente")
    sucursal = fields.Char(string="Nombre de la Sucursal")
    ruc_contribuyente = fields.Char(string="RUC del Contribuyente")

    digital_signature_file = fields.Binary(string='Archivo de firma electrónica', copy=False)
    digital_signature_password = fields.Char(string="Contraseña de firma electrónica", copy=False)
    cert = fields.Char(string="Certificado")
    private_key = fields.Char(string="Clave privada")
    public_key = fields.Char(string="Clave pública")
    fe_ambiente = fields.Selection(string="Ambiente", selection=[('test', 'Test'), ('prod', 'Producción')])

    fe_intento_reenvio = fields.Integer(string="Intentos de reenvío de Lote", default=5)
    fe_validar_schema = fields.Boolean(string="Validar Schema", default=False)
    fe_send_email = fields.Boolean(string="Enviar email", default=False)

    # Campo movido al módulo l10n_py_set
    # city_id = fields.Many2one('res.city', string="Ciudad", domain="[('state_id', '=', state_id)]")

    def generar_certificados(self):
        for i in self:
            if i.digital_signature_file and i.digital_signature_password:
                file = base64.b64decode(i.digital_signature_file)
                password = i.digital_signature_password.encode()
                p12 = crypto.load_pkcs12(file, password)
                home_directory = os.path.expanduser('~')

                # Agregamos una carpeta con el nombre de la compañia
                company_name = self.clean_name(i.name)
                home_directory = f'{home_directory}/{company_name}'
                if not os.path.exists(home_directory):
                    os.mkdir(home_directory)

                if home_directory and '\\' in home_directory:
                    home_directory = home_directory.replace('\\', '/')

                private_key = p12.get_privatekey()
                pk = crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key)
                pk_file = open(home_directory + '/' + 'private_key.pem', 'wb')
                pk_file.write(pk)
                pk_file.close()

                certificate = p12.get_certificate()
                cert = crypto.dump_certificate(crypto.FILETYPE_PEM, certificate)
                cert_file = open(home_directory + '/' + 'cert.pem', 'wb')
                # Eliminamos los saltos de lineas antes de guardar
                cert.replace(b'\n', b'')
                cert_file.write(cert)
                cert_file.close()

                public_key = certificate.get_pubkey()
                public_key = crypto.dump_publickey(crypto.FILETYPE_PEM, public_key)
                public_key_file = open(home_directory + '/' + 'public_key.pem', 'wb')
                public_key_file.write(cert)
                public_key_file.close()

                i.cert = home_directory + '/' + 'cert.pem'
                i.private_key = home_directory + '/' + 'private_key.pem'
                i.public_key = home_directory + '/' + 'public_key.pem'
                # Generamos la secuencia para utilizar en los documentos de SIFEN
                i.generar_secuencia_sifen()

    def clean_name(self, name):
        """
        Método para limpiar el nombre de la compañía de caracteres raros y espacios
        """
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
        clean_name = re.sub(r'\s+', '_', clean_name).strip()
        return clean_name.lower()

    def generar_secuencia_sifen(self):
        """
        Se genera una secuencia por cada compañia para utilizar en los documentos de SIFEN
        """
        company = self.env.company

        # Verificaos si ya existe una secuencia para FE
        sequence = self.env['ir.sequence'].sudo().search([('code', '=', 'id_mensaje'), ('company_id', '=', company.id)])
        if sequence:
            return

        # Generamos una secuencia para FE
        sequence = (
            self.env['ir.sequence']
            .sudo()
            .create(
                {
                    'name': f'Identificador de mensaje FE {company.name}',
                    'code': 'id_mensaje',
                    'implementation': 'standard',
                    'use_date_range': False,
                    'prefix': None,
                    'padding': 9,
                    'number_increment': 1,
                    'number_next_actual': 1,
                    'company_id': company.id,
                }
            )
        )
