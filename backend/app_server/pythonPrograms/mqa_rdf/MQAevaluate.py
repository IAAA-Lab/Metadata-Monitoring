"""
mqa/MQAevaluate.py
Author: Javier Nogueras (jnog@unizar.es), Javier Lacasta (jlacasta@unizar.es), Manuel Ureña (maurena@ujaen.es), F. Javier Ariza (fjariza@ujaen.es)
Last update: 2020-11-11

Evaluation of catalog RDF DCAT-AP metadata according to Metadata Quality Assessment methodology (https://www.europeandataportal.eu/mqa/methodology?locale=en)
"""

import urllib.request
from pyshacl import validate
import rdflib

FINDABILITY = 'Findability'

ACCESIBILITY = 'Accesibility'

INTEROPERABILITY = 'Interoperability'

REUSABILITY = 'Reusability'

CONTEXTUALITY = 'Contextuality'

DISTRIBUTION = 'dcat:Distribution'

DATASET = 'dcat:Dataset'

CODE_200 = ' code=200'

FROM_VOCABULARY = ' from vocabulary'

TIMEOUT = 15

CKAN = 'ckan'

EDP = 'edp'

NTI = 'nti'

SHAPESFILE = 'dcat-ap.shapes.ttl'

def make_request(url):
    request = urllib.request.Request(url)
    # Make the HTTP request.
    response = urllib.request.urlopen(request, timeout = TIMEOUT )
    assert 200 <= response.code < 400

def load_vocabulary(vocabulary_file, field = 0):
    vocabulary = []
    with open(vocabulary_file) as fp:
        for line in fp:
            words = line.strip().split(',')
            if len(words) > field:
                if words[field] != '':
                    vocabulary.append(words[field])
    return vocabulary

def contains_vocabulary_word(vocabulary, word):
    for value in vocabulary:
        if value.lower().find(word.lower()) >= 0:
            # print (value, word)
            return True
    return False

def contains_word_vocabulary(vocabulary, word):
    for value in vocabulary:
        if word.lower().find(value.lower()) >= 0:
            return True
    return False


