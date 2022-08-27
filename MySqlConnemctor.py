import mysql.connector


class MySqlConnector:
    def __init__(self, mysql_config):
        self.connection = mysql.connector.connect(**mysql_config)

    def close_connection(self):
        if self.connection.is_connected():
            cursor = self.connection.cursor()
            cursor.close()
            self.connection.close()

    def execute(self, query):
        if self.connection.is_connected():
            cursor = self.connection.cursor()
            cursor.execute(query)
            record = cursor.fetchone()
            cursor.close()
            return record

    def insert(self, query):
        if self.connection.is_connected():
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
