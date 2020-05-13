from sematch.semantic.pathsim import PathSim

ps = PathSim()

# # human-country-human, country of citizenship
# print ps.similarity('http://www.wikidata.org/entity/Q3772', 'http://www.wikidata.org/entity/Q8877',
#                     ['http://www.wikidata.org/entity/Q5',
#                      'http://www.wikidata.org/entity/Q6256'],
#                     ['http://www.wikidata.org/prop/direct/P27'])

# country-human-country, country of citizenship
print ps.similarity('http://www.wikidata.org/entity/Q30', 'http://www.wikidata.org/entity/Q17',
                    ['http://www.wikidata.org/entity/Q6256',
                     'http://www.wikidata.org/entity/Q5'],
                    ['http://www.wikidata.org/prop/direct/P27'])

