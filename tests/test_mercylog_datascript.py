import unittest
from mercylog_datascript import core


class MercyLogTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.m = core.DataScriptV1()

    def test_find_data_pattern(self):
        N, A, E = self.m.variables('n', 'a', 'e')
        query = self.m.query(find=[N, A], where=[[E, "name", N], [E, "age", A]])
        self.assertEqual(query.code(), '[:find ?n ?a :where [?e "name" ?n] [?e "age" ?a]]')

    def test_find_underscore(self):
        title = self.m.variables('title')
        query = self.m.query(find=[title], where=[[self.m._, ":movie/title", title]])
        self.assertEqual(query.code(), '[:find ?title :where [_ ":movie/title" ?title]]')

    def test_find_string(self):
        e = self.m.variables('e')
        query = self.m.query(find=[e], where=[[e, ":person/name", "Ridley Scott"]])
        self.assertEqual(query.code(), '[:find ?e :where [?e ":person/name" "Ridley Scott"]]')

    def test_find_number(self):
        e = self.m.variables('e')
        query = self.m.query(find=[e], where=[[e, ":person/age", 32]])
        self.assertEqual(query.code(), '[:find ?e :where [?e ":person/age" 32]]')
        pass

    # def test_parameterized_queries(self):
    #     title, name, p, = self.m.variables('title', 'name', 'p')
    #     query = self.m.query(find=[title], parameters=[self.m.DB, name], where=[[p, ":person/name", name]])
    #     self.assertEqual(query.code(), '[:find ?title :in $ ?name :where [?p ":person/name" ?name]]')

    def test_parameterized_queries(self):
        title, name, p, = self.m.variables('title', 'name', 'p')
        query = self.m.query(find=[title], parameters=[name], where=[[p, ":person/name", name]])
        self.assertEqual(query.code(), '[:find ?title :in $ ?name :where [?p ":person/name" ?name]]')

    # def test_parameterized_queries_any(self):
    #     title, name, p = self.m.variables('title', 'name', 'p')
    #     query = self.m.query(find=[title], parameters=[self.m.DB, self.m.any(name)], where=[[p, ":person/name", name]])
    #     self.assertEqual(query.code(), '[:find ?title :in $ [?name ...] :where [?p ":person/name" ?name]]')

    # def test_parameterized_queries_relation(self):
    #     m, p, title, box_office, director = self.m.variables('m', 'p', 'title', 'box_office', 'director')
    #     query = self.m.query(find=[title,
    #                                box_office],
    #                          parameters=[self.m.DB,
    #                                      director,
    #                                      self.m.collection([title, box_office])],
    #                          where=[[p, ":person/name", director],
    #                                 [m, ":movie/director", p],
    #                                 [m, ":movie/title", title]])
    #     self.assertEqual(query.code(),
    #                      '[:find ?title ?box_office :in $ ?director [[?title ?box_office]] :where [?p ":person/name" ?director] [?m ":movie/director" ?p] [?m ":movie/title" ?title]]')
    #     #
    #     pass

    def test_parameterized_queries_relation(self):
        m, p, title, box_office, director = self.m.variables('m', 'p', 'title', 'box_office', 'director')
        query = self.m.query(find=[title,
                                   box_office],
                             parameters=[director,
                                         self.m.collection([title, box_office])],
                             where=[[p, ":person/name", director],
                                    [m, ":movie/director", p],
                                    [m, ":movie/title", title]])
        self.assertEqual(query.code(),
                         '[:find ?title ?box_office :in $ ?director [[?title ?box_office]] :where [?p ":person/name" ?director] [?m ":movie/director" ?p] [?m ":movie/title" ?title]]')
        #
        pass

    def test_predicates(self):
        e, a = self.m.variables('e', 'a')
        is_adult = self.m.function('is_adult', lambda x: x > 18)
        query = self.m.query(find=[e],
                             parameters=[is_adult],
                             where=[[e, "age", a],
                                    [is_adult(a)]])
        exp = '[:find ?e :in $ ?is_adult :where [?e "age" ?a] [(?is_adult ?a)]]'
        self.assertEqual(query.code(), exp)
        pass

    def test_attributes(self):
        p, attr = self.m.variables('p', 'attr')
        query = self.m.query(find=[attr],
                             where=[[p, ":person/name"],
                                    [p, attr]])

        exp = '[:find ?attr :where [?p ":person/name"] [?p ?attr]]'
        self.assertEqual(query.code(), exp)
        pass

    # def test_transformation(self):
    #     exp = '[:find ?age :in $ ?name ?today :where [?p ":person/name" ?name] [?p ":person/born" ?born] [(get_age ?born ?today) ?age]]'
    #     get_age = self.m.function("get_age", lambda a_born, a_today: a_today - a_born)
    #     born, p, age, today, name = self.m.variables('born', 'p', 'age', 'today', 'name')
    #     query = self.m.query(find=[age],
    #                          parameters=[self.m.DB, name, today],
    #                          where=[
    #                              [p, ":person/name", name],
    #                              [p, ":person/born", born],
    #                              [get_age(born, today), age]
    #                          ])
    #     self.assertEqual(query.code(), exp)
    #     pass

    def test_transformation(self):
        exp = '[:find ?age :in $ ?name ?today :where [?p ":person/name" ?name] [?p ":person/born" ?born] [(get_age ?born ?today) ?age]]'
        get_age = self.m.function("get_age", lambda a_born, a_today: a_today - a_born)
        born, p, age, today, name = self.m.variables('born', 'p', 'age', 'today', 'name')
        query = self.m.query(find=[age],
                             parameters=[name, today],
                             where=[[p, ":person/name", name],
                                    [p, ":person/born", born],
                                    [get_age(born, today), age]])
        self.assertEqual(query.code(), exp)

    def test_aggregates(self):
        e, a, date = self.m.variables('e', 'a', 'date')
        agg = self.m.agg
        query = self.m.query(find=[agg.max(date)],
                             where=[[e, "age", a]])
        exp = '[:find (max ?date) :where [?e "age" ?a]]'
        self.assertEqual(query.code(), exp)

        pass

    # def test_rules(self):
    #     name, title, p, m = self.m.variables('name', 'title', 'p', 'm')
    #     actor_movie = self.m.relation('actor-movie')
    #
    #     r = self.m.rule(actor_movie(name, title), [[p, ":person/name", name],
    #                                                [m, ":movie/cast", p],
    #                                                [m, ":movie/title", title]])
    #
    #     exp = '[:find ?name :in $ % :where (actor-movie ?name "The Terminator")]'
    #     # TODO: do we do self.m.rule to explicitly state it's a rule or we can guess from the where clause?
    #     query = self.m.query(find=[name],
    #                          parameters=[self.m.DB, self.m.RULE],
    #                          where=[actor_movie(name, "The Terminator")])
    #     self.assertEqual(query.code(), exp)
    #     pass

    def test_inbuilt_functions(self):
        title, m, year = self.m.variables('title', 'm', 'year')
        gt = self.m.function("<")
        exp = '[:find ?title :where [?m ":movie/title" ?title] [?m ":movie/year" ?year] [(< ?year 1984)]]'
        query = self.m.query(find=[title],
                             where=[[m, ":movie/title", title],
                                    [m, ":movie/year", year],
                                    [gt(year, 1984)]])
        self.assertEqual(query.code(), exp)

    pass

    def test_rules_implicit_set(self):
        name, title, p, m = self.m.variables('name', 'title', 'p', 'm')
        actor_movie = self.m.relation('actor-movie')

        r = self.m.rule(actor_movie(name, title), [[p, ":person/name", name],
                                                   [m, ":movie/cast", p],
                                                   [m, ":movie/title", title]])

        exp = '[:find ?name :in $ % :where (actor-movie ?name "The Terminator")]'
        query = self.m.query(find=[name],
                             where=[actor_movie(name, "The Terminator")])
        self.assertEqual(query.code(), exp)
        pass


if __name__ == '__main__':
    unittest.main()
