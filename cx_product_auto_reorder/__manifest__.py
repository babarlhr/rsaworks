# -*- coding: utf-8 -*-
{
    'name': 'Advanced Auto Reordering Rules Control. Create and Manage Reordering Rules using Templates, Automatic Reordering Rule Order Point Generator',
    'version': '12.0.1.0',
    'author': 'Ivan Sokolov',
    'category': 'Warehouse',
    'license': 'GPL-3',
    'website': 'https://demo.cetmix.com',
    'live_test_url': 'https://demo.cetmix.com',
    'summary': """Create and manage reordering rules automatically using templates""",
    'description': """
    Create reordering rules automatically from templates. Create stock orderpoint automatically. Use template to manage
     reordering rules. Automatically generate purchase order, Automatically generate manufacturing order. 
""",
    'depends': ['product', 'stock'],
    'images': ['static/description/banner.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/cx_stock_product.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
