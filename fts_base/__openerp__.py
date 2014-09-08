# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Fulltext search",
    "version": "1.1",
    "depends": ["base"],
    "author": "Therp BV",
    "category": "Searching",
    "description": """
Base module for fulltext search
===============================

Note that this module by itself does nothing. To actually do searches, install 
at least one of the other fts_* modules, which enable searching for their
respective object types.""",
    "init_xml": [],
    'data': ["fts_proxy.xml", 'wizard/fts_config.xml', 'view/fts_base.xml'],
    'demo_xml': [],

    'installable': True,
    'active': False,
}
