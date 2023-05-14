import sqlite3
import PIL


class ImageOperator:
    def breakimage(imgurl):
        with open(imgurl,'rb') as f:
            bimage = f.read()
        return bimage


class DataBaseConnection:
    def __init__(self, dbpath):
        self.dbpath = dbpath

    def create_table(self):
        connection = sqlite3.connect('assets/mangadata.db')
        cursor = connection.cursor()
        try:
            cursor.execute('''CREATE TABLE availableMangas(
                      manganame text,
                      mangaimage blob
            ) ''')

        except sqlite3.OperationalError:
            pass

        connection.commit()
        connection.close()


    def select(self,table , keys, where=''):

        connection = sqlite3.connect('assets/mangadata.db')
        cursor = connection.cursor()

        cursor.execute(f'SELECT {keys} FROM {table} {where}')
        r = cursor.fetchall()

        connection.commit()
        connection.close()

        return r
    




