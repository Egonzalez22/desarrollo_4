from odoo import fields, models, exceptions


class WizardReporteLibroInventario(models.TransientModel):
    _name = 'wizard.reporte_libro_inventario'
    _description = 'Wizard para el reporte de Libro Inventario'

    company_id = fields.Many2one('res.company', string="Compañia", default=lambda self: self.env.company.id, required=True)
    year = fields.Integer(string='Año', required=True, default=lambda self: fields.Date.today().year)

    def download_report_xlsx(self):
        return self.env.ref('reporte_libro_inventario.reporte_libro_inventario_report').report_action(self)


class ReporteLibroInventarioXLSX(models.AbstractModel):
    _name = 'report.reporte_libro_inventario.reporte_libro_inventario_t'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, datas):
        global sheet
        global bold
        global num_format
        global position_x
        global position_y
        bold = workbook.add_format({'bold': True})
        numerico = workbook.add_format({'num_format': True, 'align': 'right'})
        numerico.set_num_format('#,##0')
        numerico_total = workbook.add_format({'num_format': True, 'align': 'right', 'bold': True})
        numerico_total.set_num_format('#,##0')
        wrapped_text = workbook.add_format()
        wrapped_text.set_text_wrap()
        wrapped_text_bold = workbook.add_format({'bold': True})
        wrapped_text_bold.set_text_wrap()

        position_x = 0
        position_y = 0

        def addSalto(positions=1):
            global position_x
            global position_y
            position_x = 0
            position_y += positions

        def addRight(positions=1):
            global position_x
            position_x += positions

        def simpleWrite(to_write, format=None):
            global sheet
            if isinstance(to_write, int) or isinstance(to_write, float):
                to_write = int(to_write)
            sheet.write(position_y, position_x, to_write or ('' if type(to_write) != int else 0), format)

        def breakAndWrite(to_write, format=None):
            global sheet
            addSalto()
            simpleWrite(to_write, format)

        def rightAndWrite(to_write, format=None):
            global sheet
            addRight()
            simpleWrite(to_write, format)

        sheet = workbook.add_worksheet('Libro Inventario')
        sheet.set_column(0, 10, 30)

        wizard = datas

        debug_mode = False

        previous_options = {
            'single_company': [1],
            'fiscal_position': 'all',
            'date': {
                'string': str(wizard.year),
                'period_type': 'fiscalyear',
                'mode': 'range',
                'date_from': str(wizard.year) + '-01-01',
                'date_to': str(wizard.year) + '-12-31',
                'filter': 'custom'},
            'comparison': {'filter': 'no_comparison',
                           'number_period': 1,
                           'date_from': str(wizard.year) + '-01-01',
                           'date_to': str(wizard.year) + '-12-31',
                           'periods': []},
            'all_entries': False,
            'analytic': True,
            'unreconciled': True,
            'unfold_all': True,
            'analytic_groupby': True,
            'analytic_plan_groupby': True,
            'include_analytic_without_aml': False,
            'unposted_in_period': False
        }

        def print_account(
                env,
                expression_id,
                account_id,
                padding=0,
                hide_empty_lines=True,
        ):
            global expressions_totals
            account_id_dict = expressions_totals[expression_id][account_id]
            if hide_empty_lines and \
                    not any(account_id_dict.get(balance_type) for balance_type in ['account_balance', 'pending_outbound', 'pending_inbound']) and \
                    not debug_mode:
                return
            show_account_detail_mode = account_id_dict.get('show_account_detail_mode')
            addSalto()
            addRight(padding)
            simpleWrite(account_id.code + '-' + account_id.name, bold)
            if debug_mode:
                rightAndWrite(account_id.id, bold)  # SOLO PRESENTE EN MODO DEBUG
                rightAndWrite(show_account_detail_mode)  # SOLO PRESENTE EN MODO DEBUG
            addRight(3)
            simpleWrite(account_id_dict.get('account_total'), numerico)
            if show_account_detail_mode == 'mode_account_balance':
                addSalto()
                addRight(padding)
                simpleWrite('Saldo Conciliado')
                addRight()
                rightAndWrite(account_id_dict.get('account_balance'), numerico)
                addSalto()
                addRight(padding)
                simpleWrite('Pagos pendientes de conciliación')
                addRight()
                rightAndWrite(account_id_dict.get('pending_outbound'), numerico)
                addSalto()
                addRight(padding)
                simpleWrite('Recibos pendientes de conciliación')
                addRight()
                rightAndWrite(account_id_dict.get('pending_inbound'), numerico)
            elif show_account_detail_mode == 'mode_account_partners':
                account_move_line_ids = account_id_dict.get('account_move_line_ids')
                if account_move_line_ids:
                    partner_ids = account_move_line_ids.mapped('partner_id')
                    partner_ids_list = list(partner_ids)
                    if account_id_dict.get('account_move_line_ids').filtered(lambda x: not x.partner_id):
                        partner_ids_list.append(partner_ids.browse())
                    for partner_id in partner_ids_list:
                        account_move_line_ids_partner = account_id_dict.get('account_move_line_ids').filtered(
                            lambda x: x.partner_id == partner_id
                        )
                        addSalto()
                        addRight(padding)
                        simpleWrite(partner_id.name if partner_id else 'Sin nombre')
                        rightAndWrite(sum(account_move_line.amount_residual for account_move_line in account_move_line_ids_partner), numerico)
            elif show_account_detail_mode == 'mode_account_inventory':
                if env.ref('base.module_stock').state in ['installed', 'to upgrade']:
                    stock_valuation_layer_ids = env['stock.valuation.layer'].search([
                        ('product_id.categ_id.property_stock_valuation_account_id', '=', account_id.id),
                    ])
                    for product_id in stock_valuation_layer_ids.product_id:
                        stock_valuation_layers_product_id = stock_valuation_layer_ids.filtered(lambda x: x.product_id == product_id)

                        stock_valuation_layers_product_id_quantity = sum(
                            stock_valuation_layer_product_id.quantity for stock_valuation_layer_product_id in stock_valuation_layers_product_id
                        )

                        stock_valuation_layers_product_id_value = sum(
                            stock_valuation_layer_product_id.value for stock_valuation_layer_product_id in stock_valuation_layers_product_id
                        )

                        stock_valuation_layers_product_id_unit_cost = 0
                        if stock_valuation_layers_product_id_value and stock_valuation_layers_product_id_quantity:
                            stock_valuation_layers_product_id_unit_cost = stock_valuation_layers_product_id_value / stock_valuation_layers_product_id_quantity

                        addSalto()
                        addRight(padding - 1)
                        simpleWrite(stock_valuation_layers_product_id_quantity, numerico)
                        rightAndWrite(product_id.name)
                        rightAndWrite(stock_valuation_layers_product_id_unit_cost, numerico)
                        rightAndWrite(stock_valuation_layers_product_id_value, numerico)
            elif show_account_detail_mode == 'mode_account_asset_fixed':
                account_assets = env['account.asset'].search([
                    ('state', 'in', ['open', 'close']),
                    ('account_asset_id', '=', account_id.id),
                ])
                for account_asset in account_assets:
                    addSalto()
                    addRight(padding)
                    simpleWrite(account_asset.name)
                    if account_asset.state == 'open' and not account_id.asset_model:
                        rightAndWrite(account_asset.original_value, numerico)
                    elif account_asset.state == 'close' or \
                            account_asset.state == 'open' and account_id.asset_model:
                        rightAndWrite(account_asset.book_value, numerico)

        def print_accounts_by_group(
                env,
                expression_id,
                padding,
                hide_empty_lines,
                group_ids,
                allowed_account_group_ids,
                account_ids,
        ):
            for group_id in group_ids:
                child_group_ids = group_ids.search([('parent_id', '=', group_id.id), ('id', 'in', allowed_account_group_ids.ids)])
                for account_group_id in child_group_ids:
                    account_group_for_total_ids = account_group_id
                    while True:
                        account_group_child_ids = account_group_for_total_ids.search([
                            ('parent_id','in',account_group_for_total_ids.ids),
                            ('id','not in',account_group_for_total_ids.ids),
                        ])
                        if account_group_child_ids:
                            account_group_for_total_ids |= account_group_child_ids
                        else:
                            break

                    account_group_total = sum([
                        expressions_totals[expression_id][account_id].get('account_total') for account_id in account_ids.search([
                            ('id', 'in', account_ids.ids),
                            ('group_id', 'in', account_group_for_total_ids.ids),
                        ])
                    ])

                    addSalto()
                    addRight(padding)
                    simpleWrite(account_group_id.name, bold)
                    addRight(3)
                    simpleWrite(account_group_total, numerico_total)
                    for account_id in account_ids.filtered(lambda account: account.group_id == account_group_id):
                        print_account(
                            env=env,
                            expression_id=expression_id,
                            account_id=account_id,
                            padding=padding,
                            hide_empty_lines=hide_empty_lines,
                        )
                    print_accounts_by_group(
                        env=env,
                        expression_id=expression_id,
                        padding=padding,
                        hide_empty_lines=hide_empty_lines,
                        group_ids=account_group_id,
                        allowed_account_group_ids=allowed_account_group_ids,
                        account_ids=account_ids,
                    )

        def print_report_lines(
                env,
                report_lines,
                padding,
                headers,
                quantity_headers,
                hide_empty_lines,
                force_print_from_report_totals,
                force_report_totals,
                account_report_id,
        ):
            if headers:
                addSalto()
                simpleWrite('Cantidad', bold)
                rightAndWrite('Detalle', bold)
                rightAndWrite('Precio Unitario', bold)
                rightAndWrite('Subotal', bold)
                rightAndWrite('Total', bold)
                headers = False

            global expressions_totals

            for report_line in report_lines:
                if force_print_from_report_totals and \
                        force_report_totals or \
                        (
                                force_report_totals and
                                ('cross_report' in [expression_id.subformula for expression_id in report_line.expression_ids]) or
                                (
                                        not report_line.foldable and not report_line.hide_if_zero
                                )
                        ):
                    report_line_total = sum(
                        force_report_totals.get(expression_id.id).get('value') for expression_id in report_line.expression_ids
                    )
                else:
                    report_line_total = sum(
                        sum(
                            expressions_totals[expression_id][account_id].get('account_total')
                            for account_id in expressions_totals[expression_id]
                        )
                        for expression_id in
                        report_line.search([('id', 'child_of', report_line.ids)]).expression_ids.filtered(lambda x: x.engine == 'domain')
                    )

                if hide_empty_lines and not report_line_total and not debug_mode:
                    continue

                addSalto()
                addRight(padding)
                simpleWrite(report_line.name, bold)
                if debug_mode: rightAndWrite(report_line.id, bold)  # SOLO PRESENTE EN MODO DEBUG
                addRight(3)
                simpleWrite(report_line_total, numerico_total)
                report_line_expressions = report_line.expression_ids.filtered(lambda x: x.engine == 'domain')
                for expression_id in report_line_expressions:
                    if account_report_id.filter_hierarchy == 'by_default':
                        account_ids = env['account.account'].browse([a.id for a in expressions_totals[expression_id]])
                        account_group_ids = account_ids.group_id
                        while True:
                            account_group_parent_ids = account_group_ids.parent_id.filtered(lambda x: x not in account_group_ids)
                            if account_group_parent_ids:
                                account_group_ids |= account_group_parent_ids
                            else:
                                break
                        root_group_ids = account_group_ids.filtered(lambda x: not x.parent_id)

                        print_accounts_by_group(
                            env=env,
                            expression_id=expression_id,
                            padding=padding,
                            hide_empty_lines=hide_empty_lines,
                            group_ids=root_group_ids,
                            allowed_account_group_ids=account_group_ids,
                            account_ids=account_ids,
                        )
                    else:
                        for account_id in expressions_totals[expression_id]:
                            print_account(
                                env,
                                expression_id,
                                account_id,
                                padding=padding,
                                hide_empty_lines=hide_empty_lines,
                            )
                print_report_lines(
                    env=env,
                    report_lines=report_line.children_ids,
                    padding=padding,
                    headers=headers,
                    quantity_headers=quantity_headers,
                    hide_empty_lines=hide_empty_lines,
                    force_print_from_report_totals=force_print_from_report_totals,
                    force_report_totals=force_report_totals,
                    account_report_id=account_report_id,
                )

        #
        #
        #
        #
        # BALANCE GENERAL
        #
        #
        #
        #
        account_financial_report_bg_l10n_py = wizard.company_id.reporte_libro_inventario_base_report_bg
        if not account_financial_report_bg_l10n_py:
            raise exceptions.ValidationError(
                'No está establecido un reporte base para el Balance General del reporte Libro Inventario, vaya a la configuración de contabilidad para establecer los parámetros necesarios')
        account_financial_report_bg_l10n_py_report_informations = account_financial_report_bg_l10n_py.get_report_informations(previous_options=previous_options)
        account_financial_report_bg_l10n_py_report_informations = account_financial_report_bg_l10n_py_report_informations.get('column_groups_totals')
        account_financial_report_bg_l10n_py_report_informations = account_financial_report_bg_l10n_py_report_informations.get(
            list(account_financial_report_bg_l10n_py_report_informations.keys())[0]
        )

        global expressions_totals  # El contenido de esta variable será calculado fuera de la función que imprime las líneas, por eso se declara como una variable global

        simpleWrite('INVENTARIO GENERAL PRACTICADO AL 31 DE DICIEMBRE DE ' + str(wizard.year), bold)
        expressions_totals = {}  # Acá irán todos los valores de las cuentas a imprimir

        expression_ids = account_financial_report_bg_l10n_py.line_ids.expression_ids.filtered(lambda
                                                                                                  x: x.engine == 'domain')  # Se filtran las expresiones de las líneas que forman la estructura del reporte, solo se usarán las expresiones que usen 'domain' para el cálculo de su contenido
        for expression_id in expression_ids:
            expressions_totals[expression_id] = {}
            aml_ids = eval(
                "wizard.env['account.move.line'].search(" + expression_id.formula + ")")  # Cada expresión a procesar tiene un dominio para obtener los apuntes contables, de los cuales se deben obtener las cuentas a preocesar
            for account_id in aml_ids.mapped('account_id').filtered(
                    lambda x:
                    x.account_type in [
                        'asset_cash',
                        'asset_receivable',
                        'asset_current',
                        'asset_non_current',
                        'asset_fixed',
                        'liability_payable',
                        'liability_current',
                        'liability_non_current',
                        'equity',
                    ]
                    and x not in (
                            x.company_id.account_journal_payment_debit_account_id,
                            x.company_id.account_journal_payment_credit_account_id,
                    )
            ).sorted(key=lambda x: x.code):

                # BALANCE A LA FECHA
                account_move_line_ids = aml_ids.search(domain=[
                    ('account_id', '=', account_id.id),
                    ('parent_state', '=', 'posted'),
                    ('date', '<=', previous_options['date']['date_to'])
                ])
                if account_move_line_ids:
                    account_balance = sum(account_move_line_ids.mapped('balance'))
                else:
                    account_balance = 0
                account_outbound = 0
                account_inbound = 0
                for move_type in ['outbound', 'inbound']:
                    wizard.env.cr.execute("""
                        SELECT SUM(amount_company_currency_signed) AS amount_total_company
                          FROM account_payment payment
                          JOIN account_move move ON move.payment_id = payment.id
                         WHERE payment.is_matched IS NOT TRUE
                           AND payment.payment_type = %s
                           AND move.state = 'posted'
                           AND move.journal_id = ANY(%s)
                      GROUP BY move.company_id, move.journal_id, move.currency_id
                    """, [move_type, wizard.env['account.journal'].search(
                        [('default_account_id', '=', account_id.id)]).ids])  # Debemos obtener todos los saldos pendientes de conciliar para la cuenta
                    query_result = self.env.cr.fetchall()
                    amount_result = sum(sum(j for j in t) for t in query_result)
                    if move_type == 'outbound':
                        account_outbound = -amount_result
                    if move_type == 'inbound':
                        account_inbound = amount_result

                # Determinamos qué modo de detalles va a tener la cuenta.
                # En el modo 'mode_account_balance' se detalla el saldo conciliado, y los pendientes de conciliación de entrada y salida.
                # En el modo 'mode_account_partners' se detalla los saldos pendientes de conciliación pero agrupados por proveedor o cliente.
                # En el modo 'mode_account_inventory' se detalla la valoración de inventario.
                # En el modo 'mode_account_asset_fixed' se detalla la valoración de los activos fijos.
                show_account_detail_mode = False

                if account_id.account_type == 'asset_cash' and not account_id.reconcile:
                    show_account_detail_mode = 'mode_account_balance'

                elif (account_id.account_type == 'asset_receivable' and account_id.reconcile) or \
                        (account_id.account_type == 'liability_payable' and account_id.reconcile):
                    show_account_detail_mode = 'mode_account_partners'

                elif account_id.account_type == 'asset_current' and not account_id.reconcile and account_id.create_asset in ['no']:
                    show_account_detail_mode = 'mode_account_inventory'

                elif (account_id.account_type == 'asset_fixed') or \
                        (account_id.account_type == 'liability_current') or \
                        (
                                account_id.account_type == 'asset_current' and
                                not account_id.reconcile and
                                account_id.create_asset in ['draft', 'validate'] and
                                account_id.asset_model
                        ):
                    show_account_detail_mode = 'mode_account_asset_fixed'

                if expression_id.subformula == '-sum':
                    account_balance *= -1
                    account_inbound *= -1
                    account_outbound *= -1

                expressions_totals[expression_id][account_id] = {
                    'account_total': account_balance + account_inbound - account_outbound,
                    'account_move_line_ids': account_move_line_ids,
                    'account_balance': account_balance,
                    'pending_outbound': account_outbound,
                    'pending_inbound': account_inbound,
                    'show_account_detail_mode': show_account_detail_mode,
                }

        print_report_lines(
            env=self.env,
            report_lines=account_financial_report_bg_l10n_py.line_ids.filtered(lambda x: not x.parent_id),
            padding=1,
            headers=True,
            quantity_headers=True,
            hide_empty_lines=True,
            force_print_from_report_totals=False,
            force_report_totals=account_financial_report_bg_l10n_py_report_informations,
            account_report_id=account_financial_report_bg_l10n_py,

        )

        addSalto(6)
        #
        #
        #
        #
        # ESTADO DE RESULTADOS
        #
        #
        #
        #
        account_financial_report_er_l10n_py = wizard.company_id.reporte_libro_inventario_base_report_er
        if not account_financial_report_er_l10n_py:
            raise exceptions.ValidationError(
                'No está establecido un reporte base para el Estado de Resultados del reporte Libro Inventario, vaya a la configuración de contabilidad para establecer los parámetros necesarios')
        account_financial_report_er_l10n_py_report_informations = account_financial_report_er_l10n_py.get_report_informations(previous_options=previous_options)
        account_financial_report_er_l10n_py_report_informations = account_financial_report_er_l10n_py_report_informations.get('column_groups_totals')
        account_financial_report_er_l10n_py_report_informations = account_financial_report_er_l10n_py_report_informations.get(
            list(account_financial_report_er_l10n_py_report_informations.keys())[0]
        )

        simpleWrite('ESTADO DE RESULTADOS PRACTICADO AL 31 DE DICIEMBRE DE ' + str(wizard.year), bold)
        expressions_totals = {}  # Acá irán todos los valores de las cuentas a imprimir

        expression_ids = account_financial_report_er_l10n_py.line_ids.expression_ids.filtered(lambda
                                                                                                  x: x.engine == 'domain')  # Se filtran las expresiones de las líneas que forman la estructura del reporte, solo se usarán las expresiones que usen 'domain' para el cálculo de su contenido
        for expression_id in expression_ids:
            expressions_totals[expression_id] = {}
            aml_ids = eval(
                "wizard.env['account.move.line'].search(" + expression_id.formula + ")")  # Cada expresión a procesar tiene un dominio para obtener los apuntes contables, de los cuales se deben obtener las cuentas a preocesar
            for account_id in aml_ids.mapped('account_id').filtered(
                    lambda x:
                    x.account_type in [
                        'income',
                        'expense',
                        'expense_depreciation',
                        'income_other',
                    ]
                    and x not in (
                            x.company_id.account_journal_payment_debit_account_id,
                            x.company_id.account_journal_payment_credit_account_id,
                    )
            ).sorted(key=lambda x: x.code):

                # BALANCE A LA FECHA
                account_move_line_ids = aml_ids.search(domain=[
                    ('account_id', '=', account_id.id),
                    ('parent_state', '=', 'posted'),
                    ('date', '<=', previous_options['date']['date_to'])
                ])
                if account_move_line_ids:
                    account_balance = sum(account_move_line_ids.mapped('balance'))
                else:
                    account_balance = 0
                account_outbound = 0
                account_inbound = 0
                for move_type in ['outbound', 'inbound']:
                    wizard.env.cr.execute("""
                        SELECT SUM(amount_company_currency_signed) AS amount_total_company
                          FROM account_payment payment
                          JOIN account_move move ON move.payment_id = payment.id
                         WHERE payment.is_matched IS NOT TRUE
                           AND payment.payment_type = %s
                           AND move.state = 'posted'
                           AND move.journal_id = ANY(%s)
                      GROUP BY move.company_id, move.journal_id, move.currency_id
                    """, [move_type, wizard.env['account.journal'].search(
                        [('default_account_id', '=', account_id.id)]).ids])  # Debemos obtener todos los saldos pendientes de conciliar para la cuenta
                    query_result = self.env.cr.fetchall()
                    amount_result = sum(sum(j for j in t) for t in query_result)
                    if move_type == 'outbound':
                        account_outbound = -amount_result
                    if move_type == 'inbound':
                        account_inbound = amount_result

                # Determinamos qué modo de detalles va a tener la cuenta.
                # En el modo 'mode_account_balance' se detalla el saldo conciliado, y los pendientes de conciliación de entrada y salida.
                # En el modo 'mode_account_partners' se detalla los saldos pendientes de conciliación pero agrupados por proveedor o cliente.
                # En el modo 'mode_account_inventory' se detalla la valoración de inventario.
                # En el modo 'mode_account_asset_fixed' se detalla la valoración de los activos fijos.
                show_account_detail_mode = False

                # if account_id.account_type == 'asset_cash' and not account_id.reconcile:
                #     show_account_detail_mode = 'mode_account_balance'
                #
                # elif (account_id.account_type == 'asset_receivable' and account_id.reconcile) or \
                #         (account_id.account_type == 'liability_payable' and account_id.reconcile):
                #     show_account_detail_mode = 'mode_account_partners'
                #
                # elif account_id.account_type == 'asset_current' and not account_id.reconcile and account_id.create_asset in ['no']:
                #     show_account_detail_mode = 'mode_account_inventory'
                #
                # elif (account_id.account_type == 'asset_fixed') or \
                #         (account_id.account_type == 'liability_current') or \
                #         (
                #                 account_id.account_type == 'asset_current' and
                #                 not account_id.reconcile and
                #                 account_id.create_asset in ['draft', 'validate'] and
                #                 account_id.asset_model
                #         ):
                #     show_account_detail_mode = 'mode_account_asset_fixed'

                if expression_id.subformula == '-sum':
                    account_balance *= -1
                    account_inbound *= -1
                    account_outbound *= -1

                expressions_totals[expression_id][account_id] = {
                    'account_total': account_balance + account_inbound - account_outbound,
                    'account_move_line_ids': account_move_line_ids,
                    'account_balance': account_balance,
                    'pending_outbound': account_outbound,
                    'pending_inbound': account_inbound,
                    'show_account_detail_mode': show_account_detail_mode,
                }

        print_report_lines(
            env=self.env,
            report_lines=account_financial_report_er_l10n_py.line_ids.filtered(lambda x: not x.parent_id),
            padding=1,
            headers=True,
            quantity_headers=False,
            hide_empty_lines=True,
            force_print_from_report_totals=True,
            force_report_totals=account_financial_report_er_l10n_py_report_informations,
            account_report_id=account_financial_report_er_l10n_py,
        )
