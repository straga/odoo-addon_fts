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
from openerp.osv import expression
from openerp import SUPERUSER_ID
import openerp

class fts_base_meta(type):

    _plugins = []
    _to_register = []

    def __init__(self, name, bases, attrs):
        if name != 'fts_base':
            if hasattr(self, 'pool'):
                self._register()
            elif self not in self._to_register:
                self._to_register.append(self)

        super(fts_base_meta, self).__init__(name, bases, attrs)

    def _register(self):
        cr = self.pool.db.cursor()
        cls=self(self.pool, cr)
        if cls._replace_base:
            for base in bases:
                for plugin in self._plugins:
                    if plugin.__class__==base:
                        self._plugins.remove(plugin)
        if cls not in self._plugins:
            self._plugins.append(cls)
        cr.commit()
        cr.close()

class fts_base(object):
    """This is the base class for modules implementing fulltext searches.
    If you want to mess around with ORM functions, you probably want to go to
    fts_proxy
    """

    __metaclass__ = fts_base_meta

    _model = None
    """The model this search works on. Required."""

    _indexed_column = None
    """The column this search works on. Required.
    If this is a list of strings, all of them will be indexed for the fulltext
    search.
    """

    _table = None
    """The table this search works on. Will be deduced from model if
    not set."""

    _tsvector_column = None
    """The column holding tsvector data. Will be created on init.
    If not set, it will be ${_indexed_column}_tsvector."""

    _tsvector_column_index = None
    """The name of the index for _tsvector_column.
    If not set, it will be ${_indexed_column}_idx."""

    _tsvector_column_trigger = None
    """The name of the trigger to update _tsvector_column when _indexed_column
    is updated.
    If not set, it will be ${_indexed_column}_trigger."""

    _tsconfig = 'pg_catalog.simple'
    """The fulltext config (=language) to be used. Will be read from 
    properties if they exist: A specific one for the current module, then
    fts_base."""

    _title_column = 'name'
    """The column to be shown as title of a match. This can be an arbitrary SQL
    expression"""

    _disable_seqscan = True
    """The postgresql query planner (as of 9.0) chooses against using the query
    planner way too often. This forces hin to use it which improves speed in all
    tested cases. Disable (and report) if this causes problems for you."""

    _replace_base = False
    """Set to true if you want to inherit a class inherited from this one and
    only show search results from your inherited class"""

    """Extra columns to be fetched from _table. Instead of columns, you can 
    also give expressions"""
    _extra_columns = []

    def __init__(self, pool, cr):
        """Assign default values and create _tsvector_column if necessary."""
        if not pool.get(self._model):
            return

        if not self._table:
            self._table = pool.get(self._model)._table

        if not self._tsvector_column:
            self._tsvector_column = (self._indexed_column
                        if isinstance(self._indexed_column, str)
                        else '_'.join(self._indexed_column)) + '_tsvector'

        if not self._tsvector_column_index:
            self._tsvector_column_index = self._tsvector_column + '_idx'

        if not self._tsvector_column_trigger:
            self._tsvector_column_trigger = self._tsvector_column + '_trigger'

        self._tsconfig=pool.get('ir.config_parameter').get_param(cr, 
                SUPERUSER_ID, 'fts_'+self._model+'_tsconfig', 
                pool.get('ir.config_parameter').get_param(cr, SUPERUSER_ID,
                    'fts_base_tsconfig', self._tsconfig))

        self._create_tsvector_column(pool, cr)

    def _create_tsvector_column(self, pool, cr):
        """Create the column to hold tsvector data."""

        if (self._model is None or self._tsvector_column is None or
            self._column_exists(cr, self._table, self._tsvector_column)):
            return

        cr.execute('''
            ALTER TABLE "%(table)s" ADD COLUMN "%(tsvector_column)s"
            tsvector''' %
            {
             'tsvector_column': self._tsvector_column,
             'table': self._table,
            })

        self._create_tsvector_column_index(pool, cr)
        self._create_indexed_column_trigger(pool, cr)
        pool.get('fts.proxy').create_init_tsvector_cronjob(cr, SUPERUSER_ID,
                                                           self)

    def _create_tsvector_column_index(self, pool, cr):
        """Create an index on _tsvector_column.
        Override if you want something else than gin."""

        cr.execute('''
            CREATE INDEX "%(tsvector_column_index)s" ON "%(table)s" USING
            gin("%(tsvector_column)s")''' %
            {
             'tsvector_column_index': self._tsvector_column_index,
             'tsvector_column': self._tsvector_column,
             'table': self._table,
            })


    def _create_indexed_column_trigger(self, pool, cr):
        """Create a trigger for changes to _indexed_column"""

       
        cr.execute('''
            CREATE TRIGGER "%(tsvector_column_trigger)s" BEFORE INSERT OR UPDATE
            ON "%(table)s" FOR EACH ROW EXECUTE PROCEDURE
            tsvector_update_trigger("%(tsvector_column)s", '%(language)s',
            "%(indexed_column)s")''' %
            {
                'tsvector_column': self._tsvector_column,
                'tsvector_column_trigger': self._tsvector_column_trigger,
                'table': self._table,
                'language': self._tsconfig,
                'indexed_column': (self._indexed_column
                                   if isinstance(self._indexed_column, str)
                                   else '","'.join(self._indexed_column))
            })

    def _drop_indexed_column_trigger(self, pool, cr):
        """Drop the trigger for changes to _indexed_column"""

        cr.execute('''
            DROP TRIGGER IF EXISTS "%(tsvector_column_trigger)s"
            ON "%(table)s"''' %
            {
                'tsvector_column_trigger': self._tsvector_column_trigger,
                'table': self._table,
            })
 
    def _init_tsvector_column(self, pool, cr):
        """Fill _tsvector_column. This can take a long time and is called in a
        cronjob.
        Override if you want to have more than just one column indexed. In that
        case you probably also have to override
        _create_indexed_column_trigger"""

        cr.execute('''
            UPDATE "%(table)s" SET "%(tsvector_column)s"=
            to_tsvector('%(language)s', %(indexed_column)s)''' %
            {
             'tsvector_column': self._tsvector_column,
             'table': self._table,
             'language': self._tsconfig,
             'indexed_column': ('"' + self._indexed_column + '"'
                                if isinstance(self._indexed_column, str)
                                else reduce(lambda x, y: ('' if x is None else
                                                          (x + " || ' ' || ")
                                                         ) +
                                            "coalesce(\"" + y + "\", '')",
                                            self._indexed_column)),
            })

    def _column_exists(self, cr, table, column):
        """Check if a columns exists in a table"""

        cr.execute("""SELECT column_name
            FROM information_schema.columns
            WHERE table_name='%(table)s' and column_name='%(column)s'""" %
            {'table': table, 'column': column})
        return cr.rowcount == 1

    def _get_filter_expression(self, cr, uid, args, context=None):
        """Return a expression for additional filtering"""
        orm_model=self.pool.get(self._model)

        applicable_args=[]

        def get_applicable_args(args, index):
            if expression.is_leaf(args[index]):
                #TODO: also check for inherited fields etc
                if ((
                        args[index][0] in orm_model._columns or
                        orm_model._log_access and 
                            args[index][0]  in ['create_date','create_uid',
                            'write_date', 'write_uid']
                    )
                    and
                    args[index][0] not in ['text','model']):
                    return [args[index]], 1
                else:
                    return [], 1
            else:
                op1=get_applicable_args(args, index+1)
                op2=get_applicable_args(args, index+op1[1]+1)
                return (([args[index]] 
                        if len(op1[0]) > 0 and len(op2[0]) > 0 
                        else []) +
                        op1[0] + op2[0],
                        op1[1] + op2[1] + 1
                        )

        if openerp.release.version_info[0] <= 6:
            args=get_applicable_args(expression.normalize(args), 0)[0]
        else:
            args=get_applicable_args(expression.normalize_domain(args), 0)[0]
        return expression.expression(cr, uid, args, orm_model, context)

    def _get_fts_proxy_values(self, cr, uid, row):
        """Returns the values used to create a new fts_proxy object. Override if
        you want to modify standard behavior or if you added columns in 
        _extra_column"""
        return {
                'model': self._model,
                'res_id': row[0],
                'rank': row[1],
                'name': row[2],
                'summary': row[3],
               }

    def search(self, cr, uid, args, order=None, context=None, count=False,
               searchstring=None):
        """The actual search function. Create fts.proxy objects and returns
        their ids.
        Override if you need more than full text matching against the query
        string"""

        res = []
        proxy_obj = self.pool.get('fts.proxy')

        if self._disable_seqscan:
            cr.execute('set enable_seqscan=off')

        filters=self._get_filter_expression(cr, uid, args, context).to_sql()
        filters=cr.mogrify(filters[0], filters[1])

        cr.execute(
        (
            "SELECT " +
            (
            "count(*)" if count else
            """
            id,
            ts_rank(%(tsvector_column)s,
                to_tsquery('%(language)s', %%(searchstring)s)),
            %(title_column)s,
            """ +
                (
                """
                ts_headline('%(language)s', %(indexed_column)s,  
                    to_tsquery('%(language)s', %%(searchstring)s),
                    'StartSel = *, StopSel = *')"""
                if context.get('fts_summary')
                else 'null'
                )
                +
                ((', '+reduce(lambda x,y: ('' if x is None else x+','+y),
                    self._extra_columns))
                if self._extra_columns else '')
            ) +
            """
            FROM %(table)s WHERE %(tsvector_column)s @@ 
                to_tsquery('%(language)s', %%(searchstring)s)"""
        ) %
        {
               'tsvector_column': self._tsvector_column,
               'table': self._table,
               'language': self._tsconfig,
               'indexed_column': ('"' + self._indexed_column + '"'
                                if isinstance(self._indexed_column, str)
                                else reduce(lambda x, y: ('' if x is None else
                                                          (x + " || ' ' || ")
                                                         ) +
                                            "coalesce(\"" + y + "\", '')",
                                            self._indexed_column)),
               'title_column': self._title_column,
        } + ' AND ' + str(filters),
        {'searchstring': searchstring})

        for row in cr.fetchall():

            if count:
                return row[0]

            res.append(proxy_obj.create(cr, uid, 
                self._get_fts_proxy_values(cr, uid, row)))

        if self._disable_seqscan:
            cr.execute('set enable_seqscan=on')

        return res
