"""
harvester/SPARQL_harvester.py
Author: Javier Nogueras (jnog@unizar.es)
Last update: 2022-07-06

Program to harvest metadata records using a SPARQL end-point
"""

from SPARQLWrapper import SPARQLWrapper, JSON

import os, sys
import ssl

import rdflib

OUTPUT = "output/"

ES_SPARQL = 'http://datos.gob.es/virtuoso/sparql'
ES_RDF = 'https://datos.gob.es/apidata/catalog/dataset/'


EDP_SPARQL = 'https://data.europa.eu/sparql'
EDP_RDF = 'https://data.europa.eu/data/api/datasets/'
EDP_FORMAT = '.ttl?useNormalizedId=true&locale=en'

def get_file_name(url):
    """
    https://europeandataportal.eu/set/data/https-opendata-aragon-es-datos-catalogo-dataset-oai-zaguan-unizar-es-89319
    return https-opendata-aragon-es-datos-catalogo-dataset-oai-zaguan-unizar-es-89319
    """
    words = url.split('/')
    file_name = words[len(words)-1]
    return file_name

def transform_to_file_name(url):
    x = ":/\\."
    y = "____"
    table = url.maketrans(x, y)
    return url.translate(table)

def create_folder(url):
    if (not os.path.exists(OUTPUT)):
        os.mkdir(OUTPUT)
    folder_name = transform_to_file_name(url)
    output_path = os.path.join(OUTPUT,folder_name)
    if (not os.path.exists(output_path)):
        os.mkdir(output_path)
    return output_path



class SPARQL_harvester:

    def __init__(self, url, user = None, passwd = None, rdf_url = None, limit = 10000, max_number_of_records = None, output_folder = OUTPUT, format = '.ttl'):
        self.url = url
        self.sparql = SPARQLWrapper(url)
        if user is not None:
            self.sparql.setCredentials(user, passwd)
        self.rdf_url = rdf_url
        self.limit = limit
        self.output_folder = output_folder
        self.format = format
        self.max_number_of_records = max_number_of_records

    def parse_dataset(self, url, graph):
        """
        Parses the dataset with URL in the graph
        """
        if self.rdf_url is not None:
            id = get_file_name(url)
            rdf_url = self.rdf_url + id + self.format
        else:
            rdf_url = url + self.format
        # print(rdf_url)
        try:
            graph.parse(rdf_url, format="turtle")
        except Exception as err:
            print(f'Other error occurred: {err}')
        return graph

    def parse_catalog(self, results, filename):
        graph = rdflib.Graph()
        for row in results["results"]["bindings"]:
            """s"""
            dataset = row["s"]["value"]
            graph = self.parse_dataset(dataset, graph)
        graph.serialize(destination=filename, format='pretty-xml') # we use XML to avoid the problems derived from the serialization of some URIs
        # graph.serialize(destination=filename, format='turtle')

    def count_datasets(self):
        self.sparql.setQuery("""
                  PREFIX dct:<http://purl.org/dc/terms/>
                  PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                  PREFIX dcat: <http://www.w3.org/ns/dcat#>
                  SELECT (count(DISTINCT ?s) as ?values) WHERE { 
                    ?s a dcat:Dataset 
                  }
                """)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        print(results)
        for row in results["results"]["bindings"]:
            """values"""
            count = int(row["values"]["value"])
        return count

    def download_datasets(self, filename, offset):
        query = """
              PREFIX dct:<http://purl.org/dc/terms/>
              PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
              PREFIX dcat: <http://www.w3.org/ns/dcat#>
              SELECT DISTINCT ?s WHERE { 
                   ?s a dcat:Dataset . 
              }
              ORDER by ?s
              OFFSET  """ + str(offset) + """
              LIMIT """ + str(self.limit) + """
            """
        print(query)
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        self.parse_catalog(results, filename)

    def harvest(self):
        folder = create_folder(self.url)
        count = self.count_datasets()
        print (count, ' datasets')
        if self.max_number_of_records is not None:
            count = self.max_number_of_records
        offset = 0
        i=1
        while (offset < count):
            catalog_file_name = os.path.join(folder, 'catalog'+str(i)+'.rdf')
            self.download_datasets( catalog_file_name, offset)
            offset = offset + self.limit
            i = i + 1

if __name__ == '__main__':

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    URL = sys.argv[1]

    harvester = SPARQL_harvester(url = URL, limit=100, max_number_of_records=500, output_folder = OUTPUT)
    # harvester = SPARQL_harvester(url = ES_SPARQL, rdf_url= ES_RDF, limit=50, max_number_of_records=50, output_folder = OUTPUT, format = EDP_FORMAT)
    # harvester = SPARQL_harvester(url = EDP_SPARQL, rdf_url= EDP_RDF, limit=50, max_number_of_records=50, output_folder = OUTPUT, format = EDP_FORMAT)
    harvester.harvest()
