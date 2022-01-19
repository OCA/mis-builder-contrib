import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-mis-builder-contrib",
    description="Meta package for oca-mis-builder-contrib Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-mis_builder_analytic',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