class MQAevaluate:

    def __init__(self, catalog_rdf_file, shapes_turtle_file = SHAPESFILE, catalog_format = 'application/rdf+xml', catalog_type = CKAN):
        self.catalog = catalog_rdf_file
        self.shapes = shapes_turtle_file
        self.graph = rdflib.Graph()
        self.graph.parse(source=self.catalog, format = catalog_format) #jnog
        self.datasetCount = self.count_entities(DATASET)
        self.distributionCount = self.count_entities(DISTRIBUTION)
        self.totalPoints = 0
        self.catalog_type = catalog_type
        self.results_file = open(catalog_rdf_file+'_results.txt', 'w')

    def shacl(self):
        '''
        https://github.com/RDFLib/pySHACL
        More information about SHACL at https://www.w3.org/TR/shacl/
        Shapes file adapted from https://github.com/SEMICeu/dcat-ap_shacl/blob/master/shacl/dcat-ap.shapes.ttl
        Original shape constraint file does not include sh:targetClass and does not verify anything.
        The following target class was included:
          sh:targetClass dcat:Dataset ;
        '''
        sg = rdflib.Graph()
        sg.parse(source=self.shapes, format='turtle')

        try:
            r = validate(self.graph, shacl_graph=sg, inference='rdfs', abort_on_first=True)
            conforms, results_graph, results_text = r
            if not conforms:
                error_file_name = self.catalog+ '_errors_SHACL.txt'
                with open(error_file_name, "w", encoding="utf-8") as text_file:
                    text_file.write(results_text)
            return conforms
        except Exception as err:
            print(f'Exception occurred: {err}')
            return False

    def count_entities(self, entity):
        qres = self.graph.query("""
                   PREFIX dct:<http://purl.org/dc/terms/>
                   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX dcat: <http://www.w3.org/ns/dcat#>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT  (count(DISTINCT ?resource) as ?values)  WHERE {
                        ?resource rdf:type """+ entity +""" .
                    }
                    """)
        for row in qres:
            count = int(row["values"])
        return count

    def count_entity_property(self, entity, property):
        qres = self.graph.query("""
                   PREFIX dct:<http://purl.org/dc/terms/>
                   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX dcat: <http://www.w3.org/ns/dcat#>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT  (count(DISTINCT ?resource) as ?values)  WHERE {
                        ?resource rdf:type """+ entity + """ .
        	            ?resource """ + property +""" ?value .
                    }
                    """)
        for row in qres:
            count = int(row["values"])
        return count

    def count_edp_formats_from_vocabulary(self, vocabulary):
        '''
        The format returned by EDP is a URL, the last token of the URL is the label of the format, e.g. http://publications.europa.eu/resource/authority/file-type/XML
        '''
        qres = self.graph.query("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            SELECT ?value (COUNT(?value) as ?count)
            WHERE {
                ?resource a dcat:Distribution .
                ?resource dct:format ?value .
            }
            GROUP BY ?value
            """)
        count = 0
        for row in qres:
            format = row["value"]
            words = format.strip().split('/')
            if len(words) > 0:
                format_label = words[len(words)-1]
                partialCount = int(row["count"])
                # print('Recognised format: ', format_label, partialCount)
                if contains_vocabulary_word(vocabulary,format_label):
                    count += partialCount
        return count

    def count_nti_formats_from_vocabulary(self, vocabulary):
        '''
        The format returned by NTI models is a dct:IMT
        '''
        qres = self.graph.query("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            SELECT ?value (COUNT(?value) as ?count)
            WHERE {
                ?resource a dcat:Distribution .
                ?resource dct:format ?format .
                ?format rdfs:label ?value .
            }
            GROUP BY ?value
            """)
        count = 0
        for row in qres:
            format = row["value"]
            words = format.strip().split('/')
            if len(words) > 0:
                format_label = words[len(words)-1]
                partialCount = int(row["count"])
                # print('Recognised format: ', format_label, partialCount)
                if contains_vocabulary_word(vocabulary,format_label):
                    count += partialCount
        return count

    def count_values_contained_in_vocabulary(self, entity, property, vocabulary):
        qres = self.graph.query("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            SELECT ?value (COUNT(?value) as ?count)
            WHERE {
                ?resource a """ + entity + """ .
                ?resource """ + property + """ ?value .
            }
            GROUP BY ?value
            """)
        count = 0
        for row in qres:
            format = row["value"]
            partialCount = int(row["count"])
            #if contains_exact(vocabulary,format):
            if contains_vocabulary_word(vocabulary, format):
                    count += partialCount
        return count

    def count_values_containing_vocabulary(self, entity, property, vocabulary):
        qres = self.graph.query("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            SELECT ?value (COUNT(?value) as ?count)
            WHERE {
                ?resource a """ + entity + """ .
                ?resource """ + property + """ ?value .
            }
            GROUP BY ?value
            """)
        count = 0
        for row in qres:
            license = row["value"]
            partialCount = int(row["count"])
            # print(license, partialCount)
            if contains_word_vocabulary(vocabulary, license):
                count += partialCount
        return count

    def count_urls_with_200_code(self, property):
        qres = self.graph.query("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            SELECT ?value (COUNT(?value) as ?count)
            WHERE {
                ?resource a dcat:Distribution .
                ?resource """+ property+""" ?value
            }
            GROUP BY ?value
            """)
        count = 0

        error_file_name = self.catalog + '_errors_'+property.replace(":","_") + ".txt"
        with open(error_file_name, "w", encoding="utf-8") as text_file:
            for row in qres:
                url = row["value"]
                partialCount = int(row["count"])
                try:
                    make_request(url)
                    count += partialCount
                except:
                    text_file.write(url + '\t' + str(partialCount) + '\n')
                    #print(url + " not reached")
        return count

    def print(self, dimension, property, count, population, weight):
        if population > 0:
            percentage = count / population
        else:
            percentage = 0
        if count > 0:
            partialPoints = percentage * weight
            self.totalPoints += partialPoints
        else:
            partialPoints = 0
        self.results_file.write(dimension + "\t" + property + "\t" + str(count) + "\t" + str(population) + "\t" + str(percentage) + "\t" + str(partialPoints) + "\t" + str(weight)+"\n")

    def findability_keywords_available(self):
        dimension = FINDABILITY
        entity = DATASET
        property = 'dcat:keyword'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 30)

    def findability_category_available(self):
        dimension = FINDABILITY
        entity = DATASET
        property = 'dcat:theme'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 30)

    def findability_spatial_available(self):
        dimension = FINDABILITY
        entity = DATASET
        property = 'dct:spatial'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 20)

    def findability_temporal_available(self):
        dimension = FINDABILITY
        entity = DATASET
        property = 'dct:temporal'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 20)

    def accesibility_accessURL_code_200(self):
        dimension = ACCESIBILITY
        entity = DISTRIBUTION
        property = 'dcat:accessURL'
        count = self.count_urls_with_200_code(property)
        population = self.distributionCount
        self.print(dimension, property + CODE_200, count, population, 50)

    def accesibility_downloadURL_available(self):
        dimension = ACCESIBILITY
        entity = DISTRIBUTION
        property = 'dcat:downloadURL'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 20)

    def accesibility_downloadURL_code_200(self):
        dimension = ACCESIBILITY
        entity = DISTRIBUTION
        property = 'dcat:downloadURL'
        count = self.count_urls_with_200_code(property)
        population = self.distributionCount
        self.print(dimension, property + CODE_200, count, population, 30)

    def interoperability_format_available(self):
        dimension = INTEROPERABILITY
        entity = DISTRIBUTION
        property = 'dct:format'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 20)

    def interoperability_mediaType_available(self):
        dimension = INTEROPERABILITY
        entity = DISTRIBUTION
        property = 'dcat:mediaType'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 10)

    def interoperability_format_from_vocabulary(self):
        '''
        https://www.iana.org/assignments/media-types/media-types.xhtml
        '''
        dimension = INTEROPERABILITY
        entity = DISTRIBUTION
        property = 'dct:format'
        vocabulary = load_vocabulary('IMTvalues.csv',1)
        if self.catalog_type == CKAN:
            count = self.count_values_contained_in_vocabulary(entity,property,vocabulary)
        else:
            if self.catalog_type == EDP:
                count = self.count_edp_formats_from_vocabulary(vocabulary)
            else:
                #NTI
                count = self.count_nti_formats_from_vocabulary(vocabulary)
        population = self.distributionCount
        self.print(dimension, property + FROM_VOCABULARY, count, population, 10)

    def interoperability_format_nonProprietary(self):
        '''
        https://gitlab.com/european-data-portal/edp-vocabularies/-/blob/master/Custom%20Vocabularies/edp-non-proprietary-format.rdf
        '''
        dimension = INTEROPERABILITY
        entity = DISTRIBUTION
        property = 'dct:format'
        vocabulary = load_vocabulary('non-proprietary.csv',1)
        if self.catalog_type == CKAN:
            count = self.count_values_contained_in_vocabulary(entity,property,vocabulary)
        else:
            if self.catalog_type == EDP:
                count = self.count_edp_formats_from_vocabulary(vocabulary)
            else:
                #NTI
                count = self.count_nti_formats_from_vocabulary(vocabulary)
        population = self.distributionCount
        self.print(dimension, property + ' non-proprietary', count, population, 20)

    def interoperability_format_machineReadable(self):
        '''
        https://gitlab.com/european-data-portal/edp-vocabularies/-/blob/master/Custom%20Vocabularies/edp-machine-readable-format.rdf
        '''
        dimension = INTEROPERABILITY
        entity = DISTRIBUTION
        property = 'dct:format'
        vocabulary = load_vocabulary('machine-readable.csv',1)
        if self.catalog_type == CKAN:
            count = self.count_values_contained_in_vocabulary(entity,property,vocabulary)
        else:
            if self.catalog_type == EDP:
                count = self.count_edp_formats_from_vocabulary(vocabulary)
            else:
                #NTI
                count = self.count_nti_formats_from_vocabulary(vocabulary)
        population = self.distributionCount
        self.print(dimension, property + ' machine-readable', count, population, 20)

    def interoperability_DCAT_AP_compliance(self):
        dimension = INTEROPERABILITY
        entity = DATASET
        property = 'dct:format'
        if self.catalog is not None and self.shapes is not None:
            conforms = self.shacl()
            if conforms:
                count = self.datasetCount
            else:
                count = 0
        else:
            count = -1
        population = self.datasetCount
        self.print(dimension, 'DCAT-AP compliance', count, population, 30)

    def reusability_license_available(self):
        dimension = REUSABILITY
        entity = DISTRIBUTION
        property = 'dct:license'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 20)

    def reusability_license_from_vocabulary(self):
        '''
        https://gitlab.com/european-data-portal/edp-vocabularies/-/blob/master/Custom%20Vocabularies/edp-licences-skos.rdf
        '''
        dimension = REUSABILITY
        entity = DISTRIBUTION
        property = 'dct:license'
        vocabulary = load_vocabulary('licenses.csv')
        count = self.count_values_containing_vocabulary(entity,property,vocabulary)
        population = self.distributionCount
        self.print(dimension, property + FROM_VOCABULARY, count, population, 10)

    def reusability_accessRights_available(self):
        dimension = REUSABILITY
        entity = DATASET
        property = 'dct:accessRights'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 10)

    def reusability_accessRights_from_vocabulary(self):
        '''
        https://gitlab.com/european-data-portal/edp-vocabularies/-/blob/master/EU%20Vocabularies/access-right-skos.rdf
        '''
        dimension = REUSABILITY
        entity = DATASET
        property = 'dct:accessRights'
        vocabulary = load_vocabulary('access-right.csv',1)
        count = self.count_values_contained_in_vocabulary(entity,property,vocabulary)
        population = self.datasetCount
        self.print(dimension, property + FROM_VOCABULARY, count, population, 5)

    def reusability_contactPoint_available(self):
        dimension = REUSABILITY
        entity = DATASET
        property = 'dcat:contactPoint'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 20)

    def reusability_publisher_available(self):
        dimension = REUSABILITY
        entity = DATASET
        property = 'dct:publisher'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 10)

    def contextuality_rights_available(self):
        dimension = CONTEXTUALITY
        entity = DISTRIBUTION
        property = 'dct:rights'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 5)

    def contextuality_fileSize_available(self):
        dimension = CONTEXTUALITY
        entity = DISTRIBUTION
        property = 'dcat:byteSize'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 5)

    def contextuality_issued_available(self):
        dimension = CONTEXTUALITY
        entity = DATASET
        property = 'dct:issued'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 5)

    def contextuality_modified_available(self):
        dimension = CONTEXTUALITY
        entity = DATASET
        property = 'dct:modified'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 5)

    def evaluate(self):
        self.results_file.write("Dimension\tIndicator/property\tCount\tPopulation\tPercentage\tPoints\tWeight\n")
        self.findability_keywords_available()
        self.findability_category_available()
        self.findability_spatial_available()
        self.findability_temporal_available()
        # self.accesibility_accessURL_code_200()
        # self.accesibility_downloadURL_available()
        # self.accesibility_downloadURL_code_200()
        self.interoperability_format_available()
        self.interoperability_mediaType_available()
        self.interoperability_format_from_vocabulary()
        self.interoperability_format_nonProprietary()
        self.interoperability_format_machineReadable()
        self.interoperability_DCAT_AP_compliance()
        self.reusability_license_available()
        self.reusability_license_from_vocabulary()
        self.reusability_accessRights_available()
        self.reusability_accessRights_from_vocabulary()
        self.reusability_contactPoint_available()
        self.reusability_publisher_available()
        self.contextuality_rights_available()
        self.contextuality_fileSize_available()
        self.contextuality_issued_available()
        self.contextuality_modified_available()
        self.results_file.write("Total points\t"+ str(self.totalPoints)+'\n')
        self.results_file.close()
