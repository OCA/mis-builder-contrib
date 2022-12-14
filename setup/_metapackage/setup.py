import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-mis-builder-contrib",
    description="Meta package for oca-mis-builder-contrib Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-mis_builder_budget_product>=15.0dev,<15.1dev',
        'odoo-addon-mis_builder_total_committed_purchase>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
