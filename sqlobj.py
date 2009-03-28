""" sqlobj --- Connection object and middleware for SQL
"""

__author__ = "Oliver Steele <steele@osteele.com>"
__copyright__ = "Copyright 1999-2001 by Oliver Steele."
__license__ = "Python License"

#
# Database Connection
#

import MySQLdb

class Connection:
    trace = 0
    simulation = 0

    def __init__(self, **keys):
        self.db = MySQLdb.Connect(**keys)
        self.cursor = self.db.cursor()
        self.nextid = 0 # for debugging

    def sqlvalue(self, s):
        if s is None:
            return 'NULL'
        elif type(s) == type(''):
            return '"' + self.db.escape_string(s) + '"'
        else:
            return "%s" % s

    def sqltest(self, k, v):
        return "%s=%s" % (k, self.sqlvalue(v))

    def insert(self, expr):
        if self.trace:
            print expr
        if self.simulation:
            pass
        else:
            self.cursor.execute(expr)

    def select(self, expr, limit=-1):
        if self.trace:
            print expr
        if self.simulation:
            self.nextid += 1
            return [self.nextid]
        else:
            try:
                self.cursor.execute(expr)
            except:
                import sys
                print >> sys.stderr, expr
                raise
            if limit==1:
                return self.cursor.fetchone()
            else:
                return self.cursor.fetchmany(limit)

    def insertRow(self, tableName, fields={}):
        self.insert("INSERT INTO " + tableName + "(" + \
               ','.join(["%s" % key for key in fields.keys()]) + ") " + \
               "VALUES (" + ','.join(map(self.sqlvalue, fields.values())) + ");")

    def truncateTables(self):
        if self.simulation: return
        for table, in self.select('show tables'):
            self.cursor.execute('truncate table %s' % table)

#
# Tables
#

# Base class
class Table:
    def __init__(self, name, keys=[], primaryKey=None, connection=None):
        self.name = name
        self.keys = keys
        self.primaryKey = primaryKey
        self.connection = connection

    def insert(self, **keys):
        connection.insertRow(self.name, keys)

    def lookup(self, **keys):
        results = connection.select( \
                "SELECT %s FROM %s WHERE " % (self.primaryKey, self.name) + \
                ' AND '.join([sqltest(k,v) for k,v in keys.items()]) + ';',
                limit=2)
        if results:
            assert len(results) == 1
            return results[0]
    
    def select(self, **keys):
        assert self.primaryKey
        if self.keys:
            lookupKeys = {}
            for key in self.keys:
                if keys.has_key(key):
                    lookupKeys[key] = keys[key]
            id = self.lookup(**lookupKeys)
            if id:
                #raise "duplicate entry: %r" % keys
                # todo: update if the fields aren't the same
                return id
        self.insert(**keys)
        return select("SELECT LAST_INSERT_ID();", limit=1)[0]

    def update(self, **keys):
        raise "Table.update() called"
        results = select( \
                "SELECT 1 FROM %s WHERE " % self.name + \
                ' AND '.join([sqltest(k,v) for (k,v) in keys.items()]) + ';', limit=1)
        if not results:
            self.insert(**keys)

    def get_id(self, **attrs):
        return self.select(**attrs)

# Entities have a unique primary key
class EntityTable(Table):
    def __init__(self, name, **attrs):
        assert attrs.get('primaryKey')
        Table.__init__(self, name, **attrs)

# Details have a non-unique foreign key.  A detail is one-to-many
# where the target is a data primitive.
class DetailTable(Table):
    pass

# Relations have at least two foreign keys.
# A relation is one-to-many or many-to-many.
class Relation(Table):
    pass
