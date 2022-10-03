#!/usr/bin/python
# -*- coding: utf-8 -*-

# Separador de sílabas en Español traducido del C++ elaborado por:
# HERNÁNDEZ-FIGUEROA, Zenón; CARRERAS-RIUDAVETS, Francisco J.; RODRÍGUEZ-RODRÍGUEZ, Gustavo.
# Automatic syllabification for Spanish using lemmatization and derivation to solve the prefix’s prominence issue.
# Expert Systems with Applications, 2013, vol. 40, no 17, p. 7122-7131. Disponible en http://tip.iatext.ulpgc.es


# Código traducido del C++ y C# por Ureña-Cámara, Manuel A. Dpto. Ing. Cartográfica, Geodésica y Fotogrametría.
# Universidad de Jaén. maurena@ujaen.es
# Modificaciones realizadas para optimizar el código Python. Eliminación del lastword
# 2020. Modificaciones para adaptarlo a código Python 3

# Clase separadora de sílabas
class SeparadorDeSilabas:
    # Constantes
    openclosewithwrittenaccent = {u'á', u'Á', u'à', u'À',
                                  u'é', u'É', u'è', u'È',
                                  u'ó', u'Ó', u'ò', u'Ò'}
    openvowel = {u'a', u'A', u'e', u'E', u'o', u'O'}
    closevowelwithwrittenaccent = {u'í', u'Í', u'ì', u'Ì', u'ú', u'Ú', u'ù', u'Ù', u'ü', u'Ü'}
    closevowel = {u'i', u'I', u'u', u'U'}
    closevoweldieresis = closevowel.union({u'ü', u'Ü'})
    openvowelandcloseaccentvowel = openclosewithwrittenaccent.union(
        openvowel.union(closevowelwithwrittenaccent))

    """Constructor"""
    def __init__(self, word):
        self.posiciones = []
        self.pal = word
        self.len = len(self.pal)
        self.enctonica = False
        self.tonica = 0
        self.letraacentuada = -1
        # Process directly
        self.__procesar()

    """  Returns the number of syllables in a word """
    def numerodesilabas(self):
        return len(self.posiciones) - 1  # Positions include the last character not only the beginning

    """Devuelve un array con las posiciones de inicio de las sílabas de palabra"""
    def posicionsilabas(self):
        return self.posiciones

    """Obtener la lista de sílabas descompuestas"""
    def silabas(self):
        return [self.pal[self.posiciones[i]:self.posiciones[i + 1]] for i in range(0, len(self.posiciones) - 1)]

    """Devuelve la posición de la sílaba tónica de palabra"""
    def silabatonica(self):
        return self.tonica

    """Determina si una palabra está correctamente tildada
       Devuelve:
        0 - bien
        7 - varias tildes en la palabra tildada
        8 - aguda mal tildada
        9 - llana mal tildada
    """
    def bientildada(self):
        numsilabas = self.numerodesilabas()
        # Comprueba si hay más de una tilde en la palabra
        if sum([self.pal.lower().count(j) for j in u"áéíóú"]) > 1:
            return 7

        postonica = self.posiciones[numsilabas + 1]

        if (numsilabas - postonica) < 2:
            # Si la palabra no es esdrújula
            ultcar = self.pal[-1]
            if postonica < numsilabas:
                final = self.posiciones[postonica + 1]
            else:
                final = self.len
            final = final - self.posiciones[postonica]
            silaba = self.pal[self.posiciones[postonica]: final].lower()

            # Se busca si hay tilde en la sílaba tónica
            for pos in range(0, len(self.posiciones)):
                if "áéíóú".find(silaba[pos]) != -1:
                    if pos < len(silaba):
                        # Hay tilde en la sílaba tónica
                        # La palabra es aguda y no termina en n, s, vocal -> error
                        if (postonica == numsilabas) and ("nsáéíióúu".find(ultcar) == -1):
                            return 8

                        # La palabra es llana y termina en n, s, vocal -> error
                        if (postonica == numsilabas - 1) and ("nsaeiou".find(ultcar) != -1):
                            return 9
                    return 0

        return 0  # La palabra está correctamente tildada


    """Imprimir el resultado de la descomposición en sílabas"""
    def imprime(self):
        print (self.pal)
        print (u'Número silábas', self.numerodesilabas())
        print (u'Sílabas', self.posiciones, self.silabas())
        print (u'Sílaba tónica', self.silabatonica())

    # Métodos privados
    """Devuelve un array con las posiciones de inicio de las sílabas de palabra (versión privada)"""
    def __procesar(self):
        #  Buscamos las sílabas
        pos = 0
        while pos < self.len:
            self.posiciones.append(pos)  # Marcamos el inicio de la sílaba actual

            # Las sílabas tiene 3 partes: ataque, núcleo y coda
            pos = self.__ataque(pos)
            pos = self.__nucleo(pos)
            pos = self.__coda(pos)

            if self.enctonica and (self.tonica == 0):
                self.tonica = len(self.posiciones)  # It marks the stressed syllable
        # Insert the last character (this changes length + 1)
        self.posiciones.append(self.len)
        # If the word has not written accent, the stressed syllable is determined
        # according to the stress rules
        if not self.enctonica:
            if len(self.posiciones) < (2 + 1):
                self.tonica = len(self.posiciones)  # Monosyllables
            else:
                # Polysyllables
                letrafin = (self.pal[self.len - 1]).lower()
                letraant = (self.pal[self.len - 2]).lower()

                if not self.__isconsonant(letrafin) or (letrafin == u'y') or \
                   (letrafin in u'ns' and not self.__isconsonant(letraant)):
                    self.tonica = len(self.posiciones) - 1 - 1  # Stressed penultimate syllable
                else:
                    self.tonica = len(self.posiciones) - 1  # Stressed last syllable

    """Determina si existe hiato"""
    def __hiato(self):
        acentuada = (self.pal[self.letraacentuada]).lower()

        # Hiatus is only possible if there is accent
        if ((self.letraacentuada > 1) and (self.pal[self.letraacentuada - 1].lower() == u'u') and
                (self.pal[self.letraacentuada - 2].lower() == u'q')):
            return False  # The 'u' letter belonging "qu" doesn't form hiatus

        # The central character of a hiatus must be a close - vowel with written accent
        if acentuada in u'íìúù':
            if (self.letraacentuada > 0) and self.__openvowel(self.pal[self.letraacentuada - 1]):
                return True
            if (self.letraacentuada < (self.len - 1)) and self.__openvowel(self.pal[self.letraacentuada + 1]):
                return True

        return False

    """Determina el ataque de la silaba de pal que empieza en pos y avanza pos hasta la 
       posición siguiente al final de dicho ataque
       La función se ha modificado para no usar variables por referencia ya que
       devuelve la posición modificada
    """
    def __ataque(self, pos):
        # Se considera que todas las consonantes iniciales forman parte del ataque
        ultconsonante = u'a'
        while (pos < self.len) and ((self.__isconsonant(self.pal[pos])) and ((self.pal[pos]).lower() != u'y')):
            ultconsonante = self.pal[pos].lower()
            pos = pos + 1

        # (q | g) + u (ejemplo: queso, gueto)
        if pos < self.len - 1:
            if self.pal[pos].lower() == u'u':
                if ultconsonante == u'q':
                    pos = pos + 1
                else:
                    if ultconsonante == u'g':
                        letra = self.pal[pos + 1].lower()
                        if letra in u'eéií':
                            pos = pos + 1
        else:
            # The 'u' with diaeresis is added to the consonant
            if self.pal[pos] in u'üÜ':
                if ultconsonante == u'g':
                    pos = pos + 1
        return pos

    """Determina el núcleo de la silaba de pal cuyo ataque termina en pos - 1 y avanza pos
       hasta la posición siguiente al final de dicho núcleo
       Al igual que en el resto de funciones pos es por valor
    """
    def __nucleo(self, pos):
        # Sirve para saber el tipo de vocal anterior cuando hay dos seguidas
        # 0 = fuerte
        # 1 = débil acentuada
        # 2 = débil
        previa = 0

        if pos >= self.len:
            return pos  # ¡¿No tiene núcleo?!

        # Se salta una 'y' al principio del núcleo, considerándola consonante
        if self.pal[pos].lower() == u'y':
            pos = pos + 1

        # Primera vocal
        if pos < self.len:
            # Orden cambiado para que funcione el case como en C++ y C#
            # Vocal débil acentuada, rompe cualquier posible diptongo
            if self.pal[pos] in self.closevowelwithwrittenaccent:
                self.letraacentuada = pos
                self.enctonica = True
                return pos + 1
            # Vocal fuerte o débil acentuada
            if self.pal[pos] in self.openclosewithwrittenaccent:
                self.letraacentuada = pos
                self.enctonica = True
                previa = 0
                pos = pos + 1
            elif self.pal[pos] in self.openvowel:
                previa = 0
                pos = pos + 1
            elif self.pal[pos] in self.closevowel:
                # Vocal débil
                previa = 2
                pos = pos + 1

        # 'h' intercalada en el núcleo, no condiciona diptongos o hiatos
        hache = False
        if pos < self.len:
            if self.pal[pos].lower() == u'h':
                pos = pos + 1
                hache = True

        # Segunda vocal
        if pos < self.len:
            # Vocal fuerte o débil acentuada
            if self.pal[pos] in self.openclosewithwrittenaccent:
                self.letraacentuada = pos
                if previa != 0:
                    self.enctonica = True
                    pos = pos + 1
                else:
                    # Dos vocales fuertes no forman silaba
                    if hache:
                        return pos - 1
            # Vocal fuerte
            elif self.pal[pos] in self.openvowel:
                if previa == 0:
                    # Dos vocales fuertes no forman silaba
                    if hache:
                        return pos - 1
                else:
                    pos = pos + 1
            # Vocal débil acentuada, no puede haber triptongo, pero si diptong
            elif self.pal[pos] in self.closevowelwithwrittenaccent:
                self.letraacentuada = pos
                if previa != 0:
                    # Se forma diptongo
                    self.enctonica = True
                    pos = pos + 1
                else:
                    if hache:
                        pos = pos - 1
                return pos
            #  Vocal débil
            elif self.pal[pos] in self.closevowel:
                if pos < self.len - 1:
                    # ¿Hay tercera vocal?
                    if not self.__isconsonant(self.pal[pos + 1]):
                        if self.pal[pos - 1].lower() == u'h':
                            pos = pos - 1
                        return pos
                # Two equals close - vowels don't form diphthong
                if self.pal[pos] != self.pal[pos - 1]:
                    pos = pos + 1

                return pos  # Es un diptongo plano o descendente

        # ¿tercera vocal?
        if pos < self.len:
            if self.pal[pos].lower() in u'iu':
                # Vocal débil
                return pos + 1  # Es un triptongo

        # Por defecto ya se ha resuelto
        return pos

    """Determina la coda de la silaba de pal cuyo núcleo termina en pos - 1 y avanza pos
       hasta la posición siguiente al final de dicha coda"""
    def __coda(self, pos):
        if (pos >= self.len) or (not self.__isconsonant(self.pal[pos])):
            return pos  # No hay coda
        else:
            if pos == self.len - 1:
                # Final de palabra
                return pos + 1
            # Si sólo hay una consonante entre vocales, pertenece a la siguiente silaba
            if not self.__isconsonant(self.pal[pos + 1]):
                return pos
            c1 = (self.pal[pos]).lower()
            c2 = (self.pal[pos + 1]).lower()

            # ¿Existe posibilidad de una tercera consonante consecutina?
            if pos < self.len - 2:
                c3 = (self.pal[pos + 2]).lower()

                if not self.__isconsonant(c3):
                    # No hay tercera consonante
                    # Los grupos ll, lh, ph, ch y rr comienzan silaba
                    if (c1 + c2) in [u'll', u'ch', u'rr']:
                        return pos
                    # A consonant + 'h' begins a syllable, except for groups sh and rh
                    if (c1 != u's') and (c1 != u'r') and (c2 == u'h'):
                        return pos

                    # Si la y está precedida por s, l, r, n ó c (consonantes alveolares),
                    # una nueva silaba empieza en la consonante previa, si no, empieza en la y
                    if c2 == u'y':
                        if c1 in u'slrnc':
                            return pos
                        return pos + 1

                    # grupos: gl - kl - bl - vl - pl - fl - tl
                    if (c1 in u'bvckfgpt') and (c2 == u'l'):
                        return pos

                    # grupos: gr - kr - dr - tr - br - vr - pr - fr (y cr?)
                    if (c1 in u'bvcdkfgpt') and (c2 == u'r'):
                        return pos

                    return pos + 1
                else:
                    # Hay tercera consonante
                    if (pos + 3) == self.len:
                        # Tres consonantes al final ¿palabras extranjeras?
                        if c2 == u'y':
                            # 'y' como vocal
                            if c1 in u'slrnc':
                                return pos
                        if c3 == u'y':
                            # 'y' final funciona como vocal con c2
                            pos = pos + 1
                        else:
                            # Tres consonantes al final ¿palabras extranjeras?
                            pos = pos + 3
                        return pos
                    if c2 == u'y':
                        # 'y' as vowel
                        if c1 in u'slrnc':
                            return pos
                        return pos + 1

                    # Los grupos pt, ct, cn, ps, mn, gn, ft, pn, cz, tz, ts comienzan silaba (Bezos)
                    # Ojo, he modificado tz que no estaba
                    if (c2+c3) in [u'pt', u'ct', u'cn', u'ps', u'mn', u'gn', u'ft', u'pn', u'cz', u'tz', u'ts']:
                        return pos + 1
                    # Los grupos consonánticos formados por una consonante seguida de 'l' o 'r'
                    # no pueden separarse y siempre inician sílaba
                    # También ch o y como vocal
                    if c3 in u'lry' or ((c2 == u'c') and (c3 == u'h')):
                        pos = pos + 1  # Following syllable begins in c2
                    else:
                        pos = pos + 2  # c3 begins the following syllable
            else:
                if c2 == u'y':
                    return pos
                pos = pos + 2  # The word ends with two consonants
        return pos

    """Determines whether c is a open - vowel or close vowel with written accent"""
    def __openvowel(self, c):
        return c in self.openvowelandcloseaccentvowel

    """Determines whether c is a vowel both open or close"""
    def __isconsonant(self, c):
        return not (c in self.openvowelandcloseaccentvowel.union(self.closevoweldieresis))



if __name__ == '__main__':
    # Test consonantes y vocales
    print ('a es vocal fuerte?', 'a' in SeparadorDeSilabas.openvowelandcloseaccentvowel)
    print ('i es vocal fuerte?', 'i' in SeparadorDeSilabas.openvowelandcloseaccentvowel)
    print ('a es consonante?', not ('a' in SeparadorDeSilabas.openvowelandcloseaccentvowel.union(SeparadorDeSilabas.closevoweldieresis)))
    print ('c es consonante?', not ('c' in SeparadorDeSilabas.openvowelandcloseaccentvowel.union(SeparadorDeSilabas.closevoweldieresis)))
    # Test
    palabra = SeparadorDeSilabas(u"murciélago")
    palabra.imprime()

    palabra2 = SeparadorDeSilabas(u"estruendo")
    palabra2.imprime()

    palabra3 = SeparadorDeSilabas(u"camión")
    palabra3.imprime()

    palabra4 = SeparadorDeSilabas(u"transportar")
    palabra4.imprime()