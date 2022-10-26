"""
evaluate.py
Author: Javier Nogueras-Iso, Javier Lacasta, Manuel Antonio Ureña-Cámara, Francisco Javier Ariza-López
Last update: 2020-04-14

Class to compute measures proposed according to ISO 19157
"""

import urllib.request
from datetime import datetime, timezone

import rdflib
import validators
from SPARQLWrapper import SPARQLWrapper, JSON
from pyshacl import validate

from IndicePerspicuidad import DeterminarIndices

# from uri_access import *

COMPLETENESS_OMISSION = 'DQ_CompletenessOmission'

COMPLETENESS_COMMISSION = 'DQ_CompletenessCommission'

CONCEPTUAL_CONSISTENCY = 'DQ_ConceptualConsistency'

DOMAIN_CONSISTENCY = 'DQ_DomainConsistency'

TEMPORAL_CONSISTENCY = 'DQ_TemporalConsistency'

TEMPORAL_VALIDITY = 'DQ_TemporalValidity'

NON_THEMATIC_CLASSIFICATION_CORRECTNESS = 'DQ_ThematicClassificationCorrectness'

NON_QUANTITATIVE_ATTRIBUTE_CORRECTNESS = 'DQ_NonQuantitativeAttributeCorrectness'

POSITIONAL_CORRECTNESS = 'DQ_PositionalCorrectness'

QUALITY_OF_FREE_TEXT = 'DQ_QualityOfFreeText'

DISTRIBUTION = 'dcat:Distribution'

DATASET = 'dcat:Dataset'

THRESHOLD = 0.9584

LIMIT = 200000


def make_request(url):
    request = urllib.request.Request(url)
    # Make the HTTP request.
    response = urllib.request.urlopen(request, timeout=5)
    assert 200 <= response.code < 400


def load_vocabulary(vocabulary_file):
    vocabulary = []
    with open(vocabulary_file) as fp:
        for line in fp:
            words = line.strip().split(',')
            if words[0] != '':
                vocabulary.append(words[0])
    return vocabulary


def contains_exact(vocabulary, word):
    for value in vocabulary:
        if value == word:
            return True
    return False


def contains(vocabulary, word):
    for value in vocabulary:
        if word.find(value) >= 0:
            return True
    return False


def parse_url(origin_url):
    return urllib.parse.quote(origin_url.strip(), ':/?=&%@*_+-.').lower()


def str_to_date(date_time_str):
    """
    Expected date:  1900-01-01T09:00:00Z , 2022-03-16T00:00:00+01:00
    """
    date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%dT%H:%M:%S%z')
    # previous code:  datetime.fromisoformat(i['issued']['value'])
    return date_time_obj


