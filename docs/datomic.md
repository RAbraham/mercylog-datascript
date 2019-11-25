Extensible Data Notation

In Datomic, a Datalog query is written in extensible data notation (edn). Edn is a data format similar to JSON, but it:

    is extensible with user defined value types,
    has more base types,
    is a subset of Clojure data.

Edn consists of:

    Numbers: 42, 3.14159
    Strings: "This is a string"
    Keywords: :kw, :namespaced/keyword, :foo.bar/baz
    Symbols: max, +, ?title
    Vectors: [1 2 3] [:find ?foo ...]
    Lists: (3.14 :foo [:bar :baz]), (+ 1 2 3 4)
    Instants: #inst "2013-02-26"
    .. and a few other things which we will not need in this tutorial.

Here is an example query that finds all movie titles in our example database:

[:find ?title
 :where 
 [_ :movie/title ?title]]

Note that the query is a vector with four elements:

    the keyword :find
    the symbol ?title
    the keyword :where
    the vector [_ :movie/title ?title]

We'll go over the specific parts of the query later, but for now you should simply type the above query verbatim into the textbox below, press Run Query, and then continue to the next part of the tutorial.
Next chapter >>

    0

Find all movies titles in the database.

Query:[ I give up! ]

[:find ...

 ]

## Basic Queries

The example database we'll use contains movies mostly, but not exclusively, from the 80s. You'll find information about movie titles, release year, directors, cast members etc. As the tutorial advances we'll learn more about the contents of the database and how it's organized.

The data model in Datomic is based around atomic facts called datoms. A datom is a 4-tuple consisting of

    Entity ID
    Attribute
    Value
    Transaction ID

You can think of the database as a flat set of datoms of the form:

[<e-id>  <attribute>      <value>          <tx-id>]
...
[ 167    :person/name     "James Cameron"    102  ]
[ 234    :movie/title     "Die Hard"         102  ]
[ 234    :movie/year      1987               102  ]
[ 235    :movie/title     "Terminator"       102  ]
[ 235    :movie/director  167                102  ]
...

Note that the last two datoms share the same entity ID, which means they are facts about the same movie. Note also that the last datom's value is the same as the first datom's entity ID, i.e. the value of the :movie/director attribute is itself an entity. All the datoms in the above set were added to the database in the same transaction, so they share the same transaction ID.

A query is represented as a vector starting with the keyword :find followed by one or more pattern variables (symbols starting with ?, e.g. ?title). After the find clause comes the :where clause which restricts the query to datoms that match the given data patterns.

For example, this query finds all entity-ids that have the attribute :person/name with a value of "Ridley Scott":

[:find ?e
 :where
 [?e :person/name "Ridley Scott"]]

A data pattern is a datom with some parts replaced with pattern variables. It is the job of the query engine to figure out every possible value of each of the pattern variables and return the ones that are specified in the :find clause.

The symbol _ can be used as a wildcard for the parts of the data pattern that you wish to ignore. You can also elide trailing values in a data pattern. Therefore, the previous query is equivalent to this next query, because we ignore the transaction part of the datoms.

[:find ?e
 :where
 [?e :person/name "Ridley Scott" _]]

<< Previous chapter
Next chapter >>

    0
    1
    2

Find the entity ids of movies made in 1987

Query:[ I give up! ]

[:find ?e

 :where

 ...]



## Data patterns

In the previous chapter, we looked at data patterns, i.e., vectors after the :where clause, such as [?e :movie/title "Commando"]. There can be many data patterns in a :where clause:

[:find ?title
 :where
 [?e :movie/year 1987]
 [?e :movie/title ?title]]

The important thing to note here is that the pattern variable ?e is used in both data patterns. When a pattern variable is used in multiple places, the query engine requires it to be bound to the same value in each place. Therefore, this query will only find movie titles for movies made in 1987.

The order of the data patterns does not matter (aside from performance considerations), so the previous query could just as well have been written this way:

[:find ?title
 :where
 [?e :movie/title ?title]
 [?e :movie/year 1987]]

