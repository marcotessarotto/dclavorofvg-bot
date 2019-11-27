#
# import pysolr
#
# # Create a client instance. The timeout and authentication options are not required.
# solr = pysolr.Solr('http://10.4.100.2:8983/solr/bot_core/', always_commit=True)
#
# # Note that auto_commit defaults to False for performance. You can set
# # `auto_commit=True` to have commands always update the index immediately, make
# # an update call with `commit=True`, or use Solr's `autoCommit` / `commitWithin`
# # to have your data be committed following a particular policy.
#
#
# print(solr.get_session())
#
# # Do a health check.
# # solr.results_cls.ping()
#
#
# results = solr.search('', {
#             'q':'categoriaProfessionale:*',
#             'facet':True,
#             'facet.field':'categoriaProfessionale',
#     })
#
# print("Saw {0} result(s).".format(len(results)))



from SolrClient import SolrClient


solr = SolrClient('http://10.4.100.2:8983/solr')
res = solr.query('bot_core',{
            'q' : 'categoriaProfessionale:*',
            'facet' : True,
            'facet.field' : 'categoriaProfessionale',
    })

print(res)

print(res.get_results_count())

dict = res.get_facets()

print(dict)

od = dict['categoriaProfessionale']

words_to_be_removed = ('ed', 'e', 'alla', 'varie')

for w in words_to_be_removed:
    od.pop(w)

for k,v in od.items():
    print(f"{k}={v}\n")



# {'facet_test': {'ipsum': 0, 'sit': 0, 'dolor': 2, 'amet,': 1, 'Lorem': 1}}
# print(res.get_facet_keys_as_list('facet_test'))
# ['ipsum', 'sit', 'dolor', 'amet,', 'Lorem']
print(res.docs)


print("ok finished")