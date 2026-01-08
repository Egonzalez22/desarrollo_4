import logging
import traceback

import requests
import xmltodict
from odoo import _, api, exceptions, models

_logger = logging.getLogger(__name__)
TIMEOUT = 25


class FE(models.TransientModel):
    _name = 'fe.wsdl'
    _description = 'FE WSDL Services'

    @api.model
    def consultaRuc(self, soap_structure, logger):
        try:
            wsdl = self.obtener_url('fe_ws_consulta_ruc')
            session = self.obtener_session(wsdl)
            rsp = self.send_request(session, soap_structure, wsdl, logger, fake=False)

            return rsp

        except Exception as ex:
            self.log_errors(ex, "consultaRuc", False)

    @api.model
    def consultaDe(self, soap_structure, logger):
        try:
            wsdl = self.obtener_url('fe_ws_consulta')
            session = self.obtener_session(wsdl)
            rsp = self.send_request(session, soap_structure, wsdl, logger, fake=False)

            return rsp

        except Exception as ex:
            self.log_errors(ex, "consultaDe", False)

    @api.model
    def consultaResultadoLote(self, soap_structure, logger):
        try:
            wsdl = self.obtener_url('fe_ws_consulta_lote')
            session = self.obtener_session(wsdl)
            rsp = self.send_request(session, soap_structure, wsdl, logger, fake=False)

            return rsp

        except Exception as ex:
            self.log_errors(ex, "consultaResultadoLote", False)

    @api.model
    def recepcionLoteDe(self, soap_structure, logger):
        try:
            wsdl = self.obtener_url('fe_ws_recibe_lote')
            session = self.obtener_session(wsdl)
            rsp = self.send_request(session, soap_structure, wsdl, logger, fake=False)
            return rsp

        except Exception as ex:
            self.log_errors(ex, "recepcionLoteDe", False)

    @api.model
    def recepcionDe(self, soap_structure, logger):
        try:
            wsdl = self.obtener_url('fe_ws_recibe')
            session = self.obtener_session(wsdl)
            rsp = self.send_request(session, soap_structure, wsdl, logger, fake=False)

            return rsp

        except Exception as ex:
            self.log_errors(ex, "recepcionDe", False)

    @api.model
    def recepcionEvento(self, soap_structure, logger):
        try:
            wsdl = self.obtener_url('fe_ws_evento')
            session = self.obtener_session(wsdl)
            rsp = self.send_request(session, soap_structure, wsdl, logger, fake=False)

            return rsp

        except Exception as ex:
            self.log_errors(ex, "recepcionEvento", False)

    @api.model
    def consultaDeOrganismosExternos(self, logger):
        return False

    def obtener_session(self, wsdl):
        """
        Retorna sesion de requests con certificado y llave privada
        """
        session = requests.Session()
        cert = self.env.company.cert
        key = self.env.company.private_key
        if not cert or not key:
            self.log_errors(None, "Certificado o llave privada no configurados", True)

        session.cert = (cert, key)
        return session

    def obtener_url(self, param):
        """
        Obtiene la url del ambiente de producción o de prueba según el parámetro
        Args:
            param (str): Nombre base del parámetro
        Returns:
            str: Url del ambiente
        """
        ambiente = self.env.company.fe_ambiente
        if ambiente:
            wsdl = self.env['ir.config_parameter'].sudo().get_param(f"{param}_{ambiente}")
            return wsdl
        else:
            self.log_errors(None, "No se pudo obtener la URL", True)

    def send_request(self, session, payload, wsdl, logger, fake=False):
        try:
            headers = {'User-Agent': "Interfaces", 'Content-Type': 'application/xml; charset=utf-8'}
            if fake:
                logging.debug(
                    u"""FAKE!!: Sending request to url {} 
                        with headers {}
                        paypoad {}""".format(
                        wsdl, headers, payload.strip()
                    )
                )
                return True

            res = session.post(wsdl, data=payload, headers=headers, timeout=TIMEOUT)

            if logger:
                logger.sudo().write(
                    {
                        "request": payload,
                        "response": res.text,
                        "status_code": res.status_code,
                    }
                )

            # Si el status_code no es 200, no tenemos forma de parsear y se debe guardar completo
            if res.status_code != 200:
                return res

            xdrsp = False
            try:
                # En test, SIFEN a veces retorna HTML cuando hay error
                xdrsp = xmltodict.parse(res.text)
            except Exception as ex:
                self.log_errors(ex, "send_request xmltodict status 200", False)

            return xdrsp
        except requests.exceptions.Timeout as ex:
            if logger:
                logger.sudo().write(
                    {
                        "request": payload,
                        "response": "Timeout",
                        "status_code": 400,
                    }
                )
            self.log_errors(ex, "send_request timeout", False)
            return False

        except Exception as ex:
            if logger:
                logger.sudo().write(
                    {
                        "request": payload,
                        "response": ex.args[0] if ex.args else "Exception en send_request",
                        "status_code": 400,
                    }
                )
            self.log_errors(ex, "send_request", False)
            return False

    def log_errors(self, ex, method, raise_exception=True):
        """
        Metodo para manejar los errores que vienen por un raise Exception
        Args:
            ex (exceptions): Contiene el error del raise Exception
            method (str): Nombre del metodo donde se produjo el error
            raise_exception (bool): Si es True realiza un raise con el error del raise Exception
        Raises:
            exceptions.ValidationError: Realiza un raise con el error del raise Exception
        """
        _logger.error(f"=============== {method} ==============")
        _logger.error(ex)
        err = traceback.format_exc()
        _logger.error(err)
        _logger.error(f"=============== FIN: {method} ==============")

        msg = ex.args[0] if ex and ex.args else f"Error en {method} en SIFEN"
        _logger.error(msg)

        if raise_exception:
            raise exceptions.ValidationError(_(msg))
