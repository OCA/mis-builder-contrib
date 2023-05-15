import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-mis-builder-contrib",
    description="Meta package for oca-mis-builder-contrib Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-mis_builder_total_committed_purchase>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
