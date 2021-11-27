import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-mis-builder-contrib",
    description="Meta package for oca-mis-builder-contrib Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-mis_builder_budget_tier_validation',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
