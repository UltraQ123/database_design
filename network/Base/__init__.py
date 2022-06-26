from peewee import *
data = {
    'charset': 'utf8',
    'sql_mode': 'PIPES_AS_CONCAT',
    'use_unicode': True,
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'tj_market'
}
database = MySQLDatabase('test', **data)