/* -*- coding: utf-8 -*-
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
############################################################################*/

openerp.fts_base = function(openerp)
{
    openerp.web.ListView.include(
    {
        init: function()
        {
            var result = this._super.apply(this, arguments);
            if(this.model == 'fts.proxy')
            {
                this.options.selectable = false;
            }
            return result;
        },
        select_record:function (index, view)
        {
            if(this.model == 'fts.proxy')
            {
                var self = this;
                this.dataset.read_ids(
                    this.dataset.ids[index],
                    ['model', 'res_id', 'name'])
                .then(function(row)
                    {
                        self.do_action({
                            type: 'ir.actions.act_window',
                            name: row.name,
                            res_model: row.model,
                            target: 'current',
                            //TODO: decide if we want a popup or breadcrumb. the latter i think
                            //target: 'new',
                            res_id: row.res_id,
                            views: [[false, 'form']],
                            flags: {
                                'initial_mode': 'view',
                            //    'initial_mode': 'edit',
                            },
                        });
                    });
            }
            else
            {
                return this._super.apply(this, arguments);
            }
        },
    });
}
