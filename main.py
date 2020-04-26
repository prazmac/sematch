from sematch.semantic.pathsim import PathSim

ps = PathSim()

# print ps.similarity('http://www.wikidata.org/entity/Q165325', 'http://www.wikidata.org/entity/Q928019',
#                     ['http://www.wikidata.org/entity/Q11424',
#                      'http://www.wikidata.org/entity/Q5',
#                      'http://www.wikidata.org/entity/Q6256'],
#                     ['http://www.wikidata.org/prop/direct/P161',
#                      'http://www.wikidata.org/prop/direct/P27'])

print ps.similarity('http://www.wikidata.org/entity/Q165325', 'http://www.wikidata.org/entity/Q928019',
                    ['http://www.wikidata.org/entity/Q11424',
                     'http://www.wikidata.org/entity/Q5'],
                    ['http://www.wikidata.org/prop/direct/P161'])