class ISO19157Evaluation:

    def __init__(self, url, user=None, passwd=None, harvest_date_string=None, url_strict_check=False):
        self.sparql = SPARQLWrapper(url)
        if user is not None:
            self.sparql.setCredentials(user, passwd)
        self.datasetCount = self.count_entities(DATASET)
        self.distributionCount = self.count_entities(DISTRIBUTION)
        self.timeData = ""  # Espacio para los resultados de la consulta temporal porque se usa dos veces
        self.checks = 0
        self.passedChecks = 0
        if harvest_date_string is not None:
            self.harvest_date = str_to_date(harvest_date_string)
        else:
            self.harvest_date = datetime.now(timezone.utc)
        self.url_strict_check = url_strict_check

    def count_entities(self, entity):
        self.sparql.setQuery("""
                   PREFIX dct:<http://purl.org/dc/terms/>
                   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX dcat: <http://www.w3.org/ns/dcat#>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT  (count(DISTINCT ?resource) as ?values)  WHERE {
                        ?resource rdf:type """ + entity + """ .
                    }
                    """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for row in results["results"]["bindings"]:
            """values"""
            count = int(row["values"]["value"])
        return count

    def count(self, query):
        self.sparql.setQuery(query)
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
                        ?resource rdf:type """ + entity + """ .
        	            ?resource """ + property + """ ?value .
                    }
                    """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for row in results["results"]["bindings"]:
            """values"""
            count = int(row["values"]["value"])
        return count

    def count_distinct_entity_property(self, entity, property):
        self.sparql.setQuery("""
                   PREFIX dct:<http://purl.org/dc/terms/>
                   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX dcat: <http://www.w3.org/ns/dcat#>
                   PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                   SELECT  (count(DISTINCT ?value) as ?values)  WHERE {
                        ?resource rdf:type """ + entity + """ .
        	            ?resource """ + property + """ ?value .
                    }
                    """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for row in results["results"]["bindings"]:
            """values"""
            count = int(row["values"]["value"])
        return count

    def count_distinct_entity_property_literal_range(self, entity, property, range):
        self.sparql.setQuery("""
                   PREFIX dct:<http://purl.org/dc/terms/>
                   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX dcat: <http://www.w3.org/ns/dcat#>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT  (count(DISTINCT ?value) as ?values)  WHERE {
                        ?resource rdf:type """ + entity + """ .
        	            ?resource """ + property + """ ?value .
        	            FILTER(datatype(?value)=""" + range + """) .
                    }
                    """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for row in results["results"]["bindings"]:
            """values"""
            count = int(row["values"]["value"])
        return count

    def count_distinct_entity_property_is_literal(self, entity, property):
        self.sparql.setQuery("""
                   PREFIX dct:<http://purl.org/dc/terms/>
                   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX dcat: <http://www.w3.org/ns/dcat#>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    SELECT  (count(DISTINCT ?value) as ?values)  WHERE {
                        ?resource rdf:type """ + entity + """ .
        	            ?resource """ + property + """ ?value .
        	            FILTER(isLiteral(?value)) .
                    }
                    """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for row in results["results"]["bindings"]:
            """values"""
            count = int(row["values"]["value"])
        return count

    def count_distinct_entity_property_class_range(self, entity, property, range):
        self.sparql.setQuery("""
                   PREFIX dct:<http://purl.org/dc/terms/>
                   PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                   PREFIX dcat: <http://www.w3.org/ns/dcat#>
                   PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                   PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
                   PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                   PREFIX vocab: <http://vocab.linkeddata.es/datosabiertos/def/sector-publico/territorio#>
                   SELECT  (count(DISTINCT ?value) as ?values)  WHERE {
                        ?resource rdf:type """ + entity + """ .
        	            ?resource """ + property + """ ?value .
        	            ?value rdf:type """ + range + """ .
                    }
                    """)

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        for row in results["results"]["bindings"]:
            """values"""
            count = int(row["values"]["value"])
        return count

    def count_distinct_formats(self):
        self.sparql.setQuery("""
            PREFIX dct:<http://purl.org/dc/terms/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT (count(DISTINCT ?IMTValue) as ?values) WHERE {
                ?resource rdf:type dcat:Distribution .
                ?resource dct:format ?value .
                ?value rdf:type dct:IMT .
                ?value rdf:value ?IMTValue .
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
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
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
            if contains_exact(vocabulary, format):
                count += 1  # We are only interested in distinct formats
        return count

    def count_urls_with_200_code(self, entity, property):
        self.sparql.setQuery("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            SELECT ?value (COUNT(?value) as ?count)
            WHERE {
                ?resource a """ + entity + """ .
                ?resource """ + property + """ ?value
            }
            GROUP BY ?value
            """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        count = 0

        error_file_name = 'errors_' + property.replace(":", "_") + ".txt"
        with open(error_file_name, "w", encoding="utf-8") as text_file:
            for row in results["results"]["bindings"]:
                """value, count"""
                url = parse_url(row["value"]["value"])
                partialCount = int(row["count"]["value"])
                try:
                    make_request(url)
                    count += 1  # We are only interested in distinct accessible URLs
                except:
                    text_file.write(url + '\t' + str(partialCount) + '\n')
                    # print(url + " not reached")
        return count

    def count_valid_uris(self, entity, property, population):
        offset = 0
        count = 0
        while offset < population:
            self.sparql.setQuery("""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX dct: <http://purl.org/dc/terms/>
                PREFIX dcat: <http://www.w3.org/ns/dcat#>
                SELECT DISTINCT ?value
                WHERE {
                    ?resource a """ + entity + """ .
                    ?resource """ + property + """ ?value
                }
                OFFSET """ + str(offset) + """
                LIMIT """ + str(LIMIT))
            self.sparql.setReturnFormat(JSON)
            results = self.sparql.query().convert()

            for row in results["results"]["bindings"]:
                offset = offset + 1
                uri = row["value"]["value"]
                url = parse_url(uri)
                valid = validators.url(url)
                if valid:
                    count += 1
                else:  # Check if uri is a urn. This check could be improved
                    if uri.strip().lower().startswith('urn:'):
                        count += 1
        return count

    def count_valid_urls(self, entity, property, population):
        offset = 0
        count = 0
        while offset < population:
            self.sparql.setQuery("""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX dct: <http://purl.org/dc/terms/>
                PREFIX dcat: <http://www.w3.org/ns/dcat#>
                SELECT DISTINCT ?value
                WHERE {
                    ?resource a """ + entity + """ .
                    ?resource """ + property + """ ?value
                }
                OFFSET """ + str(offset) + """
                LIMIT """ + str(LIMIT))
            self.sparql.setReturnFormat(JSON)
            results = self.sparql.query().convert()

            for row in results["results"]["bindings"]:
                offset = offset + 1
                url = parse_url(row["value"]["value"])
                valid = validators.url(url)
                if valid:
                    count += 1
        return count

    def count_freetext(self, entity, property):
        self.sparql.setQuery("""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>

            SELECT ?recurso ?valor
            WHERE {
                ?recurso rdf:type """ + entity + """ .
                ?recurso """ + property + """ ?valor .
                FILTER (lang(?valor) = 'es')
            }""")

        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()

        # TODO: Eliminar caracteres extraños y dependientes del HTML, otras codificaciones, etc.
        # Por ahora eso no afecta a los resultados con el conjunto almacenado

        # Calculamos ambos índices
        count = sum(map(lambda x: 1 if x >= 50 else 0,
                        [DeterminarIndices(i['valor']['value']).returnmax() for i in results['results']['bindings']]))

        return count

    def count_temporal_consistency(self):
        # Versión reducida de la consulta porque hemos quitado el accuralPeriodicity y startDate and endDate
        if len(self.timeData) == 0:
            self.sparql.setQuery("""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                PREFIX dct: <http://purl.org/dc/terms/>
                PREFIX dcat: <http://www.w3.org/ns/dcat#>

                SELECT ?recurso ?issued ?modified ?valid
                WHERE {
                    ?recurso a dcat:Dataset .
                    optional { ?recurso dct:issued ?issued }
                    optional { ?recurso dct:modified ?modified }
                    optional { ?recurso dct:valid ?valid }
                }""")
            self.sparql.setReturnFormat(JSON)
            self.timeData = self.sparql.query().convert()

        # Asignamos la consulta almacenada
        results = self.timeData

        # Realizamos el cuenteo teniendo en cuenta los elementos opcionales
        error_count = 0
        for i in results['results']['bindings']:
            # La comprobacion es issued<=modified<=valid
            issued_lt_modified = True
            issued_lt_valid = True
            modified_lt_valid = True

            if ('issued' in i) and ('modified' in i):
                issued_lt_modified = str_to_date(i['issued']['value']) <= str_to_date(i['modified']['value'])
            if ('issued' in i) and ('valid' in i):
                issued_lt_valid = str_to_date(i['issued']['value']) <= str_to_date(i['valid']['value'])
            if ('modified' in i) and ('valid' in i):
                modified_lt_valid = str_to_date(i['modified']['value']) <= str_to_date(i['valid']['value'])
            if issued_lt_modified and issued_lt_valid and modified_lt_valid:
                pass
            else:
                error_count = error_count + 1
        return error_count

    def count_temporal_validity(self, harvest):
        if len(self.timeData) == 0:
            self.sparql.setQuery("""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                PREFIX dct: <http://purl.org/dc/terms/>
                PREFIX dcat: <http://www.w3.org/ns/dcat#>

                SELECT ?recurso ?issued ?modified ?valid
                WHERE {
                    ?recurso a dcat:Dataset .
                    optional { ?recurso dct:issued ?issued }
                    optional { ?recurso dct:modified ?modified }
                    optional { ?recurso dct:valid ?valid }
                }""")
            self.sparql.setReturnFormat(JSON)
            self.timeData = self.sparql.query().convert()

        # Asignamos la consulta almacenada
        results = self.timeData

        # Realizamos el cuenteo teniendo en cuenta los elementos opcionales
        error_count = 0
        for i in results['results']['bindings']:
            # La comprobacion es harvest<=valid	harvest>=issued	harvest>=modified
            issued_lt_harvest = True
            modified_lt_harvest = True
            valid_gt_harvest = True
            if ('issued' in i):
                issued_lt_harvest = str_to_date(i['issued']['value']) <= harvest
            if ('modified' in i):
                modified_lt_harvest = str_to_date(i['modified']['value']) <= harvest
            if ('valid' in i):
                valid_gt_harvest = str_to_date(i['valid']['value']) >= harvest
            if issued_lt_harvest and modified_lt_harvest and valid_gt_harvest:
                pass
            else:
                error_count = error_count + 1  # El error funciona mejor que en la solución suma

        return error_count

    def print(self, dimension, entity, property, count, population):
        self.checks += 1
        percentage = count / population
        if percentage >= THRESHOLD:
            passed = True
            self.passedChecks += 1
        else:
            passed = False
        print(dimension, entity, property, count, population, percentage, passed, sep=";")

    def completeness_commission_dataset(self):
        dimension = COMPLETENESS_COMMISSION
        entity = DATASET
        population = self.datasetCount
        query = """
                PREFIX dct:<http://purl.org/dc/terms/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX dcat: <http://www.w3.org/ns/dcat#>
                SELECT ?resource WHERE {
                    ?resource rdf:type dcat:Dataset .
                    OPTIONAL {?resource dct:identifier ?value1} .
                    OPTIONAL {?resource dct:modified ?value2} .
                    OPTIONAL {?resource dct:issued ?value3} .
                    OPTIONAL {?resource dct:accrualPeriodicity ?value4} .
                    OPTIONAL {?resource dct:license ?value5} .
                    OPTIONAL {?resource dct:valid ?value6} .
                    OPTIONAL {?resource dct:publisher ?value7}
                } 
                GROUP BY ?resource
                HAVING ((count(?resource) > 1))
                    """
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        count = population - len(results["results"]["bindings"])  # For the moment, we compute correct percentage
        self.print(dimension, entity, None, count, population)

    def completeness_commission_distribution(self):
        dimension = COMPLETENESS_COMMISSION
        entity = DISTRIBUTION
        population = self.distributionCount
        query = """
                PREFIX dct:<http://purl.org/dc/terms/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX dcat: <http://www.w3.org/ns/dcat#>
                SELECT ?resource WHERE {
                    ?resource rdf:type dcat:Distribution .
                    OPTIONAL {?resource dct:identifier ?value1} .
                    OPTIONAL {?resource dcat:accessURL ?value2} .
                    OPTIONAL {?resource dcat:mediaType ?value3} .
                    OPTIONAL {?resource dcat:byteSize ?value4} 
                } 
                GROUP BY ?resource
                HAVING ((count(?resource) > 1))
                     """
        self.sparql.setReturnFormat(JSON)
        self.sparql.setQuery(query)
        results = self.sparql.query().convert()
        count = population - len(results["results"]["bindings"])  # For the moment, we compute correct percentage
        self.print(dimension, entity, None, count, population)

    def completeness_omission_dataset(self):
        dimension = COMPLETENESS_OMISSION
        entity = DATASET
        population = self.datasetCount
        query = """
                PREFIX dct:<http://purl.org/dc/terms/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX dcat: <http://www.w3.org/ns/dcat#>
                SELECT (count(?resource) AS ?values) WHERE {
                  {
                      ?resource rdf:type dcat:Dataset .
                      FILTER NOT EXISTS { ?resource dct:title ?value1 }
                  } UNION {
                      ?resource rdf:type dcat:Dataset .
                      FILTER NOT EXISTS { ?resource dct:publisher ?value2 }
                  } UNION {
                      ?resource rdf:type dcat:Dataset .
                      FILTER NOT EXISTS { ?resource dct:description ?value3 }
                  } UNION {
                      ?resource rdf:type dcat:Dataset .
                      FILTER NOT EXISTS { ?resource dcat:theme ?value4 }
                  } UNION {
                      ?resource rdf:type dcat:Dataset .
                      FILTER NOT EXISTS { ?resource dcat:distribution ?value5 }
                  }
                }
                    """
        count = population - self.count(query)  # For the moment, we compute correct percentage
        self.print(dimension, entity, None, count, population)

    def completeness_omission_distribution(self):
        dimension = COMPLETENESS_OMISSION
        entity = DISTRIBUTION
        population = self.distributionCount
        query = """
                PREFIX dct:<http://purl.org/dc/terms/>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX dcat: <http://www.w3.org/ns/dcat#>
                SELECT (count(?resource) AS ?values) WHERE {
                  {
                      ?resource rdf:type dcat:Distribution .
                      FILTER NOT EXISTS { ?resource dcat:accessURL ?value1 }
                  } UNION {
                      ?resource rdf:type dcat:Distribution .
                      FILTER NOT EXISTS { ?resource dcat:mediaType ?value2 }
                  }
                }
                    """
        count = population - self.count(query)  # For the moment, we compute correct percentage
        self.print(dimension, entity, None, count, population)

    def conceptual_consistency_dataset(self):
        dimension = CONCEPTUAL_CONSISTENCY
        entity = DATASET
        population = self.datasetCount
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            SELECT (count (DISTINCT ?resource) as ?values)
            WHERE {
                ?resource rdf:type dcat:Dataset .
                ?resource ?property ?value .
                FILTER (?property NOT IN  (rdf:type, dcat:distribution, dcat:keyword, dcat:theme, dct:accrualPeriodicity, dct:conformsTo, dct:description, dct:identifier, dct:issued, dct:language, dct:license, dct:modified, dct:publisher, dct:references, dct:spatial, dct:temporal, dct:title, dct:valid))
            }

                    """
        # We make the exception of considering dct:language instead of dc:language
        count = population - self.count(query)
        self.print(dimension, entity, None, count, population)

    def conceptual_consistency_distribution(self):
        dimension = CONCEPTUAL_CONSISTENCY
        entity = DISTRIBUTION
        population = self.distributionCount
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            SELECT (count (DISTINCT ?resource) as ?values)
            WHERE {
                ?resource rdf:type dcat:Distribution .
                ?resource ?property ?value .
                FILTER (?property NOT IN  (rdf:type, dcat:accessURL, dcat:byteSize, dcat:mediaType, dct:identifier, dct:relation, dct:title))
            }
                    """
        count = population - self.count(query)
        self.print(dimension, entity, None, count, population)

    def count_valid_format_urls(self, population):
        offset = 0
        count = 0
        while offset < population:
            self.sparql.setQuery("""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX dct: <http://purl.org/dc/terms/>
                PREFIX dcat: <http://www.w3.org/ns/dcat#>
                SELECT ?url ?value ?label
                WHERE {
                    ?resource rdf:type dcat:Distribution .
                    ?resource dcat:accessURL ?url .
                    ?resource dct:format ?format .
                    OPTIONAL {?format rdf:value ?value} .
                    OPTIONAL {?format rdfs:label ?label}
                }
                OFFSET """ + str(offset) + """
                LIMIT """ + str(LIMIT))
            self.sparql.setReturnFormat(JSON)
            results = self.sparql.query().convert()

            for row in results["results"]["bindings"]:
                offset = offset + 1
                url = parse_url(row["url"]["value"])
                label = row["label"]["value"].lower()
                value = row["value"]["value"].lower()
                if self.url_strict_check:
                    urlReport = URL(url, offline=False, timeout=5)
                    magic = urlReport.getType().magic
                    http = urlReport.getType().http
                    extension = urlReport.getType().extension
                    if label in magic or label in http or label in extension:
                        count += 1
                else:
                    if label in url or value in url:
                        count += 1
        return count

    def conceptual_consistency_distribution_format_accessURL(self):
        dimension = CONCEPTUAL_CONSISTENCY
        entity = DISTRIBUTION
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            SELECT (count (DISTINCT ?resource) as ?values)
            WHERE {
                ?resource rdf:type dcat:Distribution .
                ?resource dcat:accessURL ?url .
                ?resource dct:format ?format .
                OPTIONAL {?format rdf:value ?value} .
                OPTIONAL {?format rdfs:label ?label}
            }
                    """
        # in principle the population should be equivalent to self.distributionCount. We calculate again for security if later we use while loop
        population = self.count(query)
        count = self.count_valid_format_urls(population)
        self.print(dimension, entity, 'dct:format vs dcat:accessURL', count, population)

    def domain_consistency_dataset_title(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:title'
        # count = self.count_distinct_entity_property_literal_range(entity, property, 'rdf:langString')
        count = self.count_distinct_entity_property_is_literal(entity, property)
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_description(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:description'
        # count = self.count_distinct_entity_property_literal_range(entity, property, 'rdf:langString')
        count = self.count_distinct_entity_property_is_literal(entity, property)
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_theme(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dcat:theme'
        count = self.count_distinct_entity_property_class_range(entity, property, 'skos:Concept')
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_keyword(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dcat:keyword'
        count = self.count_distinct_entity_property_is_literal(entity, property)
        # count = self.count_distinct_entity_property_literal_range(entity, property, 'xsd:string')
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_identifier(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:identifier'
        population = self.count_distinct_entity_property(entity, property)
        count = self.count_valid_uris(entity, property, population)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_issued(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:issued'
        count = self.count_distinct_entity_property_literal_range(entity, property, 'xsd:dateTime')
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_modified(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:modified'
        count = self.count_distinct_entity_property_literal_range(entity, property, 'xsd:dateTime')
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_accrualPeriodicity(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:accrualPeriodicity'
        count = self.count_distinct_entity_property_class_range(entity, property, 'dct:Frequency')
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_language(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:language'
        population = self.count_distinct_entity_property(entity, property)
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dcat: <http://www.w3.org/ns/dcat#>
            SELECT (count(DISTINCT ?value) as ?values)
            WHERE {
                ?resource rdf:type dcat:Dataset .
                ?resource dct:language ?value .
                FILTER (?value IN  ('es', 'gl', 'ca', 'eu', 'en', 'fr'))
            }
            """
        count = self.count(query)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_publisher(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:publisher'
        count = self.count_distinct_entity_property_class_range(entity, property, 'foaf:Agent')
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_spatial(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:spatial'
        count = self.count_distinct_entity_property_class_range(entity, property, 'vocab:Provincia')
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_temporal(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:temporal'
        count = self.count_distinct_entity_property_class_range(entity, property, 'dct:PeriodOfTime')
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_valid(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:valid'
        count = self.count_distinct_entity_property_literal_range(entity, property, 'xsd:dateTime')
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_references(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:references'
        population = self.count_distinct_entity_property(entity, property)
        count = self.count_valid_urls(entity, property, population)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_conformsTo(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:conformsTo'
        population = self.count_distinct_entity_property(entity, property)
        count = self.count_valid_urls(entity, property, population)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_license(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dct:license'
        population = self.count_distinct_entity_property(entity, property)
        count = self.count_valid_urls(entity, property, population)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_dataset_distribution(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DATASET
        property = 'dcat:distribution'
        count = self.count_distinct_entity_property_class_range(entity, property, DISTRIBUTION)
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_distribution_identifier(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DISTRIBUTION
        property = 'dct:identifier'
        population = self.count_distinct_entity_property(entity, property)
        count = self.count_valid_uris(entity, property, population)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_distribution_title(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DISTRIBUTION
        property = 'dct:title'
        count = self.count_distinct_entity_property_is_literal(entity, property)
        # count = self.count_distinct_entity_property_literal_range(entity, property, 'rdf:langString')
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_distribution_accessURL(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DISTRIBUTION
        property = 'dcat:accessURL'
        population = self.count_distinct_entity_property(entity, property)
        count = self.count_valid_urls(entity, property, population)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_distribution_format(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DISTRIBUTION
        property = 'dct:format'
        vocabulary = load_vocabulary('IMTvalues.csv')
        count = self.count_formats_from_vocabulary(vocabulary)
        population = self.count_distinct_formats()
        self.print(dimension, entity, property, count, population)

    def domain_consistency_distribution_byteSize(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DISTRIBUTION
        property = 'dcat:byteSize'
        count = self.count_distinct_entity_property_literal_range(entity, property, 'xsd:decimal')
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def domain_consistency_distribution_license(self):
        dimension = DOMAIN_CONSISTENCY
        entity = DISTRIBUTION
        property = 'dct:license'
        population = self.count_distinct_entity_property(entity, property)
        count = self.count_valid_urls(entity, property, population)
        self.print(dimension, entity, property, count, population)

    def temporal_consistency(self):
        dimension = TEMPORAL_CONSISTENCY
        entity = DATASET
        count = self.datasetCount - self.count_temporal_consistency()
        population = self.datasetCount
        self.print(dimension, entity, 'dct:issued, dct:modified, dct:valid', count, population)

    def temporal_validity(self):
        dimension = TEMPORAL_VALIDITY
        entity = DATASET
        count = self.datasetCount - self.count_temporal_validity(self.harvest_date)
        population = self.datasetCount
        self.print(dimension, entity, 'dct:issued, dct:modified, dct:valid', count, population)

    def non_quantitative_attribute_correctness_dataset_references(self):
        dimension = NON_QUANTITATIVE_ATTRIBUTE_CORRECTNESS
        entity = DATASET
        property = 'dct:references'
        count = self.count_urls_with_200_code(entity, property)
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def non_quantitative_attribute_correctness_dataset_conformsTo(self):
        dimension = NON_QUANTITATIVE_ATTRIBUTE_CORRECTNESS
        entity = DATASET
        property = 'dct:conformsTo'
        count = self.count_urls_with_200_code(entity, property)
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def non_quantitative_attribute_correctness_distribution_accessURL(self):
        dimension = NON_QUANTITATIVE_ATTRIBUTE_CORRECTNESS
        entity = DISTRIBUTION
        property = 'dcat:accessURL'
        count = self.count_urls_with_200_code(entity, property)
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def non_quantitative_attribute_correctness_distribution_license(self):
        dimension = NON_QUANTITATIVE_ATTRIBUTE_CORRECTNESS
        entity = DISTRIBUTION
        property = 'dct:license'
        count = self.count_urls_with_200_code(entity, property)
        population = self.count_distinct_entity_property(entity, property)
        self.print(dimension, entity, property, count, population)

    def positional_correctness(self):
        dimension = POSITIONAL_CORRECTNESS
        entity = DATASET
        property = 'dct:spatial'
        count = -1  # TODO
        population = self.datasetCount
        self.print(dimension, entity, property, count, population)

    def quality_of_free_text_dataset_title(self):
        dimension = QUALITY_OF_FREE_TEXT
        entity = DATASET
        property = 'dct:title'
        count = self.count_freetext(entity, property)
        population = self.datasetCount
        self.print(dimension, entity, property, count, population)

    def quality_of_free_text_dataset_description(self):
        dimension = QUALITY_OF_FREE_TEXT
        entity = DATASET
        property = 'dct:description'
        count = self.count_freetext(entity, property)
        population = self.datasetCount
        self.print(dimension, entity, property, count, population)

    def evaluate(self):

        print("Dimension", "Entity", "Property", "Count", "Population", "Percentage", "Pass")

        # Completeness commission
        self.completeness_commission_dataset()
        self.completeness_commission_distribution()

        # Completeness omission
        self.completeness_omission_dataset()
        self.completeness_omission_distribution()

        # Conceptual consistency
        self.conceptual_consistency_dataset()
        self.conceptual_consistency_distribution()
        # TODO: Habilitar metrica
        # self.conceptual_consistency_distribution_format_accessURL()

        # Domain consistency Dataset
        self.domain_consistency_dataset_title()
        self.domain_consistency_dataset_description()
        self.domain_consistency_dataset_theme()
        self.domain_consistency_dataset_keyword()
        self.domain_consistency_dataset_identifier()
        self.domain_consistency_dataset_issued()
        self.domain_consistency_dataset_modified()
        self.domain_consistency_dataset_accrualPeriodicity()
        self.domain_consistency_dataset_language()
        self.domain_consistency_dataset_publisher()
        self.domain_consistency_dataset_spatial()
        self.domain_consistency_dataset_temporal()
        self.domain_consistency_dataset_valid()
        self.domain_consistency_dataset_references()
        self.domain_consistency_dataset_conformsTo()
        self.domain_consistency_dataset_distribution()
        self.domain_consistency_dataset_license()

        # Domain consistency Distribution
        self.domain_consistency_distribution_identifier()
        self.domain_consistency_distribution_title()
        #TODO: Habilitar metrica
        # self.domain_consistency_distribution_accessURL()
        self.domain_consistency_distribution_format()
        self.domain_consistency_distribution_byteSize()
        # self.domain_consistency_distribution_license()

        # Temporal quality
        self.temporal_consistency()
        self.temporal_validity()

        # Thematic accuracy
        # self.non_quantitative_attribute_correctness_dataset_conformsTo()
        # self.non_quantitative_attribute_correctness_dataset_references()
        # self.non_quantitative_attribute_correctness_distribution_accessURL()
        # self.non_quantitative_attribute_correctness_distribution_license()

        # Positional positional_correctness
        self.positional_correctness()

        # Quality of free text
        self.quality_of_free_text_dataset_title()
        self.quality_of_free_text_dataset_description()

        print(self.passedChecks, "passed checks out of ", self.checks, " checks")
