#!/usr/bin/python
# -*- coding: utf-8 -*-

# Indice de perspicuidad
# Ureña-Cámara, Manuel A. Dpto. Ing. Cartográfica, Geodésica y Fotogrametría.
# Universidad de Jaén. maurena@ujaen.es
# El índice de Flesh:
# IF = 206.836 - 1.015 * N(palabras) / N(oraciones) - 84.6 * N(sílabas) / N(palabras)
#
# El índice de perspicuidad es una modificación del índice de Flesh hecha por Fernandez-Huertas para
# ser adatpado al español:
# IF_FH = 206.835 - 1.015 * N(palabras) / N(oraciones) - 60.0 * N(sílabas) / N(palabras)
#
# Además se calcula el índice de Szigiriszt-Pazos
# IP = 206.835 - N(palabras) / N(oraciones) - 62.3 * N(sílabas) / N(palabras)
# 2020.04.30 maurena
# - Simplificación para el uso con el software de IAAA
# 2020. maurena
# - Modificación para el cálculo desde una entrada de texto
# - Adaptación a python 3
# - Inclusión de pandas para simplificar las operaciones
#

# Importaciones generales
import re
import io
import sys

# Código del separador de sílabas
from SeparadorDeSilabas3 import SeparadorDeSilabas

# Clase para la determinación de los índices de legibilidad
class DeterminarIndices:
    def __init__(self, c):
        self.cadena = c
        self.i_f, self.i_f_fh, self.i_p = 0, 0, 0
        self.Npal, self.Norac, self.Npal = 0, 0, 0
        self.palabras, self.oraciones, self.silabas = [], [], {}
        self.__procesar()

    def imprime(self):
        print (self.cadena)
        print (u"Número oraciones", self.Norac)
        print (u"Número palabras", self.Npal)
        print (u"Número sílabas", self.Nsil)
        print (u"Indice Flesh", self.i_f)
        print (u"Indice Flesh_Fernandez_Huertas", self.i_f_fh)
        print (u"Indice Perspicuidad", self.i_p)
    
    def returnmax(self):
        return max(self.i_f_fh, self.i_p)

    def export(self):
        return {'oraciones': self.Norac, 'palabras': self.Npal, 'silabas': self.Nsil, 'flesh_en': self.i_f, 'flesh_es': self.i_f_fh, 'perspicuidad': self.i_p}

    def __procesar(self):
        # Vamos a determinar el número de oraciones. Una oración vamos a separarlas exclusivamente por puntos
        # pero como pueden existir acrónimos. Suponemos que una oración tiene que tener al menos 5 caracteres
        # + 2 por los espacioes
        oraciones = self.cadena.split('.')
        self.oraciones = []
        i = 0
        while i < len(oraciones):
            o = oraciones[i]
            i = i + 1
            while (i < len(oraciones)) and (len(oraciones[i]) < 5):
                o = o + oraciones[i]
                i = i + 1
            self.oraciones.append(o)

        self.Norac = len(self.oraciones)

        # Ahora determinamos las palabras
        palabras = list(filter(None, re.split(r"[, \.\r\n\-!?:]+", self.cadena)))
        self.Npal = len(palabras)

        # Ahora determinamos el número de sílabas
        self.Nsil = 0
        for i in palabras:
            try:
                o = SeparadorDeSilabas(i)
                self.Nsil = self.Nsil + o.numerodesilabas()
                self.silabas[i] = o.silabas()
            except:
                # A estos errores les añadimos sólo una
                self.Nsil = self.Nsil + 1
                self.silabas[i] = i

        # Determinamos los índices
        if self.Norac > 0 and self.Npal > 0:
            self.i_f = 206.835 - 1.015 * self.Npal / self.Norac - 84.6 * self.Nsil / self.Npal
            self.i_f_fh = 206.835 - 1.015 * self.Npal / self.Norac - 60.0 * self.Nsil / self.Npal
            self.i_p = 206.835 - self.Npal / self.Norac - 62.3 * self.Nsil / self.Npal
