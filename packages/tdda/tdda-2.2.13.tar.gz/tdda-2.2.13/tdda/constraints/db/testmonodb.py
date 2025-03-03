print('Skipping MongoDB tests (not yet working)', file=sys.stderr)

#if pymongo and not os.path.exists(MONGODB_CONN_FILE):
#    print('Skipping Mongo because no connection file exists at %s.'
#          % MONGODB_CONN_FILE)

MONGODB_CONN_FILE = os.path.join(os.path.expanduser('~'),
                                 '.tdda_db_conn_mongodb')

try:
    import pymongo
except ImportError:
    #print('Skipping MongoDB tests (no driver library pymongo)',
           file=sys.stderr)
    pymongo = None
pymongo = None  # The tests don't yet work for MongoDB


@unittest.skipIf(pymongo is None or not os.path.exists(MONGODB_CONN_FILE),
                 'MongoDB not available, or no tdda mongodb connection file')
class TestMongoDBConstraintDiscoverers(ReferenceTestCase,
                                       TestDatabaseConstraintDiscoverers):
    @classmethod
    def setUpClass(cls):
        cls.db = database_connection(dbtype='mongodb')
        cls.dbh = DatabaseHandler('mongodb', cls.db)

@unittest.skipIf(pymongo is None or not os.path.exists(MONGODB_CONN_FILE),
                 'MongoDB not available, or no tdda mongodb connection file')
class TestMongoDBHandlers(ReferenceTestCase, TestDatabaseHandlers):
    @classmethod
    def setUpClass(cls):
        db = database_connection(dbtype='mongodb')
        cls.dbh = DatabaseHandler('mongodb', db)

TestMongoDBConstraintDiscoverers.set_default_data_location(TESTDATA_DIR)