In both cases, the result set will be exactly the same.

Let's say we want to find out who starred in "Lethal Weapon". We will need three data patterns for this. The first one finds the entity ID of the movie with "Lethal Weapon" as the title:

[?m :movie/title "Lethal Weapon"]

Using the same entity ID at ?m, we can find the cast members with the data pattern:

[?m :movie/cast ?p] 

In this pattern, ?p will now be (the entity ID of) a person entity, so we can grab the actual name with:

[?p :person/name ?name] 

The query will therefore be:

[:find ?name
 :where
 [?m :movie/title "Lethal Weapon"]
 [?m :movie/cast ?p]
 [?p :person/name ?name]]

<< Previous chapter
Next chapter >>

    0
    1
    2
    3

Find movie titles made in 1985

Query:[ I give up! ]

[:find ?title

 :where

 ...]

## Parameterized queries

Looking at this query:

[:find ?title
 :where
 [?p :person/name "Sylvester Stallone"]
 [?m :movie/cast ?p]
 [?m :movie/title ?title]]

It would be great if we could reuse this query to find movie titles for any actor and not just for "Sylvester Stallone". This is possible with an :in clause, which provides the query with input parameters, much in the same way that function or method arguments does in your programming language.

Here's that query with an input parameter for the actor:

[:find ?title
 :in $ ?name
 :where
 [?p :person/name ?name]
 [?m :movie/cast ?p]
 [?m :movie/title ?title]]

This query takes two arguments: $ is the database itself (implicit, if no :in clause is specified) and ?name which presumably will be the name of some actor.

The above query is executed like (q query db "Sylvester Stallone"), where query is the query we just saw, and db is a database value. You can have any number of inputs to a query.

In the above query, the input pattern variable ?name is bound to a scalar - a string in this case. There are four different kinds of input: scalars, tuples, collections and relations.
A quick aside

Hold on. Where does that $ get used? In query, each of these data patterns is actually a 5 tuple, of the form:

[<database> <entity-id> <attribute> <value> <transaction-id>]

It's just that the database part is implicit, much like the first parameter in the :in clause. This query is functionally identical to the previous one:

[:find ?title
 :in $ ?name
 :where
 [$ ?p :person/name ?name]
 [$ ?m :movie/cast ?p]
 [$ ?m :movie/title ?title]]

Tuples

A tuple input is written as e.g. [?name ?age] and can be used when you want to destructure an input. Let's say you have the vector ["James Cameron" "Arnold Schwarzenegger"] and you want to use this as input to find all movies where these two people collaborated:

[:find ?title
 :in $ [?director ?actor]
 :where
 [?d :person/name ?director]
 [?a :person/name ?actor]
 [?m :movie/director ?d]
 [?m :movie/cast ?a]
 [?m :movie/title ?title]]

Of course, in this case, you could just as well use two distinct inputs instead:

:in $ ?director ?actor

Collections

You can use collection destructuring to implement a kind of logical or in your query. Say you want to find all movies directed by either James Cameron or Ridley Scott:

[:find ?title
 :in $ [?director ...]
 :where
 [?p :person/name ?director]
 [?m :movie/director ?p]
 [?m :movie/title ?title]]

Here, the ?director pattern variable is initially bound to both "James Cameron" and "Ridley Scott". Note that the ellipsis following ?director is a literal, not elided code.
Relations

Relations - a set of tuples - are the most interesting and powerful of input types, since you can join external relations with the datoms in your database.

As a simple example, let's consider a relation with tuples [movie-title box-office-earnings]:

[
 ...
 ["Die Hard" 140700000]
 ["Alien" 104931801]
 ["Lethal Weapon" 120207127]
 ["Commando" 57491000]
 ...
]

Let's use this data and the data in our database to find box office earnings for a particular director:

[:find ?title ?box-office
 :in $ ?director [[?title ?box-office]]
 :where
 [?p :person/name ?director]
 [?m :movie/director ?p]
 [?m :movie/title ?title]]

