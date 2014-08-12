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

from openerp.addons.fts_base.fts_base import fts_base

class fts_analytic_account(fts_base):
    _model = 'account.analytic.account'
    _indexed_column = ['name','description']
    _title_column = 'name'
    _tsvector_column_index = 'analytic_account_name_desc_tsvector_idx'
    _tsvector_column_trigger = 'analytic_account_name_desc_tsvector_trigger'

class fts_project_task(fts_base):

    _model = 'project.task'
    _indexed_column = ['name','description','notes']
    _title_column = 'name'
    _tsvector_column_index = 'project_task_name_desc_notes_tsvector_idx'
    _tsvector_column_trigger = 'project_task_name_desc_notes_tsvector_trigger'
