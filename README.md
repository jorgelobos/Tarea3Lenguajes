# Tarea3Lenguajes

Implementaremos el lenguaje del curso en un lenguaje NO funcional (Python). Específicamente, implementaremos el parser, interp y run.

## Empezando



### Prerequisites

Para esta tarea descargamos las librerias nltk y sexpdata, ya sea desde
```
pip install nltk
pip install sexpdata
```
O desde pypi

* [nltk](https://pypi.python.org/pypi/nltk) - Natural Language Toolkit
* [Sexpdata](https://pypi.python.org/pypi/sexpdata) - Sexpdata

Además, usamos una librería llamada [Racython](https://github.com/ddworken/racython) que fue modificada para efectos de la tarea.


### Ejecutando

Una vez hecho lo anterior, para correr la tarea solo es necesario el siguiente comando

```
python tarea3.py <tu expresion en Racket>
```

Por ejemplo, la siguiente expresión debe retornar 6

```
python tarea3.py "(if0 (< 5 0) 5 6)"
```

## Corriendo los tests

Solamente debes hacer el comando a continuación, el que arrojará tres errores. Esto es intencional dado los errores de identificador libre.
```
python testingRacython.py
```

## Github

Este proyecto además está almacenado en mi [Github](https://github.com/jorgelobos/Tarea3Lenguajes) personal.