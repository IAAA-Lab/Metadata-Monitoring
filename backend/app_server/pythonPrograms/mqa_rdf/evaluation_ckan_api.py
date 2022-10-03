"""
mqa/evaluation_ckan_api.py
Author: Javier Nogueras (jnog@unizar.es)
Last update: 2020-11-13

Program to test MQA evaluation: Evaluation of catalog RDF DCAT-AP metadata according to Metadata Quality Assessment methodology (https://www.europeandataportal.eu/mqa/methodology?locale=en)
   It uses either the dcat_catalog_search function of CKAN API (in case ckanext-dcat is correctly installed), or the package_search function of CKAN API
"""

from ckan.mqa.MQAevaluate import MQAevaluate
import os
import ssl
import sys

import requests
from requests.exceptions import HTTPError

from urllib.request import urlopen
import json

import rdflib

HYDRA = "http://www.w3.org/ns/hydra/core#"

OUTPUT = "local_evaluation"

def retrieve_hydra_value(graph, property):
    result = None
    hydra_type = rdflib.URIRef(HYDRA + "PagedCollection")
    for s, p, o in graph.triples((None, rdflib.namespace.RDF.type, hydra_type)):
        rdf_property = rdflib.term.URIRef(HYDRA + property)
        result = int(graph.value(s,rdf_property))
    return result

def parse_json_response(search_request, graph = None):
    """
    Parses the RDF contained as JSon response and adds it to the graph received as parameter
    """
    print(search_request)
    try:
        response = requests.get(search_request)
        response.raise_for_status()
        # access JSOn content
        jsonResponse = response.json()
        rdf_catalog = jsonResponse["result"]
        if graph is None:
            graph = rdflib.Graph()
        graph.parse(data=rdf_catalog,format="application/rdf+xml")
        return graph

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def catalog_search(ckan_url, file_name, keyword = 'trafair'):
    """
    Downloads the RDF in a paged JSON response
    """
    search_request = ckan_url + '/api/3/action/dcat_catalog_search?q='+keyword+'&format=rdf'
    graph = parse_json_response(search_request)

    items_per_page = retrieve_hydra_value(graph,'itemsPerPage')
    total_items = retrieve_hydra_value(graph,'totalItems')

    if (total_items > items_per_page):
        i = 2
        partial_count = items_per_page
        while (partial_count < total_items):
            search_request = ckan_url + '/api/3/action/dcat_catalog_search?q='+keyword+'&format=rdf&page='+str(i)
            parse_json_response(search_request,graph)
            partial_count = partial_count + items_per_page
            i = i + 1
    graph.serialize(destination=file_name,format='pretty-xml')

def package_search(ckan_url, file_name, keyword = 'trafair'):
    """
    Downloads the RDF in a paged JSON response with dataset identifiers
    """
    search_request = ckan_url + '/api/3/action/package_search?q='+keyword+'&rows=1000'
    print(search_request)
    try:
        response = urlopen(search_request)
        jsonResponse = json.load(response)
        rows = jsonResponse["result"]["results"]
        graph = rdflib.Graph()
        for row in rows:
            dataset_request = ckan_url + '/dataset/'+ row["name"] + '.rdf'
            print(dataset_request)
            graph.parse(dataset_request, format="application/rdf+xml")
        graph.serialize(destination=file_name, format='pretty-xml')
    except Exception as err:
        print(f'Other error occurred: {err}')

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

def zaragoza_evaluation():
    ckan_url = 'http://atila.unizar.es:3394'
    folder = create_folder(ckan_url)
    catalog_file_name = os.path.join(folder,'catalog.rdf')
    catalog_search(ckan_url, catalog_file_name)
    mqaEvaluate = MQAevaluate(catalog_file_name)
    mqaEvaluate.evaluate()

def tuscany_evaluation():
    ckan_url = 'http://dati.toscana.it'
    folder = create_folder(ckan_url)
    catalog_file_name = os.path.join(folder,'catalog.rdf')
    catalog_search(ckan_url, catalog_file_name)
    mqaEvaluate = MQAevaluate(catalog_file_name, catalog_type = 'edp')
    mqaEvaluate.evaluate()

def emilia_romagna_evaluation():
    ckan_url = 'https://dati.emilia-romagna.it'
    folder = create_folder(ckan_url)
    catalog_file_name = os.path.join(folder,'catalog.rdf')
    catalog_search(ckan_url, catalog_file_name)
    mqaEvaluate = MQAevaluate(catalog_file_name, catalog_type = 'edp')
    mqaEvaluate.evaluate()

def santiago_evaluation():
    ckan_url = 'https://datos.santiagodecompostela.gal/catalogo'
    folder = create_folder(ckan_url)
    catalog_file_name = os.path.join(folder,'catalog.rdf')
    package_search(ckan_url, catalog_file_name)
    mqaEvaluate = MQAevaluate(catalog_file_name, catalog_type = 'nti')
    mqaEvaluate.evaluate()


if __name__ == '__main__':


    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    zaragoza_evaluation()
    tuscany_evaluation()
    emilia_romagna_evaluation()
    santiago_evaluation()