Note that the ?box-office pattern variable does not appear in any of the data patterns in the :where clause.
<< Previous chapter
Next chapter >>

    0
    1
    2
    3

Find movie title by year

Query:[ I give up! ]

[:find ?title

 :in $ ?year

 :where

 ...]

Input #1:

1988

 
## More queries

A datom, as described earlier, is the 4-tuple [eid attr val tx]. So far, we have only asked questions about values and/or entity-ids. It's important to remember that it's also possible to ask questions about attributes and transactions.
Attributes

For example, say we want to find all attributes that are associated with person entities in our database. We know for certain that :person/name is one such attribute, but are there others we have not yet seen?

[:find ?attr
 :where 
 [?p :person/name]
 [?p ?attr]]

The above query returns a set of entity ids referring to the attributes we are interested in. To get the actual keywords we need to look them up using the :db/ident attribute:

[:find ?attr
 :where
 [?p :person/name]
 [?p ?a]
 [?a :db/ident ?attr]]

This is because attributes are also entities in our database!
Transactions

It's also possible to run queries to find information about transactions, such as:

    When was a fact asserted?
    When was a fact retracted?
    Which facts were part of a transaction?
    Etc.

The transaction entity is the fourth element in the datom vector. The only attribute associated with a transaction (by default) is :db/txInstant which is the instant in time when the transaction was committed to the database.

Here's how we use the fourth element to find the time that "James Cameron" was set as the name for that person entity:

[:find ?timestamp
 :where
 [?p :person/name "James Cameron" ?tx]
 [?tx :db/txInstant ?timestamp]]
 

<< Previous chapter
Next chapter >>

    0
    1
    2
    3

What attributes are associated with a given movie.

Query:[ I give up! ]

[:find ?attr

 :in $ ?title

 :where

 ...]

Input #1:

"Commando"

 
## Predicates

So far, we have only been dealing with data patterns: [?m :movie/year ?year]. We have not yet seen a proper way of handling questions like "Find all movies released before 1984". This is where predicate clauses come into play.

Let's start with the query for the question above:

[:find ?title
 :where
 [?m :movie/title ?title]
 [?m :movie/year ?year]
 [(< ?year 1984)]]

The last clause, [(< ?year 1984)], is a predicate clause. The predicate clause filters the result set to only include results for which the predicate returns a "truthy" (non-nil, non-false) value. You can use any Clojure function or Java method as a predicate function:

[:find ?name
 :where 
 [?p :person/name ?name]
 [(.startsWith ?name "M")]]

Clojure functions must be fully namespace-qualified, so if you have defined your own predicate awesome? you must write it as (my.namespace/awesome? ?movie). Some ubiquitous predicates can be used without namespace qualification: <, >, <=, >=, =, not= and so on.
<< Previous chapter
Next chapter >>

    0
    1
    2

Find movies older than a certain year (inclusive)

Query:[ I give up! ]

[:find ?title ...

 ]

Input #1:

1979

 
## Transformation functions

Transformation functions are pure (= side-effect free) functions or methods which can be used in queries to transform values and bind their results to pattern variables. Say, for example, there exists an attribute :person/born with type :db.type/instant. Given the birthday, it's easy to calculate the (very approximate) age of a person:

(defn age [birthday today]
  (quot (- (.getTime today)
           (.getTime birthday))
        (* 1000 60 60 24 365)))

with this function, we can now calculate the age of a person inside the query itself:

[:find ?age
 :in $ ?name ?today
 :where
 [?p :person/name ?name]
 [?p :person/born ?born]
 [(tutorial.fns/age ?born ?today) ?age]]

A transformation function clause has the shape [(<fn> <arg1> <arg2> ...) <result-binding>] where <result-binding> can be the same binding forms as we saw in chapter 3:

    Scalar: ?age
    Tuple: [?foo ?bar ?baz]
    Collection: [?name ...]
    Relation: [[?title ?rating]]

One thing to be aware of is that transformation functions can't be nested. You can't write

[(f (g ?x)) ?a]

