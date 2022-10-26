"""
mqa/run.py
Author: Javier Nogueras (jnog@unizar.es)
Last update: 2020-11-13

MQA evaluation of Spanish metadata about budget at datos.gob.es.
"""

from mqa_rdf.MQAevaluate import MQAevaluate
from SPARQLWrapper import SPARQLWrapper, JSON

import os
import ssl

import rdflib

OUTPUT = "output/"

ES_SPARQL = 'http://datos.gob.es/virtuoso/sparql'

def get_file_name(url):
    """
    https://europeandataportal.eu/set/data/https-opendata-aragon-es-datos-catalogo-dataset-oai-zaguan-unizar-es-89319
    return https-opendata-aragon-es-datos-catalogo-dataset-oai-zaguan-unizar-es-89319
    """
    words = url.split('/')
    file_name = words[len(words)-1]
    return file_name

def load_lines(file, field = 0):
    vocabulary = []
    with open(file) as fp:
        for line in fp:
            word = line.strip()
            if word != '':
                vocabulary.append(word)
    return vocabulary

def parse_dataset(url, graph):
    """
    Parses the dataset with URL in the graph
    """
    id = get_file_name(url)
    rdf_url = 'https://datos.gob.es/apidata/catalog/dataset/'+ id + '.ttl'
    print(rdf_url)
    try:
        graph.parse(rdf_url, format="turtle")
    except Exception as err:
        print(f'Other error occurred: {err}')
    return graph

def parse_catalog(results, filename):
    graph = rdflib.Graph()
    for row in results["results"]["bindings"]:
        """s"""
        dataset = row["s"]["value"]
        graph = parse_dataset(dataset,graph)
    #graph.serialize(destination=filename, format='pretty-xml')
    graph.serialize(destination=filename, format='turtle')

def search_datasets_without_location(url, filename):
    sparql = SPARQLWrapper(url)
    sparql.setQuery("""
          PREFIX dct:<http://purl.org/dc/terms/>
          PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
          PREFIX dcat: <http://www.w3.org/ns/dcat#>
          SELECT DISTINCT ?s WHERE { 
            { ?s a dcat:Dataset . ?s dcat:keyword ?value . FILTER regex(str(?value), 'aurrekontua', 'i') . FILTER NOT EXISTS { ?s dct:spatial ?location }} 
            UNION {?s a dcat:Dataset . ?s dcat:keyword ?value . FILTER regex(str(?value), 'presupuesto', 'i') . FILTER NOT EXISTS { ?s dct:spatial ?location }} 
            UNION {?s a dcat:Dataset . ?s dcat:keyword ?value . FILTER regex(str(?value), 'pressuposto', 'i') . FILTER NOT EXISTS { ?s dct:spatial ?location }} 
            UNION {?s a dcat:Dataset . ?s dcat:keyword ?value . FILTER regex(str(?value), 'orzamento', 'i') . FILTER NOT EXISTS { ?s dct:spatial ?location }}
          }
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    parse_catalog(results,filename)

def search_datasets(url, filename, keyword1, keyword2, keyword3, keyword4):
    sparql = SPARQLWrapper(url)
    sparql.setQuery("""
          PREFIX dct:<http://purl.org/dc/terms/>
          PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
          PREFIX dcat: <http://www.w3.org/ns/dcat#>
          SELECT ?s WHERE {
            {   ?s a dcat:Dataset .
                ?s dcat:keyword ?value . 
                FILTER regex(str(?value), '"""+ keyword1 +"""', 'i')
            } UNION { 
                ?s a dcat:Dataset .
                ?s dcat:keyword ?value .
                FILTER regex(str(?value), '"""+ keyword2 +"""', 'i')
            } UNION { 
                ?s a dcat:Dataset .
                ?s dcat:keyword ?value .
                FILTER regex(str(?value), '"""+ keyword3 +"""', 'i')
            } UNION { 
                ?s a dcat:Dataset .
                ?s dcat:keyword ?value .
                FILTER regex(str(?value), '"""+ keyword4 +"""', 'i')
            }
          } 
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    parse_catalog(results,filename)


def search_datasets_with_location(url, filename, keyword,location):
    sparql = SPARQLWrapper(url)
    sparql.setQuery("""
          PREFIX dct:<http://purl.org/dc/terms/>
          PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
          PREFIX dcat: <http://www.w3.org/ns/dcat#>
          SELECT DISTINCT ?s WHERE { 
               ?s a dcat:Dataset . 
               ?s dcat:keyword ?value . 
               FILTER regex(str(?value), '"""+ keyword +"""', 'i') . 
               ?s dct:spatial <""" + location + """> .
          } 
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    parse_catalog(results,filename)

def transform_to_file_name(url):
    x = ":/\\."
    y = "____"
    table = url.maketrans(x, y)
    return url.translate(table)

def create_folder(ckan_url):
    if (not os.path.exists(OUTPUT)):
        os.mkdir(OUTPUT)
    ckan_folder = transform_to_file_name(ckan_url)
    output_path = os.path.join(OUTPUT,ckan_folder)
    if (not os.path.exists(output_path)):
        os.mkdir(output_path)
    return output_path

def presupuestos():
    folder = create_folder('es_budget')
    catalog_file_name = os.path.join(folder,'catalog.ttl')
    search_datasets(ES_SPARQL, catalog_file_name, 'presupuesto', 'aurrekontua', 'pressuposto', 'orzamento')
    exit(0)
    mqaEvaluate = MQAevaluate(catalog_file_name, catalog_format= 'turtle', catalog_type = 'edp')
    mqaEvaluate.evaluate()

def presupuestos_por_territorio():
    vocabulary = load_lines('spatial.txt')
    for location in vocabulary:
        location_name = location.replace("http://datos.gob.es/recurso/sector-publico/territorio/","")
        folder = create_folder(location_name)
        catalog_file_name = os.path.join(folder,'catalog.ttl')
        search_datasets_with_location(ES_SPARQL, catalog_file_name, 'presupuesto',location)
        mqaEvaluate = MQAevaluate(catalog_file_name, catalog_format= 'turtle', catalog_type = 'edp')
        mqaEvaluate.evaluate()

def presupuestos_sin_territorio():
    folder = create_folder("es_without_spatial")
    catalog_file_name = os.path.join(folder,'catalog.ttl')
    search_datasets_without_location(ES_SPARQL, catalog_file_name)
    mqaEvaluate = MQAevaluate(catalog_file_name, catalog_format= 'turtle', catalog_type = 'edp')
    mqaEvaluate.evaluate()

if __name__ == '__main__':

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context


    presupuestos()
    presupuestos_por_territorio()
    presupuestos_sin_territorio()
