# -*- coding: utf-8 -*-
##############################################################################
#
# This module is developed by Idealis Consulting SPRL
# Copyright (C) 2020 Idealis Consulting SPRL (<https://idealisconsulting.com>).
# All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'KYO Sale',
    'category': 'Sales',
    'website': 'https://www.idealisconsulting.com/',
    'summary': 'Sale Module for EXKi S.A',
    'version': '1.0',
    'description': """
        """,
    'author': 'Idealis Consulting',
    'depends': [
        'base',
        'sale',
        'documents',
    ],
    'data': [
        'views/sale_order.xml',
    ],
    'installable': True,
    'auto_install': False,
}
