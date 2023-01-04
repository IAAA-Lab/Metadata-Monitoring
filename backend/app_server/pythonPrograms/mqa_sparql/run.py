"""
mqa_sparql/run.py
Author: Javier Nogueras (jnog@unizar.es), Javier Lacasta (jlacasta@unizar.es), Manuel Ureña (maurena@ujaen.es), F. Javier Ariza (fjariza@ujaen.es)
Last update: 2020-04-21

Main program to test MQA evaluation: Evaluation of catalog RDF DCAT-AP metadata according to Metadata Quality Assessment methodology (https://www.europeandataportal.eu/mqa/methodology?locale=en)
"""

from MQAevaluate import MQAevaluate
import os, ssl, sys
from datetime import datetime


if __name__ == '__main__':
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # len - 1 to delete argv[0] (for testing purposes)
    if len(sys.argv)-1 == 0:
        # URL = 'http://datos.gob.es/virtuoso/sparql'
        URL = 'http://localhost:3030/ckan_local'
        # date in YYYY-MM-DD HH-mm-ss format
        date = datetime.now().strftime('%Y-%d-%m')
        filename = 'testMQA - ' + datetime.now().strftime('%Y-%d-%m %H:%M:%S') + '.ttl'
    else:
        URL = sys.argv[1]
        filename = sys.argv[2]
        date = sys.argv[3]


    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    # url = 'https://datosgob.iaaa.es/db/query'
    # user = 'admin'
    # passwd = ''
    # mqaEvaluate = MQAevaluate(url, user, passwd, 'datosgobes20190612.rdf', 'dcat-ap.shapes.ttl',)
    # mqaEvaluate.evaluate()
    #
    # exit(0)

    print("\nCURRENT")
    mqaCurrent = MQAevaluate(URL, filename=filename, date=date)
    mqaCurrent.evaluate()