from odoo import api, fields, models
from . import amount_to_text_spanish
import socket

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    print_count = fields.Integer(string='Contador de impresiones', copy=False)
    fecha_inicio_vencimiento = fields.Boolean(string='Fecha y Vencimiento igual', compute="_tipo_cheque")
    es_portador = fields.Boolean(string='Es cheque al portador', default=False, copy=False)
    nro_cuenta_id = fields.Many2one('res.partner.bank', string='Nro. de cuenta')


    @api.onchange('bank_id')
    def _cuenta_banco(self):
        if self.bank_id:
            num_cuenta = []
            consulta = self.env['res.partner.bank'].search([('bank_id','=', self.bank_id.id)])
            for dato in consulta:
                if dato.id not in num_cuenta:
                    num_cuenta.append(dato.id)
            self.nro_cuenta_id = False # Reinicia el valor del campo lote para que el usuario no conserve selecciones anteriores que ya no son válidas
            return {'domain': {'nro_cuenta_id': [('id', 'in', num_cuenta)]}}
            

    @api.onchange('nro_cuenta_id')
    def _cuenta_banco_numero(self):
        if self.nro_cuenta_id.acc_number:
            self.nro_cuenta = self.nro_cuenta_id.acc_number


    @api.model
    def formatear_monto(self, monto, currency=False, lang=False):
        if not lang:
            lang_str = self._context.get('lang')
        else:
            lang_str = lang
        if not currency:
            currency_id = self.env.user.company_id.currency_id
        else:
            currency_id = currency
        lang_id = self.env['res.lang'].search([('code', '=', lang_str)])

        if lang_id and currency_id:
            fmt = "%.{0}f".format(currency_id.decimal_places)
            return lang_id.format(fmt, monto, grouping=True)
        else:
            return '{:.6f}'.format(monto)

    def amount_to_text(self, amount, currency):
        convert_amount_in_words = amount_to_text_spanish.to_word(amount)
        return convert_amount_in_words

    def _tipo_cheque(self):
        for i in self:
            if i.fecha_cheque == i.fecha_vencimiento_cheque:
                self.update({'fecha_inicio_vencimiento': True})
            else:
                self.update({'fecha_inicio_vencimiento': False})

    def print_cheque_vista(self):
        self.print_count += 1
        return self.env.ref('interfaces_impresion_cheque.cheque_vista_action').report_action(self)

    def print_cheque_diferido(self):
        self.print_count += 1
        return self.env.ref('interfaces_impresion_cheque.cheque_diferido_action').report_action(self)

    def permitir_reimpresion(self):
        self.print_count = 0

    def print_cheque_vista_itau_sudameris(self):
        self.print_count += 1
        return self.env.ref('interfaces_impresion_cheque.cheque_itau_sudameris_vista_action').report_action(self)
    

    def print_cheque_vista_vision(self):
        self.print_count += 1
        return self.env.ref('interfaces_impresion_cheque.cheque_vision_vista_action').report_action(self)

    def print_cheque_diferido_v2(self):
        self.print_count += 1
        return self.env.ref('interfaces_impresion_cheque.cheque_diferido_v2_action').report_action(self)

    def print_cheque_vista_dolares(self):
        self.print_count += 1
        return self.env.ref('interfaces_impresion_cheque.cheque_dolares_vista_action').report_action(self)
    
    @api.model
    def truncate_nombre_proveedor(self, name, max_length=10):
        if len(str(name)) > max_length:
            return name[:max_length] + "..."
        else:
            return name
        
    

    def limitar_campo_espacios_derecha(self, limite, string=''):
        if not string:
            string = ''
        if len(string) < limite:
            return string.ljust(limite)
        else:
            return string[:limite]

    def limitar_campo_espacios_izquierda(self, limite, string=''):
        if not string:
            string = ''
        if len(string) < limite:
            faltante = limite - len(string)
            return (''.ljust(faltante) + string)
        else:
            return string[:limite]

    def cortar_cadena(self, texto, longitud_maxima):
        if len(texto) > longitud_maxima:
            indice_espacio = texto.rfind(' ', 0, longitud_maxima)
            if indice_espacio != -1:
                parte_cortada = texto[indice_espacio+1:]
                texto = texto[:indice_espacio]
            else:
                parte_cortada = texto[longitud_maxima:]
                texto = texto[:longitud_maxima]
            return texto, parte_cortada
        else:
            return texto, None
        
    def invoice_print_escpos(self):
        for this in self:



            if this.currency_id.name == 'PYG':
                texto_cortado, parte_cortada  = self.cortar_cadena(this.amount_to_text(this.amount, this.currency_id), 77)
            else:
                # texto_cortado, parte_cortada  = self.cortar_cadena(this.amount_to_text(this.amount, this.currency_id), 61)
                texto_cortado, parte_cortada  = self.cortar_cadena(this.check_amount_in_words, 61)

            # cheque =  ""
            # cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea1"+  "\n"
            # cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea2"+  "\n"
            # cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea3"+  "\n"
            # cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea4"+  "\n"
            # cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea5"+  "\n"
            # if this.currency_id.name == 'PYG':
            #     if texto_cortado and parte_cortada:
            #         cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea6"+  "\n"
            #         cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea7"+  "\n"
            #     else:
            #         cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea6"+  "\n"
            # cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea8"+  "\n"
            # cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea9"+  "\n"
            # cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea10"+  "\n"
            # cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea11"+  "\n"
            # cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea12"+  "\n"
            # cheque += self.limitar_campo_espacios_derecha(5, " ") + "Linea13"+  "\n"
            
            cheque =  ""
            if this.currency_id.name == 'PYG':
                cheque += self.limitar_campo_espacios_derecha(86, " ")\
                    + self.limitar_campo_espacios_derecha(27, str(this.formatear_monto(this.amount,currency=this.currency_id))+'.--')+ "\n"
            else:
                cheque += self.limitar_campo_espacios_derecha(89, " ")\
                    + self.limitar_campo_espacios_derecha(30, str(this.formatear_monto(this.amount,currency=this.currency_id))+'.--')+ "\n"
                
            cheque += self.limitar_campo_espacios_derecha(5, " ") + "\n"
            cheque += self.limitar_campo_espacios_derecha(5, " " )+ self.limitar_campo_espacios_derecha(10, str(this.fecha_cheque.strftime('%d-%m-%Y'))) + self.limitar_campo_espacios_derecha(52, " " )+ self.limitar_campo_espacios_derecha(5, str(this.fecha_cheque.day)) + self.limitar_campo_espacios_derecha(8, str(this.fecha_cheque.month)) + self.limitar_campo_espacios_derecha(6, str(this.fecha_cheque.year)[2:] )+ "\n"   
            cheque += self.limitar_campo_espacios_derecha(5, " ") + self.limitar_campo_espacios_derecha(9, str(this.truncate_nombre_proveedor(this.observaciones)))  +  "\n"
            if this.partner_id:
                cheque += self.limitar_campo_espacios_derecha(5, " ") + self.limitar_campo_espacios_derecha(9, str(this.truncate_nombre_proveedor(this.observaciones))) + self.limitar_campo_espacios_derecha(26, " " )+ self.limitar_campo_espacios_derecha(40, str(this.partner_id.name)) +  "\n"
            else:
                cheque += self.limitar_campo_espacios_derecha(5, " ") + self.limitar_campo_espacios_derecha(9, str(this.truncate_nombre_proveedor(this.observaciones))) + self.limitar_campo_espacios_derecha(26, " " )+ self.limitar_campo_espacios_derecha(40, "Al portador") +  "\n"


            if this.currency_id.name == 'PYG':
                if texto_cortado and parte_cortada:
                    cheque += self.limitar_campo_espacios_derecha(38, " ") + self.limitar_campo_espacios_derecha(67, str(texto_cortado))+  "\n"
                    cheque += self.limitar_campo_espacios_derecha(25, " ") + self.limitar_campo_espacios_derecha(35, str(parte_cortada)+'.--')+  "\n"
                else:
                    cheque += self.limitar_campo_espacios_derecha(38, " ") + self.limitar_campo_espacios_derecha(70, str(this.amount_to_text(this.amount, this.currency_id)))+  "\n"
            else:
                if texto_cortado and parte_cortada:
                    cheque += self.limitar_campo_espacios_derecha(46, " " )+ self.limitar_campo_espacios_derecha(65, str(texto_cortado)) +  "\n "
                    cheque += self.limitar_campo_espacios_derecha(21, " " )+ self.limitar_campo_espacios_derecha(37, str(parte_cortada)+'.--') +  "\n"
                else:
                    cheque += self.limitar_campo_espacios_derecha(46, " " )+ self.limitar_campo_espacios_derecha(65, str(this.check_amount_in_words)+'.--') +  "\n"
            cheque += self.limitar_campo_espacios_derecha(5, " ") +  "\n"
            cheque += self.limitar_campo_espacios_derecha(5, " ") +  "\n"
            cheque += self.limitar_campo_espacios_derecha(5, " ") +  "\n"
            cheque += self.limitar_campo_espacios_derecha(5, " ") +  "\n"
            cheque += self.limitar_campo_espacios_derecha(5, " ") + self.limitar_campo_espacios_derecha(15, str(this.formatear_monto(this.amount,currency=this.currency_id))+'.--') +  "\n"

           
            printer_ip = False
            printer_ip = self.env['ir.config_parameter'].sudo().get_param('cheque_printer_ip')
            # printer_ip = "192.168.0.157"
            # debug_factura = []
            # for f in factura.split('\n'):
            #     debug_factura.append(f+ str('-holaaaaaaaaaaaaaaaaa'))
            # print(debug_factura)
            print(cheque)
            if printer_ip:
                SERVER = printer_ip
                PORT = 8090
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((SERVER, PORT))
                client.send(cheque.encode('utf-8'))
                client.close()
