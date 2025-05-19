{
    "name": "MIS Builder Contract",
    "summary": "Provide account contract lines for MIS builder reports",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/mis-builder-contrib",
    "depends": ["mis_builder", "contract"],
    "demo": [
        "demo/contract_line_demo.xml",
        "demo/mis_report_demo.xml",
        "demo/mis_report_instance_demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/mis_contract_line_view.xml",
    ],
    "installable": True,
}
