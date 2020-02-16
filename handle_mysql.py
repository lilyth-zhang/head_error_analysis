import pymysql

class database_handler(object):
    ''' 定义一个 MySQL 操作类'''
    
    def __init__(self,host,username,password,database,port):
        '''初始化数据库信息并创建数据库连接'''
        self.db = pymysql.connect(host
                                  ,username
                                  ,password
                                  ,database
                                  ,port
                                  ,charset='utf8')
    
    def exec(self,sql):
        ''' 执行sql '''
        self.cursor = self.db.cursor()
        try:
            # 执行sql
            affect_cnt = self.cursor.execute(sql)
            self.db.commit()
            return affect_cnt
        except:
            # 发生错误时回滚
            self.db.rollback()
        finally:
            self.cursor.close()
        return
    
    def exec_many(self,sql,data_list):
        ''' bulk execute sql 
        
        Args:
            sql: eg: "INSERT IGNORE INTO test_entry_CJ VALUES(null,%s,%s,%s)"
            data_list: list of tuple, eg: [('python','mysql','HTML'),('脚本语言'，'数据库'，'超文本标记语言')]
        '''
        self.cursor = self.db.cursor()
        try:
            affect_cnt = self.cursor.executemany(sql, data_list)
            self.db.commit()
            return affect_cnt
        except Exception as e:
            print(e)
            self.db.rollback()
        finally:
            self.cursor.close()
        return 

    def query(self,sql):
        ''' 数据库查询 '''
        self.cursor = self.db.cursor()
        try:
            self.cursor.execute(sql) # 返回 查询数据 条数 可以根据 返回值 判定处理结果
            data = self.cursor.fetchall() # 返回所有记录列表
            return data
        except Exception as e:
            print(e)
            self.db.rollback()
        finally:
            self.cursor.close()
        return

    def close(self):
        ''' 数据库连接关闭 '''
        self.db.close()

        
if __name__ == '__main__':
    mydb = database_handler('172.16.0.173', 'sail', 'sunmiailab2019', 'heads_error_analysis_db', 43306)
    print('connected success')
    ### head_error_main,video_path,pic_path,model_path #########
    ## 写个循环，弄个语句
#     print(mydb.query('select * from trjctry_runtime'))
#     mydb.exec_many('insert into trjctry_runtime values (%s, %s)',
#                        [(0, current_time)])


#  alter table model_path modify column m_path varchar(1000);
