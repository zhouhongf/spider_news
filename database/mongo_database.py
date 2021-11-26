from pymongo import MongoClient, collection
from config import singleton, Config
import time
import json
from functools import wraps

MONGODB = Config.MONGO_DICT




@singleton
class MongoDatabase:

    def client(self):
        mongo = MongoClient(
            host=MONGODB['host'] if MONGODB['host'] else 'localhost',
            port=MONGODB['port'] if MONGODB['port'] else 27017,
            username=MONGODB['username'] if MONGODB['username'] else '',
            password=MONGODB['password'],
        )
        return mongo

    def db(self):
        return self.client()[MONGODB['db']]

    @staticmethod
    def upsert(collec: collection, condition: dict, data: dict):
        result = collec.find_one(condition)
        if result:
            collec.update_one(condition, {'$set': data})
            print('MONGO数据库《%s》中upsert更新: %s' % (collec.name, condition))
            return None
        else:
            collec.insert_one(data)
            print('MONGO数据库《%s》中upsert新增: %s' % (collec.name, condition))
            return condition

    @staticmethod
    def do_insert_one(collec: collection, condition: dict, data: dict):
        result = collec.find_one(condition)
        if result:
            print('MONGO数据库《%s》中do_insert_one已存在: %s' % (collec.name, condition))
            return None
        else:
            collec.insert_one(data)
            print('MONGO数据库《%s》中do_insert_one新增: %s' % (collec.name, condition))
            return condition


def send_database():
    time_start = time.perf_counter()
    print('===================================运行MongoDB备份: %s=========================================' % time_start)
    mongo = MongoDatabase()
    mongo_db = mongo.db()
    collection_origin = mongo_db['MANUAL']

    mongo_remote = MongoClient(host=Config.HOST_REMOTE, port=27017, username=MONGODB['username'], password=MONGODB['password'])
    try:
        db_remote = mongo_remote[MONGODB['db']]
        collection_remote = db_remote['MANUAL']

        manuals = collection_origin.find({'status': 'undo'})
        if manuals.count() > 0:
            for data in manuals:
                condition = {'_id': data['_id']}
                result = collection_remote.find_one(condition)
                if not result:
                    done = collection_remote.insert_one(data)
                    if done:
                        data['status'] = 'uploaded'
                        collection_origin.update_one(condition, {'$set': data})
        else:
            print('MANUAL_URL数据库中没有未上传的记录。')
    except:
        print('===================================未能连接远程SERVER=======================================')
    time_end = time.perf_counter()
    print('===================================完成MongoDB备份: %s, 用时: %s=========================================' % (time_end, (time_end - time_start)))


def dump_data_json(database: str, collection_name: str):
    print('===================================开始执行dump_data_json()=======================================')
    mongo = MongoDatabase().client()
    db_origin = mongo[database]
    collection_origin = db_origin[collection_name]

    datas = collection_origin.find()
    list_data = [data for data in datas]
    filename = collection_name + '.json'
    with open(filename, 'w') as f:
        f.write(json.dumps(list_data, ensure_ascii=False, indent=2))
