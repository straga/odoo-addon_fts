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

from openerp.osv.orm import TransientModel
from openerp.osv import fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import SUPERUSER_ID
from openerp.release import version_info
from openerp.tools.translate import _
import openerp
from openerp.addons.fts_base.fts_base import fts_base_meta
from lxml import etree

class fts_config(TransientModel):
    _name = 'fts.config'

    _columns = {
              }

    def default_get(self, cr, uid, fields_list, context=None):
        result={}
        for search_plugin in fts_base_meta._plugins:
            result['tsconfig_'+search_plugin._model]=search_plugin._tsconfig
            result['lock_'+search_plugin._model]=False
        return result

    def fields_get(self, cr, user, fields=None, context=None):
        result=super(fts_config, self).fields_get(cr, user, fields, context)
        for search_plugin in fts_base_meta._plugins:
            result['tsconfig_'+search_plugin._model]={
                    'type': 'char',
                    'string': _('Configuration'),
                    'readonly': True
                    }
        return result

    def _get_default_form_view(self, cr, user, context=None):
        view = etree.Element('form', col='2')
        for search_plugin in fts_base_meta._plugins:
            group=etree.SubElement(view, 'group', string=search_plugin._model,
                    colspan='2', col='3')
            etree.SubElement(group, 'field',
                    name='tsconfig_'+search_plugin._model, invisible='True')
            etree.SubElement(group, 'field', 
                    name='tsconfig_'+search_plugin._model)
            etree.SubElement(group, 'button', type="object",
                    name="recreate_search_index", 
                    string=_("Recreate search index"), icon="gtk-refresh",
                    context=('{"recreate_search_index_model": "'+
                        search_plugin._model+'"}'))
        return view

    def recreate_search_index(self, cr, uid, ids, context=None):
        for search_plugin in fts_base_meta._plugins:
            if search_plugin._model==context.get('recreate_search_index_model'):
                self.pool.get('fts.proxy').recreate_search_index(cr, 
                        uid, search_plugin)
        return {'type': 'ir.actions.act_window_close'}
