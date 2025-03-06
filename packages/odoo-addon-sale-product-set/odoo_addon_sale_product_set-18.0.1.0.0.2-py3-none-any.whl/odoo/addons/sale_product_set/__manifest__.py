# Copyright 2015 Anybox
# Copyright 2018 Camptocamp, ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sales product set",
    "category": "Sales",
    "license": "AGPL-3",
    "author": "Anybox, Odoo Community Association (OCA)",
    "version": "18.0.1.0.0",
    "website": "https://github.com/OCA/sale-workflow",
    "depends": ["sale", "sale_management", "product_set"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_set.xml",
        "views/product_set_line.xml",
        "wizard/sale_product_set_wizard_view.xml",
        "views/sale_order.xml",
        "views/res_config_settings.xml",
    ],
    "demo": ["demo/product_set_line.xml"],
    "installable": True,
}
