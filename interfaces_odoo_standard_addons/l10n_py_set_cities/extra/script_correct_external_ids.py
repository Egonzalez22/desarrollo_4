ir_model_datas = self.env["ir.model.data"].search(
    [
        ("module", "=", "facturacion_electronica_py"),
        ("model", "in", ["res.country.state", "res.district", "res.city"]),
    ]
)
ir_model_datas.write({"module": "l10n_py_set_cities"})
self._cr.commit()
