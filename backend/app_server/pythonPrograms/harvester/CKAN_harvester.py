"""
harvester/CKAN_harvester.py
Author: Javier Nogueras (jnog@unizar.es)
Last update: 2022-07-06

Program to harvest metadata records using a CKAN API. See https://docs.ckan.org/en/2.9/api/index.html#ckan.logic.action.get.package_search for additional parameters
"""

import os
import ssl


from urllib.request import urlopen
import json

import rdflib

HYDRA = "http://www.w3.org/ns/hydra/core#"

OUTPUT = "output"

LOCAL_CKAN = "http://localhost:5000/api/3/action/"

EDP_CKAN = 'https://data.europa.eu/data/search/ckan/'
EDP_RDF = 'https://data.europa.eu/data/api/datasets/'
EDP_FORMAT = '.ttl?useNormalizedId=true&locale=en'

#https://data.europa.eu/data/api/datasets/5fa93b994b29f6390f150980.ttl?useNormalizedId=true&locale=en

#https://data.europa.eu/data/api/datasets/5fa93b994b29f6390f150980.ttl
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

class CKAN_harvester:

    def __init__(self, url, rdf_url = None, limit = 10000, max_number_of_records = None, output_folder = OUTPUT, format = '.ttl'):
        self.url = url
        self.rdf_url = rdf_url
        self.limit = limit
        self.max_number_of_records = max_number_of_records
        self.output_folder = output_folder
        self.format = format

    def count_datasets(self):
        """
        Downloads the RDF in a paged JSON response with dataset identifiers
        """
        search_request = self.url + 'package_search?rows=0'
        print(search_request)
        try:
            response = urlopen(search_request)
            jsonResponse = json.load(response)
            count = jsonResponse["result"]["count"]
            return count
        except Exception as err:
            print(f'Other error occurred: {err}')

    def parse_dataset(self, id, graph):
        rdf_url = self.rdf_url + id + self.format
        # print(rdf_url)
        try:
            graph.parse(rdf_url, format="turtle")
        except Exception as err:
            print(f'Other error occurred: {err}')
        return graph

    def parse_catalog(self, results, file_name):
        rows = results["result"]["results"]
        graph = rdflib.Graph()
        for row in rows:
            graph = self.parse_dataset(row["id"], graph)
        # graph.serialize(destination=file_name, format='pretty-xml')
        graph.serialize(destination=file_name, format='turtle')

    def download_datasets(self, file_name, offset):
        """
        Downloads the RDF in a paged JSON response with dataset identifiers
        """
        search_request = self.url + 'package_search?rows='+str(self.limit)+'&start='+str(offset)+'&sort=%27id%20asc%27'
        print(search_request)
        response = urlopen(search_request)
        jsonResponse = json.load(response)
        self.parse_catalog(jsonResponse, file_name)

    def harvest(self):
        folder = create_folder(self.url)
        count = self.count_datasets()
        print (count, ' datasets')
        # exit(0)
        if self.max_number_of_records is not None:
            count = self.max_number_of_records
        offset = 0
        i=1
        while (offset < count):
            catalog_file_name = os.path.join(folder, 'catalog'+str(i)+'.ttl')
            self.download_datasets( catalog_file_name, offset)
            offset = offset + self.limit
            i = i + 1



if __name__ == '__main__':


    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    harvester = CKAN_harvester(url = LOCAL_CKAN, rdf_url= EDP_RDF, limit=500, max_number_of_records=5000, output_folder = OUTPUT, format = EDP_FORMAT)
    harvester.harvest()

