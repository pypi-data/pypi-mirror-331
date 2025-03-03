import numpy as np

# Total de puntos: número de puntos del texto entre número de palabras.
# Cuanto más próximo a uno, más lecturable, al implicar frases más cortas
def indicePuntos(texto):
    palabras = texto.split()
    numPal = len(palabras)
    puntos = texto.count('.')
    indice = puntos/numPal
    return indice

# Total de puntos y aparte: número de puntos y aparte del texto entre número de palabras
# Cuanto más próximo al índice de puntos, más lecturable, al implicar párrafos más cortos
def indicePuntoyAparte(texto):
    palabras = texto.split()
    numPal = len(palabras)
    puntosAparte = texto.count('.\n')
    indice = puntosAparte/numPal
    return indice

# Total de comas: número de comas del texto entre número de palabras
# Cuanto más próximo a cero más lecturable
def indiceComas(texto):
    palabras = texto.split()
    numPal = len(palabras)
    comas = texto.count(',')
    indice = comas/numPal
    return indice

import spacy
nlp = spacy.load('es_core_news_sm')
import pandas as pd

def indiceExtension(texto):
    doc = nlp(texto)
    etiquetas_lexicas = {'NOUN', 'VERB', 'ADJ', 'ADV', 'ADP'}
    numLexicas = 0
    numSilabas = 0
    for token in doc:
        if token.pos_ in etiquetas_lexicas:
            numLexicas = numLexicas +1
            numSilabas = numSilabas + len(a.inserted(str(token)).split('-'))
    indice = numSilabas/numLexicas
    return indice

# Índice de palabras trisílabas y polisílabas: cociente entre el número de palabras trisílabas y polisílabas y el número de palabras léxicas.
# Cuanto más próximo a cero más lecturable
def indiceTriPoli(texto):
    doc = nlp(texto)
    etiquetas_lexicas = {'NOUN', 'VERB', 'ADJ', 'ADV', 'ADP'}
    palabras = texto.split()
    numPal = len(palabras)
    palabrasPoli = 0
    for p in palabras:
        numSilabas = len(a.inserted(p).split('-'))
        if numSilabas >= 3:
            palabrasPoli = palabrasPoli+1
    palabrasLexicas = 0
    for token in doc:
        if token.pos_ in etiquetas_lexicas:
            palabrasLexicas = palabrasLexicas + 1
    indice = palabrasPoli/palabrasLexicas
    return indice

# Índice de palabras trisílabas y polisílabas léxicas: cociente entre el número de palabras trisílabas y polisílabas léxicas y el número de palabras léxicas.
# Cuanto más próximo a cero más lecturable
def indiceTriPoliLexica(texto):
    doc = nlp(texto)
    etiquetas_lexicas = {'NOUN', 'VERB', 'ADJ', 'ADV', 'ADP'}
    palabrasPoli = 0
    palabrasLexicas = 0
    for token in doc:
        if token.pos_ in etiquetas_lexicas:
            palabrasLexicas = palabrasLexicas + 1
            numSilabas = len(a.inserted(str(token)).split('-'))
            if numSilabas >= 3:
                palabrasPoli = palabrasPoli + 1
    indice = palabrasPoli/palabrasLexicas
    return indice

# Índice de diversidad de palabras: cociente entre el número de palabras diferentes del texto y el total de palabras.
# Un número próximo a cero implica una excesiva redundancia de términos iguales, que origina un texto tedioso, mientras que un número próximo a uno significa una gran diversidad, que lo hace menos lecturable
def indiceDiversidad(texto):
    palabras = texto.split()
    numPal = len(palabras)
    palDistintas = len(set(palabras))
    indice = palDistintas/numPal
    return indice


