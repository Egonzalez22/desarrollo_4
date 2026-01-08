from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_partner(self):
        res = super()._loader_params_res_partner()
        # Agregamos los campos extras que se mostraran en el formulario del partner
        res["search_params"]["fields"].extend(['tipo_documento', 'contribuyente', 'nro_documento', 'company_type', 'city_id'])
        return res

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()

        # Cargamos el modelo de ciudad
        new_model = 'res.city'
        if new_model not in result:
            result.append(new_model)

        return result

    def _loader_params_res_city(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['name', 'state_id', 'country_id'],
            },
        }

    def _get_pos_ui_res_city(self, params):
        return self.env['res.city'].search_read(**params['search_params'])
