#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import mysql.connector.pooling



class MySQLDB(object):
  """
  create a pool when connect mysql, which will decrease the time spent in 
  request connection, create connection and close connection.
  """
  def __init__(self, host="127.0.0.1", port="3306", user="test",
                password="test", database="testdb", pool_name="mypool",
                pool_size=3):
    res = {}
    self._host = host
    self._port = port
    self._user = user
    self._password = password
    self._database = database
    self._pool_size = pool_size

    res["host"] = self._host
    res["port"] = self._port
    res["user"] = self._user
    res["password"] = self._password
    res["database"] = self._database
    res["pool_size"] = self._pool_size

    self.dbconfig = res
    self.pool = self.create_pool(pool_name=pool_name)
  def create_pool(self, pool_name="mypool"):
    """
    Create a connection pool, after created, the request of connecting 
    MySQL could get a connection from this pool instead of request to 
    create a connection.
    :param pool_name: the name of pool, default is "mypool"
    :param pool_size: the size of pool, default is 3
    :return: connection pool
    """
    pool = mysql.connector.pooling.MySQLConnectionPool(
      pool_name=pool_name,
      pool_reset_session=True,
      **self.dbconfig)
    return pool

  def close(self, conn, cursor):
    """
    A method used to close connection of mysql.
    :param conn: 
    :param cursor: 
    :return: 
    """
    cursor.close()
    conn.close()

  def execute(self, sql, args=None, commit=False):
    """
    Execute a sql, it could be with args and with out args. The usage is 
    similar with execute() function in module pymysql.
    :param sql: sql clause
    :param args: args need by sql clause
    :param commit: whether to commit
    :return: if commit, return None, else, return result
    """
    # get connection form connection pool instead of create one.
    conn = self.pool.get_connection()
    cursor = conn.cursor()
    if args:
      cursor.execute(sql, args)
    else:
      cursor.execute(sql)
    if commit is True:
      conn.commit()
      self.close(conn, cursor)
      return None
    else:
      res = cursor.fetchall()
      self.close(conn, cursor)
      return res

  def executemany(self, sql, args, commit=False):
      """
      Execute with many args. Similar with executemany() function in pymysql.
      args should be a sequence.
      :param sql: sql clause
      :param args: args
      :param commit: commit or not.
      :return: if commit, return None, else, return result
      """
      # get connection form connection pool instead of create one.
      conn = self.pool.get_connection()
      cursor = conn.cursor()
      cursor.executemany(sql, args)
      if commit is True:
        conn.commit()
        self.close(conn, cursor)
        return None
      else:
        res = cursor.fetchall()
        self.close(conn, cursor)
        return res
  def get_processor_by_filename(self, params):
    sql = """ 
          SELECT 
            data_id, processor, step 
          FROM Test 
          WHERE 1 
            AND data_id = %s
            AND step = %s 
          ;
          """
    
    results = self.execute(sql, params)
    if len(results) >= 1:
      processors = list()
      for result in results:
        result = {
          "data_id"     :result[0], 
          "processor"   :result[1], 
          "step"        :result[2]
        }
        processors.append(result)
      return processors
    else:
      return None


#if __name__ == "__main__":
#    mysql_pool = MySQLDB(**dbconfig)

    # TESTING
    #while True:
#    t0 = time.time()
#    #for i in range(10):
#    print(mysql_pool.execute(sql,{"name":"/test/"}))
        #print(i)   
#    print("time cousumed:", time.time() - t0)