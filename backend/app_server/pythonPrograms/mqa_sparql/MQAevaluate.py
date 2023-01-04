"""
evaluate.py
Author: Javier Nogueras (jnog@unizar.es), Javier Lacasta (jlacasta@unizar.es), Manuel Ureña (maurena@ujaen.es), F. Javier Ariza (fjariza@ujaen.es)
Last update: 2020-04-22

Evaluation of catalog RDF DCAT-AP metadata according to Metadata Quality Assessment methodology (https://www.europeandataportal.eu/mqa/methodology?locale=en)
"""

from SPARQLWrapper import SPARQLWrapper, JSON
import urllib.request
from pyshacl import validate
import rdflib
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import FOAF, RDF, DCTERMS, SKOS


FINDABILITY = 'Findability'

ACCESIBILITY = 'Accesibility'

INTEROPERABILITY = 'Interoperability'

REUSABILITY = 'Reusability'

CONTEXTUALITY = 'Contextuality'

DISTRIBUTION = 'dcat:Distribution'

DATASET = 'dcat:Dataset'

CODE_200 = ' code=200'

FROM_VOCABULARY = ' from vocabulary'

TIMEOUT = 5

DCAT = 'http://www.w3.org/ns/dcat#'
DQV = 'http://www.w3.org/ns/dqv#'
DCT = 'http://purl.org/dc/terms/'
PROV = 'http://www.w3.org/ns/prov#'
PROV = 'http://www.w3.org/ns/prov#'
XSD = 'http://www.w3.org/2001/XMLSchema#'
QR = 'http://www.qualityreport.com/qr/'

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

