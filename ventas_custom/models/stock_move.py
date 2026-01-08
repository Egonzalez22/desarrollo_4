import random
from datetime import datetime

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"
    
    mostrar_boton_generar_serie = fields.Boolean(string='Mostrar botón generar serie', compute='_compute_mostrar_boton_generar_serie')
    motivo_id = fields.Many2one('ventas.motivo', string='Motivo')
    presentacion_id = fields.Many2one('ventas.presentacion', string='Presentación')
    metodos_ids = fields.Many2many('product.template', string='Métodos')
    codigo_muestra = fields.Char(string='Código Muestra')

    grupo_id = fields.Many2one('ventas.grupo', string='Grupo')


    @api.depends('move_line_ids')
    def _compute_mostrar_boton_generar_serie(self):
        """
        Método para mostrar el boton de generar serie
        """
        for record in self:
            record.mostrar_boton_generar_serie = all([line.product_id.es_muestra for line in record.move_line_ids])

    def action_generar_nro_serie(self):
        """
        Método para asociar el nro de serie de las muestras
        """
        try:
            for line in self.move_line_ids:
                # Si es una muestra
                if line.product_id.es_muestra:

                    serie_unica = self.obtener_serie_unica()
                    codigo_muestra = self.generar_codigo_muestra(line.product_id)

                    # Asignamos un lote a la muestra
                    lot_data = {
                        'name': serie_unica,
                        'product_id': line.product_id.id,
                        'company_id': self.company_id.id,
                    }
                    lot = self.env['stock.lot'].create(lot_data)

                    # Asignamos el lote a la linea
                    line.write({
                        'lot_id': lot.id,
                        'codigo_muestra': codigo_muestra,
                    })
        except Exception as e:
            print(e)

        # return {"type": "ir.actions.act_window_close"}

    def obtener_serie_unica(self):
        """
        Generamos el formato de serie unica por cada linea del stock move
        """
        # Obtenemos la secuencia
        secuencia = self.env['ir.sequence'].sudo().next_by_code('seq_nro_serie_muestra')

        # fecha en formato AAAAMMDD
        fecha = datetime.now().strftime('%Y%m%d')

        # concatenamos
        serie = f"{fecha}{secuencia}"

        return serie

    def generar_codigo_muestra(self, muestra):
        """
        De la reunión del viernes 10/Mayo/2024, junto a Erika Meza y bajo de indicaciones de la Lic. Adela, nos presentaron el Nuevo formato de Código de Muestra:

        CC-MMAA-SSSSS
        Donde : CC ->son las dos primeras letras del nombre de la Muestra

        MM -> es el mes en cifras de la recepción de las Muestras
        AA -> son las dos últimas cifras del año de la recepción de las Muestras
        SSSSS-> viene del último Nro. de Solicitud de Análisis de cada Grupo o Área de Análisis, que son : Farma, Alta Complejidad, Toxicología y Agroquímicos.
        """
        # Obtenemos el mes y el año
        today = datetime.now()
        today_str = today.strftime('%m%y')

        # Obtenemos las dos primeras letras del nombre de la muestra
        presentacion = muestra.name[:2].upper()

        # Obtenemos la secuencia del grupo de analisis
        seq_grupo = f'seq_muestra_grupo_{self.grupo_id.tipo_grupo}'
        secuencia = self.env['ir.sequence'].sudo().next_by_code(seq_grupo)
    
        # Formateamos el codigo
        codigo = f"{presentacion}-{today_str}-{secuencia}"

        return codigo