instead, you must bind intermediate results in temporary pattern variables

[(g ?x) ?t]
[(f ?t) ?a]

<< Previous chapter
Next chapter >>

    0
    1
    2

Find people by age. Use the function tutorial.fns/age to find the age given a birthday and a date representing "today".

Query:[ I give up! ]

[:find ?name

 :in $ ?age ?today

 :where

 ...]

Input #1:

63

 

Input #2:

#inst "2013-08-02T00:00:00.000-00:00"

 
## Aggregates

Aggregate functions such as sum, max etc. are readily available in Datomic's Datalog implementation. They are written in the :find clause in your query:

[:find (max ?date)
 :where
 ...]

An aggregate function collects values from multiple datoms and returns

    A single value: min, max, sum, avg, etc.
    A collection of values: (min n ?d) (max n ?d) (sample n ?e) etc. where n is an integer specifying the size of the collection.

<< Previous chapter
Next chapter >>

    0
    1
    2

count the number of movies in the database

Query:[ I give up! ]

[:find ...

 :where

 ...]

## Rules

Many times over the course of this tutorial, we have had to write the following three lines of repetitive query code:

[?p :person/name ?name]
[?m :movie/cast ?p]
[?m :movie/title ?title]

Rules are the means of abstraction in Datalog. You can abstract away reusable parts of your queries into rules, give them meaningful names and forget about the implementation details, just like you can with functions in your favorite programming language. Let's create a rule for the three lines above:

[(actor-movie ?name ?title)
 [?p :person/name ?name]
 [?m :movie/cast ?p]
 [?m :movie/title ?title]]

The first vector is called the head of the rule where the first symbol is the name of the rule. The rest of the rule is called the body.

It is possible to use (...) or [...] to enclose it, but it is conventional to use (...) to aid the eye when distinguishing between the rule's head and its body, and also between rule invocations and normal data patterns, as we'll see below.

You can think of a rule as a kind of function, but remember that this is logic programming, so we can use the same rule to:

    find movie titles given an actor name, and
    find actor names given a movie title.

Put another way, we can use both ?name and ?title in (actor-movie ?name ?title) for input as well as for output. If we provide values for neither, we'll get all the possible combinations in the database. If we provide values for one or both, it'll constrain the result returned by the query as you'd expect.

To use the above rule, you simply write the head of the rule instead of the data patterns. Any variable with values already bound will be input, the rest will be output.

The query to find cast members of some movie, for which we previously had to write:

[:find ?name
 :where
 [?p :person/name ?name]
 [?m :movie/cast ?p]
 [?m :movie/title "The Terminator"]]

Now becomes:

[:find ?name
 :in $ %
 (actor-movie ?name "The Terminator")]

The % symbol in the :in clause represent the rules. You can write any number of rules, collect them in a vector, and pass them to the query engine like any other input:

[[(rule-a ?a ?b)
  ...]
 [(rule-b ?a ?b)
  ...]
 ...]

You can use data patterns, predicates, transformation functions and calls to other rules in the body of a rule.

Rules can also be used as another tool to write logical OR queries, as the same rule name can be used several times:

[[(associated-with ?person ?movie)
  [?movie :movie/cast ?person]]
 [(associated-with ?person ?movie)
  [?movie :movie/director ?person]]]

Subsequent rule definitions will only be used if the ones preceding it aren't satisfied.

Using this rule, we can find both directors and cast members very easily:

[:find ?name
 :in $ %
 :where
 [?m :movie/title "Predator"]
 (associated-with ?p ?m)
 [?p :person/name ?name]]

Given the fact that rules can contain calls to other rules, what would happen if a rule called itself? Interesting things, it turns out, but let's find out in the exercises.
<< Previous chapter

    0
    1
    2

Write a rule [movie-year ?title ?year] where ?title is the title of some movie and ?year is that movies release year.

Query:[ I give up! ]

[:find ?title

 :in $ %

 :where

 [movie-year ?title 1991]]

Rules:

[[(movie-year ?title ?year) ...]]

 