def exact(vocabulary, word):
    for value in vocabulary:
        if value == word:
            return True
    return False

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

    def __init__(self, url, user = None, passwd = None, catalog_rdf_file = None, shapes_turtle_file = None,
                 filename = None, date = None):

        self.sparql = SPARQLWrapper(url)
        if user is not None:
            self.sparql.setCredentials(user, passwd)
        self.catalog = catalog_rdf_file
        self.shapes = shapes_turtle_file
        self.datasetCount = self.count_entities(DATASET)
        self.distributionCount = self.count_entities(DISTRIBUTION)
        self.totalPoints = 0

        self.filename = filename
        self.date = date
        # Initialize a graph
        self.graph = Graph()
        # Load definitions from file
        self.graph.parse('../DQV_files/templates/MQA_definitions.ttl', format='turtle')

    def shacl(self):
        '''
        https://github.com/RDFLib/pySHACL
        More inormation about SHACL at https://www.w3.org/TR/shacl/
        Shapes file adapted from https://github.com/SEMICeu/dcat-ap_shacl/blob/master/shacl/dcat-ap.shapes.ttl
        Original shapefile does not include sh:targetClass and does not verify anything.
        The following target class was included:
          sh:targetClass dcat:Dataset ;
        '''
        sg = rdflib.Graph()
        sg.parse(source=self.shapes, format='turtle')
        data_graph = rdflib.Graph()
        data_graph.load(self.catalog)
        # data_graph.parse(source = catalog, format = 'turtle')

        r = validate(data_graph, shacl_graph=sg, inference='rdfs', abort_on_error=True)
        conforms, results_graph, results_text = r
        # print(conforms)
        # print(results_graph)
        # print(results_text)
        return conforms

    def count_entities(self, entity):
        self.sparql.setQuery("""
                   PREFIX dct:<http://purl.org/dc/terms/>
                   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX dcat: <http://www.w3.org/ns/dcat#>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT  (count(DISTINCT ?resource) as ?values)  WHERE {
                        ?resource rdf:type """+ entity +""" .
                    }
                    """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for row in results["results"]["bindings"]:
            """values"""
            count = int(row["values"]["value"])
        return count

    def count_entity_property(self, entity, property):
        self.sparql.setQuery("""
                   PREFIX dct:<http://purl.org/dc/terms/>
                   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX dcat: <http://www.w3.org/ns/dcat#>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT  (count(DISTINCT ?resource) as ?values)  WHERE {
                        ?resource rdf:type """+ entity + """ .
        	            ?resource """ + property +""" ?value .
                    }
                    """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for row in results["results"]["bindings"]:
            """values"""
            count = int(row["values"]["value"])
        return count

    def count_formats_from_vocabulary(self, vocabulary):
        self.sparql.setQuery("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            SELECT ?value (COUNT(?value) as ?count)
            WHERE {
                ?resource a dcat:Distribution .
                ?resource dct:format ?IMT .
                ?IMT rdf:value ?value
            }
            GROUP BY ?value
            """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        count = 0
        for row in results["results"]["bindings"]:
            """value, count"""
            format = row["value"]["value"]
            partialCount = int(row["count"]["value"])
            if exact(vocabulary,format):
                count += partialCount
        return count

    def count_values_contained_in_vocabulary(self, entity, property, vocabulary):
        self.sparql.setQuery("""
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
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        count = 0
        for row in results["results"]["bindings"]:
            """value, count"""
            value = row["value"]["value"]
            partialCount = int(row["count"]["value"])
            if contains_vocabulary_word(vocabulary,value):
                count += partialCount
        return count

    def count_values_containing_vocabulary(self,  entity, property, vocabulary):
        self.sparql.setQuery("""
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
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        count = 0
        for row in results["results"]["bindings"]:
            """value, count"""
            value = row["value"]["value"]
            partialCount = int(row["count"]["value"])
            # print(license, partialCount)
            if contains_word_vocabulary(vocabulary, value):
                count += partialCount
        return count




    def count_urls_with_200_code(self, property):
        self.sparql.setQuery("""
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
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        count = 0

        error_file_name = 'errores_'+property.replace(":","_") + ".txt"
        with open(error_file_name, "w", encoding="utf-8") as text_file:
            for row in results["results"]["bindings"]:
                """value, count"""
                url = row["value"]["value"]
                partialCount = int(row["count"]["value"])
                try:
                    make_request(url)
                    count += partialCount
                except:
                    text_file.write(url + '\t' + str(partialCount) + '\n')
                    #print(url + " not reached")
        return count


    def print(self, dimension, property, count, population, weight,
              measurement_rate, measurement_of_rate,
              properties, measurement_points, measurement_of_points,
              language=None):
        if population == 0:
            percentage = 100.0
        else:
            percentage = count / population
        if count > 0:
            partialPoints = percentage * weight
            self.totalPoints += partialPoints
        else:
            partialPoints = 0
            percentage = 0.0
        print(dimension, property, count, population, percentage, partialPoints, sep=";")
        self.graph_composition(measurement_rate, measurement_of_rate, percentage,
                               properties, measurement_points, measurement_of_points,
                               partialPoints, language)

    def findability_keywords_available(self):
        dimension = FINDABILITY
        entity = DATASET
        property = 'dcat:keyword'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 30,
                   QR + 'KeywordAvailability_rate_value', QR + 'KeywordAvailability_rate',
                   [DCAT + 'dataset', DCAT + 'keyword'], QR + 'KeywordAvailability_points_value',
                   QR + 'KeywordAvailability_points')

    def findability_category_available(self):
        dimension = FINDABILITY
        entity = DATASET
        property = 'dcat:theme'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 30,
                   QR + 'CategoryAvailability_rate_value', QR + 'CategoryAvailability_rate',
                   [DCAT + 'dataset', DCAT + 'theme'], QR + 'CategoryAvailability_points_value',
                   QR + 'CategoryAvailability_points')

    def findability_spatial_available(self):
        dimension = FINDABILITY
        entity = DATASET
        property = 'dct:spatial'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 20,
                   QR + 'SpatialAvailability_rate_value', QR + 'SpatialAvailability_rate',
                   [DCAT + 'dataset', DCT + 'spatial'], QR + 'SpatialAvailability_points_value',
                   QR + 'SpatialAvailability_points')

    def findability_temporal_available(self):
        dimension = FINDABILITY
        entity = DATASET
        property = 'dct:temporal'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 20,
                   QR + 'TemporalAvailability_rate_value', QR + 'TemporalAvailability_rate',
                   [DCAT + 'dataset', DCT + 'temporal'], QR + 'TemporalAvailability_points_value',
                   QR + 'TemporalAvailability_points')

    def accesibility_accessURL_code_200(self):
        dimension = ACCESIBILITY
        entity = DISTRIBUTION
        property = 'dcat:accessURL'
        count = self.count_urls_with_200_code(property)
        population = self.distributionCount
        self.print(dimension, property + CODE_200, count, population, 50,
                   QR + 'AccessUrlStatusCode_rate_value', QR + 'AccessUrlStatusCode_rate',
                   [DCAT + 'distribution', DCAT + 'accessURL'], QR + 'AccessUrlStatusCode_points_value',
                   QR + 'AccessUrlStatusCode_points')

    def accesibility_downloadURL_available(self):
        dimension = ACCESIBILITY
        entity = DISTRIBUTION
        property = 'dcat:downloadURL'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 20,
                   QR + 'DownloadUrlAvailability_rate_value', QR + 'AccessUrlStatusCode_rate',
                   [DCAT + 'distribution', DCT + 'downloadURL'], QR + 'DownloadUrlAvailability_points_value',
                   QR + 'AccessUrlStatusCode_points')

    def accesibility_downloadURL_code_200(self):
        dimension = ACCESIBILITY
        entity = DISTRIBUTION
        property = 'dcat:downloadURL'
        count = self.count_urls_with_200_code(property)
        population = self.distributionCount
        self.print(dimension, property + CODE_200, count, population, 30,
                   QR + 'DownloadUrlStatusCode_rate_value', QR + 'DownloadUrlStatusCode_rate',
                   [DCAT + 'distribution', DCAT + 'downloadURL'], QR + 'DownloadUrlStatusCode_points_value',
                   QR + 'DownloadUrlStatusCode_points')

    def interoperability_format_available(self):
        dimension = INTEROPERABILITY
        entity = DISTRIBUTION
        property = 'dct:format'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 20,
                   QR + 'FormatAvailability_rate_value', QR + 'FormatAvailability_rate',
                   [DCAT + 'distribution', DCT + 'format'], QR + 'FormatAvailability_points_value',
                   QR + 'FormatAvailability_points')

    def interoperability_mediaType_available(self):
        dimension = INTEROPERABILITY
        entity = DISTRIBUTION
        property = 'dcat:mediaType'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 10,
                   QR + 'MediaTypeAvailability_rate_value', QR + 'MediaTypeAvailability_rate',
                   [DCAT + 'distribution', DCAT + 'mediaType'], QR + 'MediaTypeAvailability_points_value',
                   QR + 'MediaTypeAvailability_points')

    def interoperability_format_from_vocabulary(self):
        '''
        https://www.iana.org/assignments/media-types/media-types.xhtml
        '''
        dimension = INTEROPERABILITY
        entity = DISTRIBUTION
        property = 'dct:format'
        vocabulary = load_vocabulary('IMTvalues.csv')
        count = self.count_formats_from_vocabulary(vocabulary)
        population = self.distributionCount
        self.print(dimension, property + FROM_VOCABULARY, count, population, 10,
                   QR + 'FormatMediaTypeVocabularyAlignment_rate_value', QR + 'FormatMediaTypeVocabularyAlignment_rate',
                   [DCAT + 'distribution', DCT + 'format', DCAT + 'mediaType'], QR + 'FormatMediaTypeVocabularyAlignment_points_value',
                   QR + 'FormatMediaTypeVocabularyAlignment_points')

    def interoperability_format_nonProprietary(self):
        '''
        https://gitlab.com/european-data-portal/edp-vocabularies/-/blob/master/Custom%20Vocabularies/edp-non-proprietary-format.rdf
        '''
        dimension = INTEROPERABILITY
        entity = DISTRIBUTION
        property = 'dct:format'
        vocabulary = load_vocabulary('non-proprietary.csv')
        count = self.count_formats_from_vocabulary(vocabulary)
        population = self.distributionCount
        self.print(dimension, property + ' non-proprietary', count, population, 20,
                   QR + 'FormatMediaTypeNonProprietary_rate_value', QR + 'FormatMediaTypeVocabularyAlignment_rate',
                   [DCAT + 'distribution', DCT + 'format'], QR + 'FormatMediaTypeNonProprietary_points_value',
                   QR + 'FormatMediaTypeNonProprietary_points')

    def interoperability_format_machineReadable(self):
        '''
        https://gitlab.com/european-data-portal/edp-vocabularies/-/blob/master/Custom%20Vocabularies/edp-machine-readable-format.rdf
        '''
        dimension = INTEROPERABILITY
        entity = DISTRIBUTION
        property = 'dct:format'
        vocabulary = load_vocabulary('machine-readable.csv')
        count = self.count_formats_from_vocabulary(vocabulary)
        population = self.distributionCount
        self.print(dimension, property + ' machine-readable', count, population, 20,
                   QR + 'FormatMediaTypeMachineInterpretable_rate_value', QR + 'FormatMediaTypeMachineInterpretable_rate',
                   [DCAT + 'distribution', DCT + 'format'], QR + 'FormatMediaTypeMachineInterpretable_points_value',
                   QR + 'FormatMediaTypeMachineInterpretable_points')

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
        self.print(dimension, 'DCAT-AP compliance', count, population, 30,
                   QR + 'DcatApCompliance_rate_value', QR + 'DcatApCompliance_rate',
                   [DCAT + 'dataset'], QR + 'DcatApCompliance_points_value',
                   QR + 'DcatApCompliance_points')

    def reusability_license_available(self):
        dimension = REUSABILITY
        entity = DISTRIBUTION
        property = 'dct:license'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 20,
                   QR + 'LicenceAvailability_rate_value', QR + 'LicenceAvailability_rate',
                   [DCAT + 'distribution', DCT + 'license'], QR + 'LicenceAvailability_points_value',
                   QR + 'LicenceAvailability_points')

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
        self.print(dimension, property + FROM_VOCABULARY, count, population, 10,
                   QR + 'KnownLicence_rate_value', QR + 'KnownLicence_rate',
                   [DCAT + 'distribution', DCT + 'license'], QR + 'KnownLicence_points_value',
                   QR + 'KnownLicence_points')

    def reusability_accessRights_available(self):
        dimension = REUSABILITY
        entity = DATASET
        property = 'dct:accessRights'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 10,
                   QR + 'AccessRightsAvailability_rate_value', QR + 'AccessRightsAvailability_rate',
                   [DCAT + 'dataset', DCT + 'accessRights'], QR + 'AccessRightsAvailability_points_value',
                   QR + 'AccessRightsAvailability_points')

    def reusability_accessRights_from_vocabulary(self):
        dimension = REUSABILITY
        entity = DATASET
        property = 'dct:accessRights'
        vocabulary = load_vocabulary('access-right.csv',1)
        count = self.count_values_contained_in_vocabulary(entity,property,vocabulary)
        population = self.datasetCount
        self.print(dimension, property + FROM_VOCABULARY, count, population, 5,
                   QR + 'AccessRightsVocabularyAlignment_rate_value', QR + 'AccessRightsVocabularyAlignment_rate',
                   [DCAT + 'dataset', DCT + 'accessRights'], QR + 'AccessRightsVocabularyAlignment_points_value',
                   QR + 'AccessRightsVocabularyAlignment_points')


    def reusability_contactPoint_available(self):
        dimension = REUSABILITY
        entity = DATASET
        property = 'dcat:contactPoint'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 20,
                   QR + 'ContactPointAvailability_rate_value', QR + 'ContactPointAvailability_rate',
                   [DCAT + 'dataset', DCAT + 'contactPoint'], QR + 'ContactPointAvailability_points_value',
                   QR + 'ContactPointAvailability_points')

    def reusability_publisher_available(self):
        dimension = REUSABILITY
        entity = DATASET
        property = 'dct:publisher'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 10,
                   QR + 'PublisherAvailability_rate_value', QR + 'PublisherAvailability_rate',
                   [DCAT + 'distribution', DCAT + 'contactPoint'], QR + 'PublisherAvailability_points_value',
                   QR + 'PublisherAvailability_points')

    def contextuality_rights_available(self):
        dimension = CONTEXTUALITY
        entity = DISTRIBUTION
        property = 'dct:rights'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 5,
                   QR + 'RightsAvailability_rate_value', QR + 'PublisherAvailability_rate',
                   [DCAT + 'distribution', DCT + 'rights'], QR + 'RightsAvailability_points_value',
                   QR + 'RightsAvailability_points')

    def contextuality_fileSize_available(self):
        dimension = CONTEXTUALITY
        entity = DISTRIBUTION
        property = 'dcat:byteSize'
        count = self.count_entity_property(entity, property)
        population = self.distributionCount
        self.print(dimension, property, count, population, 5,
                   QR + 'ByteSizeAvailability_rate_value', QR + 'ByteSizeAvailability_rate',
                   [DCAT + 'distribution', DCAT + 'byteSize'], QR + 'ByteSizeAvailability_points_value',
                   QR + 'ByteSizeAvailability_points')

    def contextuality_issued_available(self):
        dimension = CONTEXTUALITY
        entity = DATASET
        property = 'dct:issued'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 5,
                   QR + 'DateIssuedAvailability_rate_value', QR + 'DateIssuedAvailability_rate',
                   [DCAT + 'dataset', DCT + 'issued'], QR + 'DateIssuedAvailability_points_value',
                   QR + 'DateIssuedAvailability_points')

    def contextuality_modified_available(self):
        dimension = CONTEXTUALITY
        entity = DATASET
        property = 'dct:modified'
        count = self.count_entity_property(entity, property)
        population = self.datasetCount
        self.print(dimension, property, count, population, 5,
                   QR + 'DateModifiedAvailability_rate_value', QR + 'DateModifiedAvailability_rate',
                   [DCAT + 'dataset', DCT + 'modified'], QR + 'DateModifiedAvailability_points_value',
                   QR + 'DateModifiedAvailability_points')

    def evaluate(self):
        print("Dimension", "Indicator/property", "Count","Population","Percentage", "Points")
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
        print("Total points", self.totalPoints)
        self.graph_serialization()

    def graph_composition(self, measurement_rate, measurement_of_rate, value,
                          properties, measurement_points, measurement_of_points,
                          partialPoints, language):
        # FIJO
        catalog = URIRef(QR + 'myCatalog')
        self.graph.add((catalog, RDF.type, URIRef(DCAT + 'Catalog')))
        self.graph.add((catalog, DCTERMS.title, Literal('datos.gob.es')))
        ####

        measurement = URIRef(measurement_rate)
        measurement_derived = URIRef(measurement_points)

        self.graph.add((catalog, URIRef(DQV + 'hasQualityMeasurement'), measurement))
        self.graph.add((measurement, RDF.type, URIRef(DQV + 'QualityMeasurement')))
        self.graph.add((measurement, URIRef(DQV + 'computedOn'), catalog))

        measurement_of = URIRef(measurement_of_rate)
        self.graph.add((measurement, URIRef(DQV + 'isMeasurementOf'), measurement_of))
        self.graph.add((measurement, URIRef(DQV + 'value'), Literal(value, datatype=XSD + 'double')))
        self.graph.add((measurement, URIRef(DCT + 'date'), Literal(self.date, datatype=XSD + 'date')))

        for property in properties:
            onProperty = URIRef(property)
            self.graph.add((measurement, URIRef(QR + 'onProperty'), onProperty))
            self.graph.add((measurement_derived, URIRef(QR + 'onProperty'), onProperty))

        if language is not None:
            self.graph.add((measurement, URIRef('http://www.qualityreport.com/qr/onLanguage'), Literal(language)))

        self.graph.add((catalog, URIRef(DQV + 'hasQualityMeasurement'), measurement_derived))
        self.graph.add((measurement_derived, RDF.type, URIRef(DQV + 'QualityMeasurement')))
        self.graph.add((measurement_derived, URIRef(DQV + 'computedOn'), catalog))

        measurement_of_conformance = URIRef(measurement_of_points)
        self.graph.add((measurement_derived, URIRef(DQV + 'isMeasurementOf'), measurement_of_conformance))
        # se añade esta linea
        self.graph.add((measurement_derived, URIRef(PROV + 'wasDerivedFrom'), measurement))
        #
        # Cambia el tipo
        self.graph.add((measurement_derived, URIRef(DQV + 'value'), Literal(partialPoints, datatype=XSD + 'double')))
        #
        self.graph.add((measurement_derived, URIRef(DCT + 'date'), Literal(self.date, datatype=XSD + 'date')))

    def graph_serialization(self, graph_format='turtle'):
        self.graph.serialize(destination='../DQV_files/' + self.filename, format=graph_format)
