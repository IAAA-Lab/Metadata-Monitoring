"""
mqa/run.py
Author: Javier Nogueras (jnog@unizar.es)
Last update: 2020-11-13

MQA evaluation of Spanish metadata about budget harvested by EDP.
"""

from mqa_rdf.MQAevaluate import MQAevaluate
from SPARQLWrapper import SPARQLWrapper, JSON

import os
import ssl

import rdflib

OUTPUT = "output/"

EDP_SPARQL = 'https://www.europeandataportal.eu/sparql'

def get_file_name(url):
    """
    https://europeandataportal.eu/set/data/https-opendata-aragon-es-datos-catalogo-dataset-oai-zaguan-unizar-es-89319
    return https-opendata-aragon-es-datos-catalogo-dataset-oai-zaguan-unizar-es-89319
    """
    words = url.split('/')
    file_name = words[len(words)-1]
    return file_name



def parse_dataset(url, graph):
    """
    Parses the dataset with URL in the graph
    """
    id = get_file_name(url)
    # https://www.europeandataportal.eu/data/api/datasets/https-opendata-aragon-es-datos-catalogo-dataset-oai-zaguan-unizar-es-94411.ttl?useNormalizedId=true&locale=en
    ttl_url = 'https://www.europeandataportal.eu/data/api/datasets/'+ id + '.ttl?useNormalizedId=true&locale=en'
    print(ttl_url)
    try:
        graph.parse(ttl_url, format="turtle")
    except Exception as err:
        print(f'Other error occurred: {err}')
    return graph

def parse_catalog(results, filename):
    graph = rdflib.Graph()
    for row in results["results"]["bindings"]:
        """s"""
        dataset = row["s"]["value"]
        graph = parse_dataset(dataset,graph)
    # graph.serialize(destination=filename, format='pretty-xml')
    graph.serialize(destination=filename, format='turtle')

def search_datasets(url, filename, keyword1, keyword2, keyword3, keyword4, publisher):
    sparql = SPARQLWrapper(url)
    sparql.setQuery("""
          PREFIX dct:<http://purl.org/dc/terms/>
          PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
          PREFIX dcat: <http://www.w3.org/ns/dcat#>
          SELECT DISTINCT ?s WHERE { 
            {
               ?s a dcat:Dataset . 
               ?s dcat:keyword ?value . 
               FILTER regex(str(?value), '"""+ keyword1 +"""', 'i') . 
               ?s dct:publisher ?publisher .
               FILTER regex(str(?publisher), '"""+ publisher +"""', 'i') . 
            } UNION { 
                ?s a dcat:Dataset .
                ?s dcat:keyword ?value .
                FILTER regex(str(?value), '"""+ keyword2 +"""', 'i') .
                ?s dct:publisher ?publisher .
                FILTER regex(str(?publisher), '"""+ publisher +"""', 'i') . 
             } UNION { 
                ?s a dcat:Dataset .
                ?s dcat:keyword ?value .
                FILTER regex(str(?value), '"""+ keyword3 +"""', 'i') .
                ?s dct:publisher ?publisher .
                FILTER regex(str(?publisher), '"""+ publisher +"""', 'i') . 
             } UNION { 
                ?s a dcat:Dataset .
                ?s dcat:keyword ?value .
                FILTER regex(str(?value), '"""+ keyword4 +"""', 'i') .
                ?s dct:publisher ?publisher .
                FILTER regex(str(?publisher), '"""+ publisher +"""', 'i') . 
             }
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

def edp_presupuestos_datos_gob_es():
    folder = create_folder('edp_budget')
    catalog_file_name = os.path.join(folder,'catalog.ttl')
    #publisher = 'http://datos.gob.es/recurso/sector-publico/org/Organismo/U02100001'
    publisher = 'datos.gob.es/recurso/sector-publico/org/Organismo'
    search_datasets(EDP_SPARQL, catalog_file_name, 'presupuesto', 'aurrekontua', 'pressuposto', 'orzamento', publisher)
    mqaEvaluate = MQAevaluate(catalog_file_name, catalog_format= 'turtle', catalog_type = 'edp')
    mqaEvaluate.evaluate()


if __name__ == '__main__':

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    edp_presupuestos_datos_gob_es()
