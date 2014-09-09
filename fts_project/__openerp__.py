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
    "name": "Fulltext search - Projects and Tasks",
    "version": "1.0",
    "depends": ["fts_base", "project"],
    "author": "Therp BV, VRT Systems",
    "category": "Searching",
    "description": """
Fulltext search for projects and tasks
======================================

Search in name and description of projects, which in fact are analytic
accounts.

This module also enables search in name, description and notes of project
tasks.""",
    "init_xml": [],
    'update_xml': ['fts_project.xml'],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
