class DataScriptDemo:
    def __init__(self, js):

    def get_result(self):
        # var d = require('datascript');
        # // or
        # // var d = datascript.js;
        db = datascript.empty_db()
        db1 = datascript.db_with(db, [[":db/add", 1, "name", "Ivan"],
                                      [":db/add", 1, "age", 17]])
        db2 = datascript.db_with(db1, [{":db/id": 2,
                                        "name": "Igor",
                                        "age": 35}])

        q = '[:find ?n ?a :where [?e "name" ?n] [?e "age" ?a]]'
        result = datascript.q(q, db2)
        document.getElementById('greet').innerHTML = str(result)


datascript_demo = DataScriptDemo()
