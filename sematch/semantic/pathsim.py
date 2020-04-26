from sematch.semantic.sparql import BaseSPARQL


class WikidataSPARQL(BaseSPARQL):
    """
    An interface for Wikidata.
    """

    INSTANCE_OF = 'http://www.wikidata.org/prop/direct/P31'

    def __init__(self, limit=5000):
        BaseSPARQL.__init__(self, url='https://query.wikidata.org/sparql', limit=limit)
        self._count_multiple_tpl = """SELECT (COUNT (DISTINCT *) AS ?count) WHERE 
        {{SELECT DISTINCT %s WHERE {\n\t%s\n}}} LIMIT """ + str(limit)

    def count_multiple_query(self, variables, triples):
        """
        Executes a COUNT query over multiple variables.
        """
        q_variables = map(lambda variable: self.q_mark(variable), variables)
        variables_string = ' '.join(q_variables)
        return self.execution_template('count', variables_string, triples, self._count_multiple_tpl)[0]

    def spo_triple(self, s, p, o):
        """
        A triple with no variables (subject, predicate, and object are known).
        """
        return self.triple(self.uri(s), self.uri(p), self.uri(o))

    def ensure_entity_type(self, entity, ensured_type):
        return self.spo_triple(entity, self.INSTANCE_OF, ensured_type)

    def ensure_variable_type(self, variable, ensured_type):
        return self.po_triple(self.INSTANCE_OF, ensured_type, variable)[1]


class PathSim:
    def __init__(self):
        self._sparql = WikidataSPARQL()

    def similarity(self, entity_1, entity_2, types, relations):
        count_1 = float(self._count_meta_path_instances(entity_1, entity_2, types, relations))
        count_2 = float(self._count_meta_path_instances(entity_1, entity_1, types, relations))
        count_3 = float(self._count_meta_path_instances(entity_2, entity_2, types, relations))
        return (2 * count_1) / (count_2 + count_3)

    def _count_meta_path_instances(self, entity_1, entity_2, types, relations):
        variables = ['v%d' % i for i in xrange(len(relations) * 2 - 1)]
        triples = []
        # Types
        triples.append(self._sparql.ensure_entity_type(entity_1, types[0]))
        triples.append(self._sparql.ensure_entity_type(entity_2, types[0]))
        for i in xrange(1, len(types)):
            triples.append(self._sparql.ensure_variable_type(variables[i-1], types[i]))
            triples.append(self._sparql.ensure_variable_type(variables[-i], types[i]))
        # Relations/predicates
        triples.append(self._sparql.sp_triple(entity_1, relations[0], variables[0])[1])
        triples.append(self._sparql.sp_triple(entity_2, relations[0], variables[-1])[1])
        for i in xrange(1, len(relations)):
            triples.append(self._sparql.p_triple(variables[i - 1], relations[i], variables[i]))
            triples.append(self._sparql.p_triple(variables[-i], relations[i], variables[-1 - i]))
        return self._sparql.count_multiple_query(variables, ''.join(triples))
