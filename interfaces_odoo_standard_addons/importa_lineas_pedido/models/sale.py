from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import xlrd
import base64

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    xlsx_file=fields.Binary(string="Importar archivo")

    def importar_lineas(self):
        if not self.xlsx_file:
            raise ValidationError("Debe seleccionar un archivo para importar los datos")
        book=xlrd.open_workbook(file_contents= base64.b64decode(self.xlsx_file))
        sheet=book.sheet_by_index(0)
        self.write({'order_line':[(5,0,0)]})
        new_lines=[]
        for row in range(1,sheet.nrows):
            product=self.env['product.product'].search([('name','=',sheet.cell_value(row,0))])
            price_unit=sheet.cell_value(row,1)
            qty=sheet.cell_value(row,2)
            vals={
                'product_id':product.id,
                'name':product.display_name,
                'product_uom_qty':qty,
                'price_unit':price_unit,
                # 'company_id':self.env.company.id,
                # 'customer_lead':1,
                # 'currency_id':self.pricelist_id.currency_id.id
                }
            line=(0,0,vals)
            new_lines.append(line)
        self.write({'order_line':new_lines})
