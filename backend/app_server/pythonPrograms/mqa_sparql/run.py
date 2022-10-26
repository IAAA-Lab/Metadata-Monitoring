"""
mqa_sparql/run.py
Author: Javier Nogueras (jnog@unizar.es), Javier Lacasta (jlacasta@unizar.es), Manuel Ureña (maurena@ujaen.es), F. Javier Ariza (fjariza@ujaen.es)
Last update: 2020-04-21

Main program to test MQA evaluation: Evaluation of catalog RDF DCAT-AP metadata according to Metadata Quality Assessment methodology (https://www.europeandataportal.eu/mqa/methodology?locale=en)
"""

from mqa_sparql.MQAevaluate import MQAevaluate
import os, ssl



if __name__ == '__main__':

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    url = 'https://datosgob.iaaa.es/db/query'
    user = 'admin'
    passwd = ''
    mqaEvaluate = MQAevaluate(url, user, passwd, 'datosgobes20190612.rdf', 'dcat-ap.shapes.ttl',)
    mqaEvaluate.evaluate()

    exit(0)

    print("\nCURRENT")
    mqaCurrent = MQAevaluate('http://datos.gob.es/virtuoso/sparql')
    mqaCurrent.evaluate()
