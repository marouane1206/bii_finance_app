#!/usr/bin/python
import psycopg2
from Config import DB_Params

def postgresql_disconnect(conn):
    """ Disconnect from PostgreSQL database server """
    try:
        if conn.cursor() is not None:
            # close the communication with the PostgreSQL
            cur = conn.cursor()
            cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')


if __name__ == '__main__':
    postgresql_disconnect(conn)