# Índice de frencuencia léxica: cociente entre el número de palabras léxicas de baja frecuencia y el número de palabras léxicas.
# (se tomarán como referencia el "Corpus de la Real Academia Española" (CREA) y el "Gran diccionario del uso del español actual")
# Cuanto más próximo a cero, menor uso de palabras infrecuentes y más lecturable
def indiceFrecLexica(texto):
    numLexicas = 0
    bajaFrecuencia = 0
    doc = nlp(texto)
    etiquetas_lexicas = {'NOUN', 'VERB', 'ADJ', 'ADV', 'ADP'}
    palabras =  []
    with open('crea_1000.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            palabras.append(row['palabra'])
    for token in doc:
        if token.pos_ in etiquetas_lexicas:
            numLexicas = numLexicas +1
            #Comprobamos si sa palabra está en el diccionario
            
            if str(token) not in palabras:
                bajaFrecuencia = bajaFrecuencia +1
            
    indice = bajaFrecuencia/numLexicas
    return indice


# Índice de palabras por frase: cociente resultado de la división entre el número de palabras del texto y el número de oraciones.
# Para que un texto sea de lectura fácil, la extensión de las oraciones debe estar entre 15 y 20 palabras como máximo.
def indicePalFrase(texto):
    palabras = texto.split()
    numPal = len(palabras)
    frases = texto.split('.')
    if frases[-1]=='\n':
        numFrases = len(frases)-1 # Por si solo hay un salto de línea después del punto
    else:
        numFrases = len(frases)
    for frase in frases:
        if frase=='': # Para quitarnos las frases vacías (esto pasa si hay por ejemplo puntos suspensivos)
            numFrases = numFrases-1
    indice = numPal/numFrases # Mide el índice de palabras por frase
    return indice


# Índice global de complejidad oracional: resultado de dividir el número de oraciones entre el número de proposiciones
# El valor mínimo es 1 y el máximo es infinito, aunque por encima de 5 es complicado mantener la coherencia y la claridad en la expresión.
def indiceComplejidadOracional(texto):
    frases = texto.split('.')
    
    proposiciones = 0
    numFrases=0
    # Para cada frase vemos si es proposición o no
    for frase in frases:
        if frase!='': # Para quitarnos las frases vacías
            doc  = nlp(frase)

             # Regla 1: debe tener un verbo
            tiene_verbo = any(token.pos_== "VERB" for token in doc)

            # Regla 2: no doebe ser una pregunta, exclamación o imperativo
            es_enunciativa = not any(token.tag_ in ["INTJ", "IMP"] for token in doc)

            if tiene_verbo and es_enunciativa:
                proposiciones = proposiciones +1
                
            numFrases = numFrases+1
    if proposiciones!=0:
        indice = numFrases/proposiciones
        return indice
    else:
        return 999999
    
    
def fernandezHuerta(texto):
    palabras = texto.split()
    numPal = len(palabras)
    frases =  texto.split('.')
    numFrases = len(frases)
    numSilabas = 0
    for pal in palabras:
        numSilabas = numSilabas + len(a.inserted(pal).split('-'))
    p = 100  * numSilabas  / numPal
    f = 100*numFrases/numPal
    lecturabilidad = 206.84  - 0.6*p - 1.02*f
    return lecturabilidad


# Índice de complejidad silábica: cociente entre el número de sílabas de baja frecuencia y el número total de sílabas (referencia: "Diccionario de frecuencias de las unidades lingüísticas del castellano")
# Cuanto más próximo a cero más lecturable
def indiceComplejidad(texto):
    palabras = texto.split()
    silabasBajaFrec = []
    silabas =  []
    silbaja = 0
    for p in palabras:
        for i in a.inserted(p).split('-'):
            silabas.append(i)
    with open('silabas_frec_total.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        for row in reader:
            silabasBajaFrec.append(row['Column1'])
    silabasBajaFrec = silabasBajaFrec[2:]
    for silaba in silabas:
        if silaba not in silabasBajaFrec:
            silbaja = silbaja+1
    totalSilabas = len(silabas)
    indice = silbaja/totalSilabas
    return indice