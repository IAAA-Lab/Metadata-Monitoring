"""
iso19157/run.py
Author: Javier Nogueras
Last update: 2020-04-14

Main program to test ISO19157 evaluation
"""

from ISO19157Evaluation import ISO19157Evaluation
import os, ssl



if __name__ == '__main__':

    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    #url = 'https://datosgob.iaaa.es/db/query'
    #user = 'admin'
    #passwd = ''
    # url = 'http://155.210.155.161:3030/db/query'
    # user = 'admin'
    # passwd = ''
    #
    # evaluation = ISO19157Evaluation(url, user, passwd, 'datosgobes20190612.rdf', 'dcat-ap.shapes.ttl',)
    # evaluation.evaluate()
    #
    # exit(0)

    print("\nCURRENT")
    evaluationCurrent = ISO19157Evaluation('http://datos.gob.es/virtuoso/sparql')
    evaluationCurrent.evaluate()
    print("\nFin de la evaluación")
