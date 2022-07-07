# -*- coding: utf-8 -*-
# Part of Idealis Consulting. See LICENSE file for full copyright and licensing details.

{
    'name': "Purchase Approvals",

    'summary': """""",

    'description': """
    """,

    'author': "Idealis Consulting",
    'website': "http://www.idealisconsulting.com",

    'category': 'Human Resources/Approvals',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'approvals', 'purchase', 'hr'],

    # always loaded
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data
        'data/mail_data_template.xml',

        # Views
        'views/job_position_views.xml',
        'views/request_job_position_views.xml',
        'views/approval_category_views.xml',
        'views/approval_request_views.xml',
        'views/employee_views.xml',
        'views/purchase_order_views.xml',
        'views/res_config_settings_views.xml',

        # Wizards
        "wizards/refuse_approval_wizard_views.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'license': 'LGPL-3',
}
