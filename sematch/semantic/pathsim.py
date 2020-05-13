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
        self._ask_tpl = """ASK {\n\t%s\n}"""

    def count_multiple_query(self, variables, triples, show_query=False):
        """
        Executes a COUNT query over multiple variables.
        """
        q_variables = map(lambda variable: self.q_mark(variable), variables)
        variables_string = ' '.join(q_variables)
        return self.execution_template('count', variables_string, triples, self._count_multiple_tpl, show_query)[0]

    def ask_query(self, triples, show_query=False):
        """
        Executes an ASK query.
        """
        query = self._ask_tpl % triples
        if show_query:
            print(query)
        self._sparql.setQuery(query)
        results = self._sparql.query().convert()
        return results['boolean']

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
        directed_relations = []
        for i in xrange(0, len(relations)):
            directed_relations.append(self._find_relation_direction(relations[i], types[i], types[i + 1]))
        count_1 = float(self._count_meta_path_instances(entity_1, entity_2, types, directed_relations))
        count_2 = float(self._count_meta_path_instances(entity_1, entity_1, types, directed_relations))
        count_3 = float(self._count_meta_path_instances(entity_2, entity_2, types, directed_relations))
        if count_2 + count_3 <= 0.0:
            return None
        else:
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
        if not relations[0]['reverse']:
            triples.append(self._sparql.sp_triple(entity_1, relations[0]['iri'], variables[0])[1])
            triples.append(self._sparql.sp_triple(entity_2, relations[0]['iri'], variables[-1])[1])
        else:
            triples.append(self._sparql.po_triple(relations[0]['iri'], entity_1, variables[0])[1])
            triples.append(self._sparql.po_triple(relations[0]['iri'], entity_2, variables[-1])[1])
        for i in xrange(1, len(relations)):
            if not relations[i]['reverse']:
                triples.append(self._sparql.p_triple(variables[i - 1], relations[i]['iri'], variables[i]))
                triples.append(self._sparql.p_triple(variables[-i], relations[i]['iri'], variables[-1 - i]))
            else:
                triples.append(self._sparql.p_triple(variables[i], relations[i]['iri'], variables[i - 1]))
                triples.append(self._sparql.p_triple(variables[-1 - i], relations[i]['iri'], variables[-i]))
        return self._sparql.count_multiple_query(variables, ''.join(triples))

    def _find_relation_direction(self, relation, type_1, type_2):
        triples = [self._sparql.ensure_variable_type('v1', type_1),
                   self._sparql.ensure_variable_type('v2', type_2),
                   self._sparql.p_triple('v1', relation, 'v2')]
        return {'iri': relation, 'reverse': not self._sparql.ask_query(''.join(triples))}
