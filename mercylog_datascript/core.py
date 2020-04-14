# from typing import *

# WhereList = List[List]

SPACE = ' '


class Variable(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def code(self):
        return "?" + self.name


class AggregateFunction(object):
    # name: str
    # args: Tuple[Variable] = field(default_factory=tuple)

    def __init__(self, name, args=None):
        self.name = name
        self.args = args or tuple()

    def __call__(self, *args, **kwargs):
        self.args = args
        return self

    def code(self):
        _code = spacify([self.name, self.args[0].code()])
        return listify(_code)


# Findable = Union[Variable, AggregateFunction]


class UnderScoreVariable(object):
    # name: str = "_"

    def __init__(self):
        self.name = "_"

    def __str__(self):
        return self.name

    def code(self):
        return str(self.name)


class DatabaseVariable(Variable):
    # TODO: Same as Underscore variable. Use MetaClass?
    # name: str = "$"

    def __init__(self):
        self.name = "$"
        super(DatabaseVariable, self).__init__(self.name)

    def __str__(self):
        return self.name

    def code(self):
        # TODO: Do we need to to str()
        return str(self.name)


class RuleVariable(Variable):
    # TODO: Same as Underscore variable. Use MetaClass?
    # name: str = "%"

    def __init__(self):
        self.name = "%"
        super(RuleVariable, self).__init__(self.name)

    def __str__(self):
        return self.name

    def code(self):
        # TODO: Do we need to to str()
        return str(self.name)


class AnyParameter(object):

    def __init__(self, variable):
        self.variable = variable

    def __str__(self):
        return self.variable

    def code(self):
        # TODO: Do we need to to str()
        # [?name ...]
        return '[' + self.variable.code() + ' ...]'


class CollectionParameter(object):

    def __init__(self, variables):
        self.variables = variables
        pass

    def __str__(self):
        return self.variables

    def code(self):
        mapped_vars = map(lambda x: x.code(), self.variables)
        return '[[' + spacify(mapped_vars) + ']]'


class Query(object):

    def __init__(self, find, where, parameters):
        self.find = find
        self.where = where
        self.parameters = parameters

    def code(self):
        vars = self.to_code(self.find)

        spaced_vars = spacify(vars)
        find_str = ':find ' + spaced_vars

        where_str_list = map(lambda a_l: translate_where(a_l), self.where)
        where_str = spacify(where_str_list)
        parameter_str = self.make_parameter_str(self.parameters, self.where)

        return f"[{find_str} {parameter_str}:where {where_str}]"
        pass

    def make_parameter_str(self, parameters, where):

        all_parameters = []

        if parameters or relation_in_where(where):
            all_parameters.append(DatabaseVariable())

        if relation_in_where(where):
            all_parameters.append(RuleVariable())

        if parameters:
            all_parameters.extend(parameters)

        if all_parameters:
            parameter_str = spacify([":in"] + list(self.to_code(all_parameters))) + SPACE
        else:
            parameter_str = ''
        return parameter_str

    @staticmethod
    def to_code(var_list):
        return findables_to_code(var_list)


def relation_in_where(where):
    is_rule = map(lambda x: isinstance(x, Relation), where)
    return any(is_rule)


def findables_to_code(var_list):
    # TODO: Duplicate
    result = []
    for r in var_list:
        if hasattr(r, 'code'):
            result.append(r.code())
        elif isinstance(r, str):
            result.append(f'"{r}"')
        else:
            result.append(str(r))
    return result


def spacify(code):
    return SPACE.join(code)


# def codify(atom) -> str:
#     if isinstance(atom, Variable) or isinstance(atom, UnderScoreVariable) or isinstance(atom, Relation):
#         return atom.code()
#     elif isinstance(atom, str):
#         return f'"{atom}"'
#     else:
#         return str(atom)

def codify(atom):
    if isinstance(atom, Variable) or isinstance(atom, UnderScoreVariable) or isinstance(atom, Relation):
        return atom.code()
    elif isinstance(atom, str):
        return f'"{atom}"'
    else:
        return str(atom)


class RelationalFunction(object):
    def __init__(self, name, function=None, variables=None):
        self.name = name
        self.function = function
        self.variables = list()

    def __call__(self, *variables):
        # return self.function(*terms, **kwargs)
        self.variables = list(variables)
        return self

    def __str__(self):
        # TODO: is this duplicate, the lisp brackets
        var_str = findables_to_code(self.variables)
        _code = spacify([self.code(), spacify(var_str)])
        r = listify(_code)
        return r

    def code(self):
        if self.function:
            return "?" + self.name
        else:
            return self.name


class Aggregate:
    def __init__(self):
        pass

    def __getattr__(self, name):
        return AggregateFunction(name)


class DataScriptFunction:

    def __init__(self, var_name, function_name):
        self.var_name = var_name
        self.function_name = function_name
        self.terms = tuple()

    def __call__(self, *args, **kwargs):
        self.terms = args
        return self
        pass

    def str(self):
        return self.code()

    def code(self):
        # TOOD: Duplicate of Relation code()
        mapped_vars = []
        for t in self.terms:
            if isinstance(t, Variable):
                mapped_vars.append(t.code())
            else:
                mapped_vars.append(f'"{t}"')

        _code = spacify([self.function_name, self.var_name, spacify(mapped_vars)])
        return listify(_code)


class Var:
    def __init__(self, name):
        self.name = name
        pass

    def __getattr__(self, name):
        return DataScriptFunction(self.code(), name)

    def code(self):
        return "?" + self.name


class InvertedRelationInstance(object):
    def __init__(self, relation_instance):
        self.relation_instance = relation_instance
        pass

    def get_clause(self):
        return "not " + self.relation_instance.get_clause()

    def relation(self):
        return self.get_clause()

    def variables(self):
        return self.relation_instance.variables()


class Facts(object):
    def __init__(self, *fact_list):
        self.fact_list = fact_list

    def get_clause(self):
        fact_list_str = [f.relation() for f in self.fact_list]
        return ', '.join(fact_list_str)

    pass


class Fact(object):
    def __init__(self, terms):
        self.terms = terms


class Rule(object):
    def __init__(self, head_atom, body_atoms):
        self.head_atom = head_atom
        self.body_atoms = body_atoms
        pass

    def relation(self):
        if self.body_atoms:
            mid_fragment = ' :- ' + str(self.body_atoms)
        else:
            mid_fragment = ''

        result = self.head_atom.relation() + mid_fragment
        return result

    def get_clause(self):
        if self.body_atoms:
            mid_fragment = ' :- ' + self.body_atoms.get_clause()
        else:
            mid_fragment = ''

        return self.head_atom.relation() + mid_fragment


class RelationInstance(object):
    def __init__(self, name, *variables):
        self.name = name
        self._variables = variables

    def __le__(self, body):
        if isinstance(body, list):
            b = Facts(*body)
        else:
            b = body
        return Rule(self, b)

    def variables(self):
        return self._variables

    def get_clause(self):
        return self.relation_x()

    def relation_x(self):
        var_strs = []
        # TODO: Duplicate isinstance check
        for v in self.variables():
            if isinstance(v, str):
                x = f'"{v}"'
            else:
                x = str(v)

            var_strs.append(x)
        a_str = ','.join(var_strs)
        return self.name + listify(a_str)

    def relation(self):
        return self.relation_x()

    def __invert__(self):
        return InvertedRelationInstance(self)
        pass


class Relation(object):
    def __init__(self, name):
        self._name = name
        self.terms = tuple()

    def name(self):
        return self._name

    def __call__(self, *variables):
        self.terms = variables
        return self

    def code(self):
        mapped_vars = []
        for t in self.terms:
            if isinstance(t, Variable):
                mapped_vars.append(t.code())
            else:
                mapped_vars.append(f'"{t}"')

        _code = spacify([self.name(), spacify(mapped_vars)])

        return listify(_code)


# WhereClause = Union[List, Relation]


# TODO: Curry all functions?
class DataScriptV1(object):
    _ = UnderScoreVariable()
    DB = DatabaseVariable()
    agg = Aggregate()
    RULE = RuleVariable()

    @staticmethod
    def function(name, func=None):
        return RelationalFunction(name=name, function=func)

    @staticmethod
    def relation(name):
        return Relation(name)

    @staticmethod
    def rule(head, body):
        return Rule(head, body)

    @staticmethod
    def any(v):
        return AnyParameter(v)
        pass

    @staticmethod
    def collection(vars):
        return CollectionParameter(vars)
        pass

    @staticmethod
    def variables(*vars):
        # TODO: Duplicate with bashlog
        result = [Variable(v) for v in vars]
        if len(result) == 1:
            return result[0]
        else:
            return result

    def query(self, find, where, parameters=None):
        parameters = parameters or []
        return Query(find=find, where=where, parameters=parameters)


# def translate_where(where_clause):
#     if isinstance(where_clause, Relation):
#         result = where_clause.code()
#     else:
#         result = map(codify, where_clause)
#         result = '[' + spacify(result) + ']'
#
#     return result

def translate_where(where_clause):
    if isinstance(where_clause, Relation):
        result = where_clause.code()
    elif isinstance(where_clause, RelationalFunction):
        result = where_clause.code()
    else:
        result = map(codify, where_clause)
        result = '[' + spacify(result) + ']'

    return result


def listify(code):
    return '(' + code + ')'
