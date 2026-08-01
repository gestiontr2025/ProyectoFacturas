"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Archivo
-------
supplier_catalog.py

Descripción
-----------
Este módulo contiene el catálogo canónico de proveedores
conocidos por el Proyecto Facturas.

Los datos iniciales del catálogo fueron obtenidos a partir
del Excel de comprobantes recibidos correspondiente a la
empresa receptora:

    MADERO ROOF TOP S.A.

CUIT:

    30-71834746-3

Responsabilidades
-----------------
Este módulo se encarga de:

- Mantener la razón social oficial de cada proveedor.
- Mantener el CUIT oficial de cada proveedor.
- Mantener el nombre de fantasía cuando sea conocido.
- Registrar alias que pueden aparecer en los PDF.
- Registrar información fiscal observada históricamente.
- Permitir buscar proveedores por identificador.
- Permitir buscar proveedores por CUIT.
- Devolver candidatos encontrados dentro de un texto.
- Validar automáticamente la consistencia del catálogo.
- Evitar CUIT e identificadores duplicados.
- Evitar que la empresa receptora sea registrada como
  proveedor.
- Proteger los datos canónicos de Arta Verduleros.

Una única fuente de verdad
--------------------------
Los módulos que necesiten información oficial sobre los
proveedores deberán consultarla desde este archivo.

Por ejemplo:

- supplier_detector.py
- invoice_parser.py
- invoice_organizer.py
- futuros módulos de validación
- futuros módulos de renombrado
- futuros módulos de generación de reportes

La razón social o el CUIT de un proveedor no deberían
escribirse nuevamente dentro de esos módulos.

Esto evita que diferentes archivos contengan versiones
contradictorias de un mismo dato.

Datos canónicos y alias
-----------------------
Un dato canónico es el valor oficial que el sistema debe
guardar y mostrar.

Por ejemplo, para Arta:

    Razón social canónica:
        ARTA DE GONZALEZ S.R.L.

    Nombre de fantasía:
        Arta Verduleros

El texto defectuoso:

    AARTA DE GONZALEZ S.R.L.

puede conservarse como alias porque puede aparecer debido
al orden extraño del texto extraído desde algunos PDF.

Sin embargo, ese alias nunca debe utilizarse como razón
social oficial.

El sistema nunca debe producir valores como:

    AARTA VERDULEROS
    Aarta Verduleros

Perfil fiscal observado
------------------------
El catálogo contiene información observada en el Excel,
por ejemplo:

- Tipos de comprobante encontrados.
- Alícuotas de IVA encontradas.
- Monedas encontradas.
- Presencia de valores en la columna Otros Tributos.
- Cantidad de comprobantes observados.

Esta información es histórica y orientativa.

No significa que el proveedor esté obligado a emitir
siempre exactamente de esa manera.

Por ejemplo, si históricamente un proveedor emitió Factura
A, el programa no debe rechazar automáticamente una Nota de
Crédito A futura.

Otros tributos
--------------
El Excel utilizado agrupa diferentes conceptos dentro de
una columna llamada Otros Tributos.

Esa columna podría contener, según cada comprobante:

- Percepciones de IVA.
- Percepciones de Ingresos Brutos.
- Impuestos internos.
- Otros conceptos fiscales.

Como el Excel no permite separar esos componentes de forma
confiable, el catálogo solamente registra:

    otros_tributos_observados = True

No intenta determinar qué impuesto específico compone el
importe.

Programación defensiva
----------------------
Este archivo valida sus propios datos cuando es importado.

Si encuentra una inconsistencia, detiene el programa antes
de permitir que información incorrecta llegue al resto del
sistema.

Entre otras cosas, comprueba:

- Identificadores vacíos.
- Identificadores repetidos.
- Razones sociales vacías.
- CUIT con longitud incorrecta.
- CUIT duplicados.
- Monedas no contempladas.
- Alícuotas no contempladas.
- Cantidades negativas.
- Registro accidental del receptor como proveedor.
- Modificaciones incorrectas de los datos oficiales de
  Arta Verduleros.

Autor
-----
Diego (desarrollador del proyecto)
ChatGPT (mentor técnico)

==========================================================
"""


# ==========================================================
# INICIO DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ----------------------------------------------------------
# Esta importación modifica la forma en que Python procesa
# las anotaciones de tipos.
#
# Permite escribir anotaciones modernas como:
#
#     str | None
#     list[Proveedor]
#
# sin que Python necesite resolver inmediatamente todas las
# clases mencionadas.
#
# También ayuda a evitar algunos problemas cuando una clase
# se utiliza en anotaciones dentro del mismo archivo antes de
# que su definición haya terminado.
# ----------------------------------------------------------

from __future__ import annotations


# ----------------------------------------------------------
# Importamos el módulo re.
#
# re pertenece a la biblioteca estándar de Python y permite
# trabajar con expresiones regulares.
#
# En este módulo lo utilizaremos principalmente para:
#
# - Eliminar caracteres que no sean números de un CUIT.
# - Reemplazar puntuación y símbolos durante la
#   normalización de textos.
# - Reducir grupos de espacios consecutivos.
# - Preparar razones sociales y alias para comparaciones.
#
# Por ejemplo:
#
#     "HORECA S.R.L."
#
# podrá normalizarse como:
#
#     "HORECA S R L"
# ----------------------------------------------------------

import re


# ----------------------------------------------------------
# Importamos el módulo unicodedata.
#
# unicodedata pertenece a la biblioteca estándar.
#
# Nos permite normalizar caracteres Unicode y eliminar
# diferencias producidas por acentos.
#
# Por ejemplo:
#
#     "PIÑERO"
#
# podrá prepararse para búsqueda como:
#
#     "PINERO"
#
# Esto se utiliza solamente para comparar textos.
#
# La razón social canónica nunca se modifica ni pierde sus
# caracteres originales.
# ----------------------------------------------------------

import unicodedata


# ----------------------------------------------------------
# Importamos dataclass.
#
# Una dataclass permite crear una estructura especializada
# para almacenar información.
#
# En lugar de utilizar un diccionario genérico como:
#
#     {
#         "razon_social": "...",
#         "cuit": "..."
#     }
#
# podremos crear objetos de tipo Proveedor con campos
# claramente definidos:
#
#     proveedor.razon_social
#     proveedor.cuit
#
# Esto mejora:
#
# - La legibilidad.
# - El autocompletado del editor.
# - Las anotaciones de tipos.
# - La prevención de errores al escribir nombres de campos.
#
# También importamos replace.
#
# replace() permite crear una nueva copia de una dataclass
# modificando solamente algunos campos.
#
# Esto es necesario porque Proveedor utilizará frozen=True,
# lo cual impide modificar directamente sus atributos.
# ----------------------------------------------------------

from dataclasses import dataclass, replace


# ----------------------------------------------------------
# Importamos Iterable y Optional.
#
# Iterable indica que una función puede recibir cualquier
# colección que pueda recorrerse, por ejemplo:
#
# - list
# - tuple
# - dict_values
#
# Optional[str] significa que un dato puede contener:
#
# - Un texto.
# - None.
#
# None representa que el dato no está disponible o no fue
# confirmado.
# ----------------------------------------------------------

from typing import Iterable, Optional


# ----------------------------------------------------------
# Importamos business_config.
#
# business_config.py contiene los datos canónicos de la
# empresa receptora:
#
#     MADERO ROOF TOP S.A.
#     CUIT 30-71834746-3
#
# supplier_catalog.py lo utiliza para verificar que esa
# empresa no sea registrada accidentalmente como proveedor.
#
# Esto mantiene separadas dos responsabilidades:
#
# business_config.py:
#     Datos fijos de la empresa receptora.
#
# supplier_catalog.py:
#     Datos de los proveedores emisores.
# ----------------------------------------------------------

import business_config


# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE ESTRUCTURAS DE DATOS
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA CLASE Proveedor
# ----------------------------------------------------------

@dataclass(frozen=True)
class Proveedor:
    """
    Representar un proveedor conocido por el sistema.

    La clase utiliza:

        frozen=True

    Esto significa que un objeto Proveedor es inmutable.

    Una vez creado, otro módulo no puede hacer accidentalmente:

        proveedor.razon_social = "Otro nombre"

    Esa protección es importante porque estos valores se
    consideran datos canónicos del proyecto.

    Atributos
    ---------
    identificador:

        Nombre interno utilizado por el código.

        Ejemplo:

            arta_verduleros

        No es una razón social ni un nombre comercial.

    razon_social:

        Razón social oficial que el programa debe guardar y
        mostrar.

    nombre_fantasia:

        Nombre comercial conocido.

        Puede ser None cuando no se conoce o cuando no existe.

    cuit:

        CUIT canónico con formato:

            XX-XXXXXXXX-X

    tipos_comprobante_observados:

        Tipos de comprobante encontrados históricamente en el
        Excel.

        No representan una regla obligatoria.

    alicuotas_iva_observadas:

        Alícuotas de IVA encontradas históricamente.

        Ejemplos:

            10.5
            21.0

    otros_tributos_observados:

        True si al menos un comprobante del Excel tenía un
        importe en la columna Otros Tributos.

        No informa qué tipo específico de tributo era.

    monedas_observadas:

        Monedas encontradas históricamente.

        Actualmente se contemplan:

            ARS
            USD

    cantidad_comprobantes_observados:

        Cantidad de comprobantes del proveedor encontrados en
        el Excel utilizado para construir el catálogo.

    alias_busqueda:

        Variantes normalizadas que pueden utilizarse para
        reconocer al proveedor dentro de un texto.

        Los alias nunca reemplazan a la razón social oficial.
    """

    identificador: str
    razon_social: str
    nombre_fantasia: Optional[str]
    cuit: str

    tipos_comprobante_observados: tuple[str, ...] = ()
    alicuotas_iva_observadas: tuple[float, ...] = ()
    otros_tributos_observados: bool = False
    monedas_observadas: tuple[str, ...] = ()
    cantidad_comprobantes_observados: int = 0
    alias_busqueda: tuple[str, ...] = ()


    # ------------------------------------------------------
    # INICIO DE LA FUNCIÓN cuit_sin_guiones()
    # ------------------------------------------------------

    def cuit_sin_guiones(self) -> str:
        """
        Devolver el CUIT utilizando únicamente dígitos.

        Ejemplo
        -------
        Si el proveedor contiene:

            30-71867492-8

        la función devuelve:

            30718674928

        Esta forma resulta útil para comparar CUIT extraídos
        desde PDF que pueden aparecer:

        - Con guiones.
        - Sin guiones.
        - Con espacios.
        - Con puntos.
        """

        return "".join(
            caracter
            for caracter in self.cuit
            if caracter.isdigit()
        )

    # ------------------------------------------------------
    # FIN DE LA FUNCIÓN cuit_sin_guiones()
    # ------------------------------------------------------


    # ------------------------------------------------------
    # INICIO DE LA FUNCIÓN nombre_preferido()
    # ------------------------------------------------------

    def nombre_preferido(self) -> str:
        """
        Devolver el nombre más conveniente para mostrar.

        Prioridad
        ---------
        1. Nombre de fantasía, si existe.
        2. Razón social oficial.

        Ejemplo
        -------
        Para Arta devuelve:

            Arta Verduleros

        Para un proveedor sin nombre de fantasía devuelve su
        razón social.
        """

        return (
            self.nombre_fantasia
            or
            self.razon_social
        )

    # ------------------------------------------------------
    # FIN DE LA FUNCIÓN nombre_preferido()
    # ------------------------------------------------------


    # ------------------------------------------------------
    # INICIO DE LA FUNCIÓN convertir_a_diccionario()
    # ------------------------------------------------------

    def convertir_a_diccionario(self) -> dict:
        """
        Convertir el proveedor en un diccionario común.

        Esta conversión será útil más adelante para:

        - Mostrar información en la consola.
        - Guardar el catálogo en JSON.
        - Generar reportes.
        - Escribir datos en Excel.
        - Enviar información a otros módulos.

        Retorna
        -------
        dict

            Diccionario con todos los campos públicos del
            proveedor.
        """

        return {
            "identificador": self.identificador,
            "razon_social": self.razon_social,
            "nombre_fantasia": self.nombre_fantasia,
            "cuit": self.cuit,
            "cuit_sin_guiones": self.cuit_sin_guiones(),
            "tipos_comprobante_observados": (
                self.tipos_comprobante_observados
            ),
            "alicuotas_iva_observadas": (
                self.alicuotas_iva_observadas
            ),
            "otros_tributos_observados": (
                self.otros_tributos_observados
            ),
            "monedas_observadas": self.monedas_observadas,
            "cantidad_comprobantes_observados": (
                self.cantidad_comprobantes_observados
            ),
            "alias_busqueda": self.alias_busqueda,
        }

    # ------------------------------------------------------
    # FIN DE LA FUNCIÓN convertir_a_diccionario()
    # ------------------------------------------------------


# ----------------------------------------------------------
# FIN DE LA CLASE Proveedor
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE ESTRUCTURAS DE DATOS
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE FUNCIONES DE NORMALIZACIÓN
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN normalizar_texto_busqueda()
# ----------------------------------------------------------

def normalizar_texto_busqueda(valor: object) -> str:
    """
    Normalizar un valor para realizar búsquedas internas.

    Esta función transforma diferentes representaciones de un
    mismo texto en una forma comparable.

    Operaciones realizadas
    ----------------------
    1. Convierte el valor en texto.
    2. Normaliza caracteres Unicode.
    3. Elimina acentos.
    4. Convierte todo a mayúsculas.
    5. Reemplaza puntuación por espacios.
    6. Reduce espacios consecutivos.
    7. Elimina espacios de los extremos.

    Ejemplos
    --------
    Los textos:

        "HORECA S.R.L."
        "Horeca SRL"
        "HORECA S R L"

    pueden normalizarse a formas comparables.

    Importante
    ----------
    El resultado se utiliza únicamente para búsquedas.

    Nunca debe mostrarse como razón social oficial ni
    guardarse como dato canónico.

    Parámetros
    ----------
    valor:

        Cualquier valor que deseamos preparar para comparar.

    Retorna
    -------
    str

        Texto normalizado.

        Devuelve una cadena vacía si recibe None.
    """

    if valor is None:
        return ""

    # ------------------------------------------------------
    # NFKC unifica distintas representaciones Unicode que
    # visualmente pueden parecer iguales.
    # ------------------------------------------------------

    texto = unicodedata.normalize(
        "NFKC",
        str(valor)
    )

    # ------------------------------------------------------
    # NFD separa las letras de sus marcas de acentuación.
    #
    # Por ejemplo, conceptualmente:
    #
    #     Ñ
    #
    # se separa en:
    #
    #     N + marca diacrítica
    # ------------------------------------------------------

    texto = unicodedata.normalize(
        "NFD",
        texto
    )

    # ------------------------------------------------------
    # Eliminamos las marcas de acentuación.
    #
    # Esto facilita comparar textos provenientes de PDF que
    # pueden perder acentos durante la extracción.
    # ------------------------------------------------------

    texto = "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )

    # ------------------------------------------------------
    # Convertimos todo a mayúsculas para que la comparación
    # no dependa de mayúsculas y minúsculas.
    # ------------------------------------------------------

    texto = texto.upper()

    # ------------------------------------------------------
    # Reemplazamos cualquier carácter que no sea letra o
    # número por un espacio.
    #
    # Esto reduce diferencias entre:
    #
    #     S.R.L.
    #     S R L
    #     S-R-L
    # ------------------------------------------------------

    texto = re.sub(
        r"[^A-Z0-9]+",
        " ",
        texto
    )

    # ------------------------------------------------------
    # Reducimos varios espacios consecutivos a uno solo.
    # ------------------------------------------------------

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN normalizar_texto_busqueda()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN normalizar_cuit()
# ----------------------------------------------------------

def normalizar_cuit(cuit: object) -> Optional[str]:
    """
    Normalizar un CUIT al formato XX-XXXXXXXX-X.

    La función acepta valores como:

        30-71867492-8
        30718674928
        30 71867492 8

    Primero elimina cualquier carácter que no sea numérico.

    Luego comprueba que existan exactamente once dígitos.

    Parámetros
    ----------
    cuit:

        Valor que contiene el CUIT.

    Retorna
    -------
    str | None

        CUIT normalizado.

        Devuelve None si el valor no contiene exactamente
        once dígitos.
    """

    if cuit is None:
        return None

    digitos = "".join(
        caracter
        for caracter in str(cuit)
        if caracter.isdigit()
    )

    if len(digitos) != 11:
        return None

    return (
        f"{digitos[0:2]}-"
        f"{digitos[2:10]}-"
        f"{digitos[10]}"
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN normalizar_cuit()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN generar_alias_automaticos()
# ----------------------------------------------------------

def generar_alias_automaticos(
    razon_social: str,
    nombre_fantasia: Optional[str],
) -> tuple[str, ...]:
    """
    Generar alias de búsqueda a partir de datos canónicos.

    La función crea variantes básicas de la razón social:

    - Texto original.
    - Texto sin puntos.
    - Texto reemplazando puntos por espacios.

    Si existe nombre de fantasía, también lo incorpora.

    Luego todos los candidatos son normalizados mediante:

        normalizar_texto_busqueda()

    Los alias se guardan sin duplicados y ordenados.

    Importante
    ----------
    Los alias sirven únicamente para reconocimiento.

    Nunca deben sustituir:

    - La razón social oficial.
    - El nombre de fantasía oficial.
    - El CUIT oficial.

    Parámetros
    ----------
    razon_social:

        Razón social canónica.

    nombre_fantasia:

        Nombre comercial confirmado o None.

    Retorna
    -------
    tuple

        Tupla ordenada de alias normalizados.
    """

    candidatos = {
        razon_social,
        razon_social.replace(".", ""),
        razon_social.replace(".", " "),
    }

    if nombre_fantasia:

        candidatos.add(
            nombre_fantasia
        )

    alias = {
        normalizar_texto_busqueda(candidato)
        for candidato in candidatos
        if normalizar_texto_busqueda(candidato)
    }

    return tuple(
        sorted(alias)
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN generar_alias_automaticos()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE FUNCIONES DE NORMALIZACIÓN
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE DATOS EXTRAÍDOS DEL EXCEL
# ==========================================================


# ----------------------------------------------------------
# Cada registro de _DATOS_PROVEEDORES utiliza la siguiente
# estructura y el siguiente orden:
#
# 1. identificador interno
#
#       Nombre utilizado por el código.
#
# 2. razón social
#
#       Valor canónico oficial.
#
# 3. nombre de fantasía
#
#       Nombre comercial confirmado o None.
#
# 4. CUIT
#
#       CUIT canónico con guiones.
#
# 5. tipos de comprobante observados
#
#       Tipos encontrados históricamente en el Excel.
#
# 6. alícuotas de IVA observadas
#
#       Valores encontrados en los comprobantes.
#
# 7. otros tributos observados
#
#       True cuando al menos una fila del Excel tenía un
#       importe en Otros Tributos.
#
# 8. monedas observadas
#
#       Monedas encontradas históricamente.
#
# 9. cantidad de comprobantes observados
#
#       Cantidad de registros encontrados para el proveedor.
#
# Esta estructura compacta evita repetir muchas veces los
# nombres de los campos.
#
# Más adelante estos registros se convierten en objetos
# Proveedor, que sí tienen campos explícitos.
# ----------------------------------------------------------

_DATOS_PROVEEDORES = (
    (
        "alen_federico_hernan",
        "ALEN FEDERICO HERNAN",
        None,
        "20-38358039-1",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "all_online_solutions",
        "ALL ONLINE SOLUTIONS S. A. U.",
        "Colppy",
        "30-71246122-1",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "arta_verduleros",
        "ARTA DE GONZALEZ S.R.L.",
        "Arta Verduleros",
        "30-71867492-8",
        ("1 - Factura A",),
        (10.5,),
        False,
        ("ARS",),
        14,
    ),
    (
        "ayres_it_s_r_l",
        "AYRES IT S.R.L.",
        None,
        "30-71516351-5",
        (
            "1 - Factura A",
            "3 - Nota de Crédito A",
        ),
        (21.0,),
        False,
        ("ARS",),
        3,
    ),
    (
        "bodegas_chandon_s_a",
        "BODEGAS CHANDON S.A.",
        None,
        "30-50011889-6",
        ("1 - Factura A",),
        (21.0,),
        True,
        ("ARS",),
        1,
    ),
    (
        "bodegas_esmeralda_sociedad_anonima_s_a",
        "BODEGAS ESMERALDA SOCIEDAD ANONIMA S. A.",
        None,
        "30-50258442-8",
        ("1 - Factura A",),
        (21.0,),
        True,
        ("ARS",),
        5,
    ),
    (
        "buenos_ayres_vinos_y_bebidas_s_a",
        "BUENOS AYRES VINOS Y BEBIDAS S.A.",
        None,
        "30-70958506-8",
        (
            "1 - Factura A",
            "3 - Nota de Crédito A",
        ),
        (21.0,),
        True,
        ("ARS",),
        3,
    ),
    (
        "camargo_sergio_ariel",
        "CAMARGO SERGIO ARIEL",
        None,
        "20-27517198-1",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "campos_alves_ezequiel",
        "CAMPOS ALVES EZEQUIEL",
        None,
        "20-34188568-0",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "cantine_s_r_l",
        "CANTINE S.R.L",
        None,
        "30-71674025-7",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "ceballos_jose_ramon",
        "CEBALLOS JOSE RAMON",
        None,
        "20-22484356-6",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "cerveceria_y_malteria_quilmes",
        "CERVECERIA Y MALTERIA QUILMES S.A.I.C.A. Y G.",
        None,
        "33-50835825-9",
        (
            "1 - Factura A",
            "3 - Nota de Crédito A",
        ),
        (21.0,),
        True,
        ("ARS",),
        8,
    ),
    (
        "chesko_agustin_ezequiel",
        "CHESKO AGUSTIN EZEQUIEL",
        None,
        "20-36044835-6",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "cibones_s_a_s",
        "CIBONES S.A.S.",
        None,
        "30-71658907-9",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        3,
    ),
    (
        "coca_cola_femsa",
        "COCA COLA FEMSA DE BUENOS AIRES S A",
        None,
        "30-52539008-6",
        ("1 - Factura A",),
        (21.0,),
        True,
        ("ARS",),
        4,
    ),
    (
        "colman_tomas_agustin",
        "COLMAN TOMAS AGUSTIN",
        None,
        "20-42765269-7",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "corvalan_ariel_andres",
        "CORVALAN ARIEL ANDRES",
        None,
        "20-30345163-4",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "couto_fermin_alejo",
        "COUTO FERMIN ALEJO",
        None,
        "20-40551188-7",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "cuatro_carnes",
        "CUATRO CARNES S.R.L.",
        None,
        "33-71621542-9",
        ("1 - Factura A",),
        (10.5,),
        False,
        ("ARS",),
        5,
    ),
    (
        "daniel_a_chozas",
        "DANIEL A CHOZAS S A C I F",
        None,
        "30-53837370-9",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "davila_juan_ignacio",
        "DAVILA JUAN IGNACIO",
        None,
        "24-36502047-3",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "dba",
        "DISTRIBUIDORA DE BEBIDAS SRL",
        "DBA",
        "30-70942442-0",
        ("1 - Factura A",),
        (21.0,),
        True,
        ("ARS",),
        6,
    ),
    (
        "el_criollo",
        "DISTRIBUIDORA EL CRIOLLO SRL",
        "El Criollo",
        "30-70887901-7",
        ("1 - Factura A",),
        (
            10.5,
            21.0,
        ),
        True,
        ("ARS",),
        8,
    ),
    (
        "el_jumillano",
        "EL JUMILLANO S A",
        None,
        "30-53788287-1",
        ("1 - Factura A",),
        (21.0,),
        True,
        ("ARS",),
        5,
    ),
    (
        "emprendimientos_inmobiliarios_arenales",
        "EMPRENDIMIENTOS INMOBILIARIOS ARENALES SA",
        None,
        "30-69757899-9",
        ("1 - Factura A",),
        (21.0,),
        False,
        (
            "ARS",
            "USD",
        ),
        2,
    ),
    (
        "escobar_jorge_martin",
        "ESCOBAR JORGE MARTIN",
        None,
        "20-24460105-4",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "frigorifico_los_prados",
        "FRIGORIFICO LOS PRADOS SA",
        None,
        "30-70844445-2",
        ("1 - Factura A",),
        (10.5,),
        True,
        ("ARS",),
        5,
    ),
    (
        "garcia_juanico_rafael",
        "GARCIA JUANICO RAFAEL",
        None,
        "20-30958599-3",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "goodies_sa",
        "GOODIES SA",
        None,
        "30-71211914-0",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "green_delfina",
        "GREEN DELFINA",
        None,
        "27-41779271-1",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "green_sofia",
        "GREEN SOFIA",
        None,
        "23-43628641-4",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "grupo_avinea",
        "GRUPO AVINEA S.A.",
        None,
        "30-70998551-1",
        ("1 - Factura A",),
        (21.0,),
        True,
        ("ARS",),
        2,
    ),
    (
        "horeca",
        "HORECA SRL.",
        None,
        "30-71209619-1",
        ("1 - Factura A",),
        (
            10.5,
            21.0,
        ),
        True,
        ("ARS",),
        8,
    ),
    (
        "jo_trans",
        "JO-TRANS S.R.L.",
        None,
        "30-71327490-5",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        4,
    ),
    (
        "jordan_facundo_martin",
        "JORDAN FACUNDO MARTIN",
        None,
        "20-36413307-4",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "la_agricola",
        "LA AGRICOLA S A",
        None,
        "30-50123510-1",
        ("1 - Factura A",),
        (21.0,),
        True,
        ("ARS",),
        2,
    ),
    (
        "langeneker_carlos_marcelo",
        "LANGENEKER CARLOS MARCELO",
        None,
        "20-17611222-1",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        2,
    ),
    (
        "lavadero_industrial_norte",
        "LAVADERO INDUSTRIAL NORTE S.A.",
        None,
        "30-71099288-3",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        2,
    ),
    (
        "maccan_urbano",
        "MACCAN URBANO",
        None,
        "20-36205573-4",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "machado_barrios_juan_martin",
        "MACHADO BARRIOS JUAN MARTIN",
        None,
        "20-36123843-6",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "madero_este_parking",
        "MADERO ESTE PARKING S.A.",
        None,
        "30-70835507-7",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "melba_srl",
        "MELBA SRL",
        None,
        "30-71461086-0",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        6,
    ),
    (
        "mercadolibre",
        "MERCADOLIBRE S.R.L.",
        None,
        "30-70308853-4",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "monasa",
        "MONASA S.A",
        None,
        "30-71524041-2",
        (
            "1 - Factura A",
            "3 - Nota de Crédito A",
        ),
        (21.0,),
        False,
        ("ARS",),
        6,
    ),
    (
        "nestle_argentina",
        "NESTLE ARGENTINA S A",
        None,
        "30-50014731-4",
        ("1 - Factura A",),
        (21.0,),
        True,
        ("ARS",),
        2,
    ),
    (
        "novoa_nunez_evangelina_geraldine",
        "NOVOA NUÑEZ EVANGELINA GERALDINE",
        None,
        "27-39436258-7",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "nss_sa",
        "NSS SA",
        None,
        "30-70823326-5",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "ofimarket",
        "OFIMARKET SRL",
        None,
        "30-70873382-9",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "paniagua_carlos_alberto",
        "PANIAGUA CARLOS ALBERTO",
        None,
        "20-26522885-3",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        4,
    ),
    (
        "payway",
        "PAYWAY SAU",
        None,
        "30-70921777-8",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "pecchenino_carla_daniela",
        "PECCHENINO CARLA DANIELA",
        None,
        "27-33509165-1",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "pinero_jorge_oscar",
        "PIÑERO JORGE OSCAR",
        None,
        "20-13258976-4",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "prestifilippo_ezequiel_alejandro",
        "PRESTIFILIPPO EZEQUIEL ALEJANDRO",
        None,
        "20-30905213-8",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "qbo",
        "QBO S. R. L.",
        None,
        "30-71750897-8",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "rafael_cioffi_e_hijos",
        "RAFAEL CIOFFI E HIJOS SA",
        None,
        "30-68204143-5",
        ("1 - Factura A",),
        (21.0,),
        True,
        ("ARS",),
        8,
    ),
    (
        "ruffino_jorge_sebastian",
        "RUFFINO JORGE SEBASTIAN",
        None,
        "23-24957038-9",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "salto_jose_fernando_ezequiel",
        "SALTO JOSE FERNANDO EZEQUIEL",
        None,
        "20-35995551-1",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "sam_canillas",
        (
            "SAM CANILLAS DE MIGUEL ANGEL TALAVERA CONTRERAS "
            "Y ANDRES ARTURO ROMERO GONZALEZ SOCIEDAD LEY "
            "19550 C"
        ),
        None,
        "30-71764501-0",
        ("1 - Factura A",),
        (10.5,),
        False,
        ("ARS",),
        8,
    ),
    (
        "savio_pablo",
        "SAVIO PABLO",
        None,
        "20-20797693-5",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "schmid_erika_silvana",
        "SCHMID ERIKA SILVANA",
        None,
        "27-25219426-3",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "somaschini_maria_carmen",
        "SOMASCHINI MARIA CARMEN",
        None,
        "27-13655413-7",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "storni_maria",
        "STORNI MARIA",
        None,
        "27-30595013-6",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        4,
    ),
    (
        "suarez_quiroga_jorge_marcelo_mariano",
        "SUAREZ QUIROGA JORGE MARCELO MARIANO",
        None,
        "20-25466091-1",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        1,
    ),
    (
        "telecom_argentina",
        "TELECOM ARGENTINA SOCIEDAD ANONIMA",
        None,
        "30-63945373-8",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "top_3",
        "TOP 3 S. R. L.",
        None,
        "30-71608250-0",
        ("1 - Factura A",),
        (21.0,),
        False,
        ("ARS",),
        1,
    ),
    (
        "tossounian_ana_veronica",
        "TOSSOUNIAN ANA VERONICA",
        None,
        "23-23618616-4",
        ("11 - Factura C",),
        (),
        False,
        ("ARS",),
        4,
    ),
    (
        "volf",
        "VOLF S.A.",
        None,
        "30-71613731-3",
        ("1 - Factura A",),
        (21.0,),
        True,
        ("ARS",),
        1,
    ),
)


# ==========================================================
# FIN DEL BLOQUE DE DATOS EXTRAÍDOS DEL EXCEL
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE CONSTRUCCIÓN DEL CATÁLOGO
# ==========================================================


# ----------------------------------------------------------
# Construimos el diccionario PROVEEDORES.
#
# Cada tupla de _DATOS_PROVEEDORES se convierte en un objeto
# Proveedor.
#
# La clave del diccionario será el identificador interno.
#
# Ejemplo:
#
#     PROVEEDORES["arta_verduleros"]
#
# devolverá un objeto Proveedor con los datos oficiales de
# Arta.
#
# En esta primera construcción todavía no se agregan los
# alias de búsqueda. Se incorporarán en el siguiente bloque.
# ----------------------------------------------------------

PROVEEDORES: dict[str, Proveedor] = {
    identificador: Proveedor(
        identificador=identificador,
        razon_social=razon_social,
        nombre_fantasia=nombre_fantasia,
        cuit=cuit,
        tipos_comprobante_observados=tipos,
        alicuotas_iva_observadas=alicuotas,
        otros_tributos_observados=otros_tributos,
        monedas_observadas=monedas,
        cantidad_comprobantes_observados=cantidad,
    )
    for (
        identificador,
        razon_social,
        nombre_fantasia,
        cuit,
        tipos,
        alicuotas,
        otros_tributos,
        monedas,
        cantidad,
    ) in _DATOS_PROVEEDORES
}


# ==========================================================
# FIN DEL BLOQUE DE CONSTRUCCIÓN DEL CATÁLOGO
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE ALIAS ESPECIALES
# ==========================================================


# ----------------------------------------------------------
# Algunos proveedores necesitan alias adicionales que no
# pueden generarse automáticamente.
#
# Estos alias pueden representar:
#
# - Errores frecuentes de tipeo.
# - Errores producidos por la extracción del PDF.
# - Formas alternativas de la razón social.
# - Nombres comerciales.
#
# IMPORTANTE:
#
# Estos valores se utilizan solamente para reconocer al
# proveedor.
#
# Nunca se devuelven como razón social oficial.
# ----------------------------------------------------------

_ALIAS_ESPECIALES: dict[str, tuple[str, ...]] = {

    # El encabezado de algunos PDF de Frigorífico Los Prados no se puede
    # extraer como texto. Sin embargo, el nombre del adjunto suele contener
    # claramente el nombre comercial. Este alias permite reconocerlo sin
    # reemplazar la razón social canónica guardada en el catálogo.
    "frigorifico_los_prados": (
        "FRIGORIFICO LOS PRADOS",
        "LOS PRADOS",
    ),

    # ------------------------------------------------------
    # Arta puede aparecer en el texto extraído como AARTA.
    #
    # AARTA es solamente un alias defectuoso.
    #
    # Los valores finales siempre deben ser:
    #
    #     Razón social:
    #         ARTA DE GONZALEZ S.R.L.
    #
    #     Nombre de fantasía:
    #         Arta Verduleros
    # ------------------------------------------------------

    "arta_verduleros": (
        "ARTA DE GONZALEZ S.R.L.",
        "ARTA DE GONZALEZ SRL",
        "AARTA DE GONZALEZ S.R.L.",
        "AARTA DE GONZALEZ SRL",
        "ARTA VERDULEROS",
    ),

    # ------------------------------------------------------
    # All Online Solutions utiliza comercialmente Colppy.
    # ------------------------------------------------------

    "all_online_solutions": (
        "ALL ONLINE SOLUTIONS SAU",
        "ALL ONLINE SOLUTIONS S. A. U.",
        "COLPPY",
        "COLPPY ALL ONLINE SOLUTIONS",
    ),

    # ------------------------------------------------------
    # El Criollo puede aparecer con o sin puntos y también
    # con el error DISTRUBUIDORA.
    # ------------------------------------------------------

    "el_criollo": (
        "DISTRIBUIDORA EL CRIOLLO SRL",
        "DISTRIBUIDORA EL CRIOLLO S.R.L.",
        "DISTRUBUIDORA EL CRIOLLO SRL",
        "EL CRIOLLO",
    ),

    # ------------------------------------------------------
    # DBA puede aparecer mediante su razón social o mediante
    # su nombre comercial.
    # ------------------------------------------------------

    "dba": (
        "DISTRIBUIDORA DE BEBIDAS SRL",
        "DISTRIBUIDORA DE BEBIDAS S.R.L.",
        "DISTRUIBUIDORA DE BEBIDAS SRL",
        "DBA",
    ),
}


# ----------------------------------------------------------
# Recorremos todos los proveedores para construir sus alias.
#
# Primero generamos alias automáticos a partir de:
#
# - Razón social.
# - Razón social sin puntos.
# - Nombre de fantasía.
#
# Después agregamos los alias especiales definidos arriba.
#
# Como Proveedor utiliza frozen=True, no podemos modificar el
# objeto directamente.
#
# Por eso utilizamos replace(), que crea una copia nueva del
# proveedor reemplazando únicamente alias_busqueda.
# ----------------------------------------------------------

for _identificador, _proveedor in tuple(
    PROVEEDORES.items()
):

    _alias = set(
        generar_alias_automaticos(
            _proveedor.razon_social,
            _proveedor.nombre_fantasia,
        )
    )

    for _alias_especial in _ALIAS_ESPECIALES.get(
        _identificador,
        ()
    ):

        _alias.add(
            normalizar_texto_busqueda(
                _alias_especial
            )
        )

    PROVEEDORES[_identificador] = replace(
        _proveedor,
        alias_busqueda=tuple(
            sorted(
                alias_texto
                for alias_texto in _alias
                if alias_texto
            )
        ),
    )


# ==========================================================
# FIN DEL BLOQUE DE ALIAS ESPECIALES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE ÍNDICES DE CONSULTA
# ==========================================================


# ----------------------------------------------------------
# Creamos un índice interno por CUIT.
#
# Sin este índice, para buscar un CUIT tendríamos que recorrer
# todos los proveedores en cada consulta.
#
# Con el índice podemos acceder directamente:
#
#     CUIT sin guiones → objeto Proveedor
#
# Ejemplo conceptual:
#
#     "30718674928" → proveedor Arta
#
# El guion bajo inicial indica que esta variable es interna
# al módulo y no forma parte de su interfaz pública principal.
# ----------------------------------------------------------

_PROVEEDORES_POR_CUIT: dict[str, Proveedor] = {
    proveedor.cuit_sin_guiones(): proveedor
    for proveedor in PROVEEDORES.values()
}


# ==========================================================
# FIN DEL BLOQUE DE ÍNDICES DE CONSULTA
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE FUNCIONES PÚBLICAS
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN obtener_proveedor()
# ----------------------------------------------------------

def obtener_proveedor(
    identificador: str
) -> Optional[Proveedor]:
    """
    Obtener un proveedor mediante su identificador interno.

    Ejemplo
    -------
    obtener_proveedor("arta_verduleros")

    puede devolver el objeto Proveedor correspondiente a
    Arta.

    Esta función es tolerante.

    Si el identificador no existe o no es texto, devuelve
    None.

    Debe utilizarse cuando la ausencia del proveedor es una
    posibilidad válida y puede manejarse normalmente.

    Parámetros
    ----------
    identificador:

        Identificador interno del proveedor.

    Retorna
    -------
    Proveedor | None

        Proveedor encontrado o None.
    """

    if not isinstance(identificador, str):
        return None

    return PROVEEDORES.get(
        identificador.strip()
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN obtener_proveedor()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN obtener_proveedor_obligatorio()
# ----------------------------------------------------------

def obtener_proveedor_obligatorio(
    identificador: str
) -> Proveedor:
    """
    Obtener un proveedor y exigir que exista.

    A diferencia de obtener_proveedor(), esta función no
    devuelve None.

    Si el identificador no existe, genera un KeyError.

    Debe utilizarse cuando la ausencia del proveedor
    representa:

    - Un error de programación.
    - Una configuración incorrecta.
    - Una inconsistencia que no debería permitirse.

    Ejemplo
    -------
    Las validaciones internas exigen que exista:

        arta_verduleros

    Si alguien elimina accidentalmente ese proveedor del
    catálogo, la importación debe fallar de forma clara.

    Parámetros
    ----------
    identificador:

        Identificador interno obligatorio.

    Retorna
    -------
    Proveedor

        Proveedor encontrado.

    Excepciones
    -----------
    KeyError

        Si el proveedor no existe.
    """

    proveedor = obtener_proveedor(
        identificador
    )

    if proveedor is None:

        raise KeyError(
            "No existe un proveedor con el identificador: "
            f"{identificador!r}"
        )

    return proveedor

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN obtener_proveedor_obligatorio()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN buscar_proveedor_por_cuit()
# ----------------------------------------------------------

def buscar_proveedor_por_cuit(
    cuit: object
) -> Optional[Proveedor]:
    """
    Buscar un proveedor mediante su CUIT.

    La función acepta el CUIT:

    - Con guiones.
    - Sin guiones.
    - Con espacios.
    - Con otros separadores.

    Ejemplos equivalentes:

        30-71867492-8
        30718674928
        30 71867492 8

    Flujo
    -----
    1. Normaliza el CUIT.
    2. Comprueba que tenga once dígitos.
    3. Elimina los guiones.
    4. Consulta el índice por CUIT.

    Parámetros
    ----------
    cuit:

        CUIT que deseamos buscar.

    Retorna
    -------
    Proveedor | None

        Proveedor encontrado o None.
    """

    cuit_normalizado = normalizar_cuit(
        cuit
    )

    if cuit_normalizado is None:
        return None

    digitos = "".join(
        caracter
        for caracter in cuit_normalizado
        if caracter.isdigit()
    )

    return _PROVEEDORES_POR_CUIT.get(
        digitos
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN buscar_proveedor_por_cuit()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN buscar_proveedores_en_texto()
# ----------------------------------------------------------

def buscar_proveedores_en_texto(
    texto: object
) -> list[Proveedor]:
    """
    Buscar candidatos a proveedor dentro de un texto.

    La función analiza dos clases de coincidencias:

    1. CUIT

       Busca el CUIT del proveedor dentro de todos los
       dígitos del texto.

    2. Alias

       Busca razones sociales, nombres comerciales y
       variantes normalizadas.

    Importante
    ----------
    Esta función devuelve candidatos.

    No decide por sí sola cuál es el proveedor definitivo si
    aparecen varias coincidencias.

    supplier_detector.py será responsable de:

    - Asignar puntajes.
    - Comparar candidatos.
    - Determinar confianza.
    - Evitar confundir receptor y emisor.
    - Elegir el proveedor definitivo.

    Parámetros
    ----------
    texto:

        Texto extraído desde una factura.

    Retorna
    -------
    list

        Lista de objetos Proveedor encontrados.
    """

    texto_original = (
        ""
        if texto is None
        else str(texto)
    )

    texto_normalizado = normalizar_texto_busqueda(
        texto_original
    )

    # ------------------------------------------------------
    # Creamos también una versión que contiene solamente los
    # dígitos del texto.
    #
    # Así un CUIT puede detectarse aunque aparezca con
    # separadores diferentes.
    # ------------------------------------------------------

    digitos_texto = re.sub(
        r"\D",
        "",
        texto_original
    )

    encontrados: list[Proveedor] = []

    for proveedor in PROVEEDORES.values():

        coincide_cuit = (
            proveedor.cuit_sin_guiones()
            in digitos_texto
        )

        coincide_alias = any(
            alias
            and alias in texto_normalizado
            for alias in proveedor.alias_busqueda
        )

        if coincide_cuit or coincide_alias:

            encontrados.append(
                proveedor
            )

    return encontrados

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN buscar_proveedores_en_texto()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN listar_proveedores()
# ----------------------------------------------------------

def listar_proveedores() -> tuple[Proveedor, ...]:
    """
    Devolver todos los proveedores ordenados alfabéticamente.

    La ordenación se realiza utilizando una versión
    normalizada de la razón social.

    Retorna
    -------
    tuple

        Tupla inmutable de proveedores.
    """

    return tuple(
        sorted(
            PROVEEDORES.values(),
            key=lambda proveedor: (
                normalizar_texto_busqueda(
                    proveedor.razon_social
                )
            ),
        )
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN listar_proveedores()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN cantidad_proveedores()
# ----------------------------------------------------------

def cantidad_proveedores() -> int:
    """
    Devolver la cantidad total de proveedores registrados.

    Retorna
    -------
    int

        Número de proveedores del catálogo.
    """

    return len(
        PROVEEDORES
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN cantidad_proveedores()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE FUNCIONES PÚBLICAS
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE VALIDACIÓN DEFENSIVA
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN validar_catalogo()
# ----------------------------------------------------------

def validar_catalogo(
    proveedores: Iterable[Proveedor]
) -> None:
    """
    Validar la integridad completa del catálogo.

    Esta función recorre todos los proveedores y comprueba
    que los datos sean coherentes.

    Si encuentra un problema, genera ValueError y detiene la
    importación del módulo.

    Esto es preferible a permitir que el programa siga
    funcionando con información fiscal contradictoria.

    Validaciones generales
    ----------------------
    - Identificador no vacío.
    - Identificador no repetido.
    - Razón social no vacía.
    - CUIT con once dígitos.
    - CUIT no repetido.
    - El receptor no puede ser proveedor.
    - Cantidad observada no negativa.
    - Alícuotas contempladas.
    - Monedas contempladas.

    Validaciones especiales
    ------------------------
    También protege expresamente los datos de Arta.

    Parámetros
    ----------
    proveedores:

        Colección de objetos Proveedor.

    Retorna
    -------
    None

        No devuelve un valor.

        Si todo es correcto, finaliza silenciosamente.

    Excepciones
    -----------
    ValueError

        Si encuentra una inconsistencia.
    """

    identificadores: set[str] = set()
    cuits: set[str] = set()

    for proveedor in proveedores:

        # --------------------------------------------------
        # El identificador interno es obligatorio.
        # --------------------------------------------------

        if not proveedor.identificador.strip():

            raise ValueError(
                "Existe un proveedor sin identificador."
            )

        # --------------------------------------------------
        # Dos proveedores no pueden compartir identificador.
        # --------------------------------------------------

        if proveedor.identificador in identificadores:

            raise ValueError(
                "Identificador duplicado: "
                f"{proveedor.identificador}"
            )

        identificadores.add(
            proveedor.identificador
        )

        # --------------------------------------------------
        # La razón social canónica es obligatoria.
        # --------------------------------------------------

        if not proveedor.razon_social.strip():

            raise ValueError(
                "Existe un proveedor sin razón social: "
                f"{proveedor.identificador}"
            )

        # --------------------------------------------------
        # El CUIT debe contener exactamente once dígitos.
        # --------------------------------------------------

        if normalizar_cuit(
            proveedor.cuit
        ) is None:

            raise ValueError(
                "CUIT inválido para "
                f"{proveedor.identificador}: "
                f"{proveedor.cuit}"
            )

        cuit_digitos = proveedor.cuit_sin_guiones()

        # --------------------------------------------------
        # Dos proveedores diferentes no pueden compartir
        # CUIT.
        # --------------------------------------------------

        if cuit_digitos in cuits:

            raise ValueError(
                "CUIT duplicado: "
                f"{proveedor.cuit}"
            )

        cuits.add(
            cuit_digitos
        )

        # --------------------------------------------------
        # La empresa receptora no debe figurar como proveedor.
        #
        # business_config.es_cuit_receptor() acepta el CUIT
        # con o sin guiones.
        # --------------------------------------------------

        if business_config.es_cuit_receptor(
            proveedor.cuit
        ):

            raise ValueError(
                "El receptor no puede registrarse como "
                "proveedor: "
                f"{proveedor.razon_social}"
            )

        # --------------------------------------------------
        # La cantidad observada no puede ser negativa.
        # --------------------------------------------------

        if (
            proveedor.cantidad_comprobantes_observados
            < 0
        ):

            raise ValueError(
                "Cantidad de comprobantes negativa para "
                f"{proveedor.identificador}"
            )

        # --------------------------------------------------
        # Validamos las alícuotas de IVA.
        #
        # El conjunto contiene las alícuotas actualmente
        # contempladas por el proyecto.
        #
        # Si aparece una alícuota nueva en el futuro, deberá
        # revisarse antes de agregarla.
        # --------------------------------------------------

        for alicuota in (
            proveedor.alicuotas_iva_observadas
        ):

            if alicuota not in {
                0.0,
                2.5,
                5.0,
                10.5,
                21.0,
                27.0,
            }:

                raise ValueError(
                    "Alícuota no contemplada para "
                    f"{proveedor.identificador}: "
                    f"{alicuota}"
                )

        # --------------------------------------------------
        # Validamos las monedas contempladas.
        # --------------------------------------------------

        for moneda in proveedor.monedas_observadas:

            if moneda not in {
                "ARS",
                "USD",
            }:

                raise ValueError(
                    "Moneda no contemplada para "
                    f"{proveedor.identificador}: "
                    f"{moneda}"
                )

    # ------------------------------------------------------
    # INICIO DE LAS VALIDACIONES ESPECIALES DE ARTA
    # ------------------------------------------------------

    # ------------------------------------------------------
    # Arta debe existir obligatoriamente en el catálogo.
    # ------------------------------------------------------

    arta = obtener_proveedor_obligatorio(
        "arta_verduleros"
    )

    # ------------------------------------------------------
    # Protegemos la razón social canónica.
    # ------------------------------------------------------

    if (
        arta.razon_social
        != "ARTA DE GONZALEZ S.R.L."
    ):

        raise ValueError(
            "La razón social canónica de Arta debe ser "
            "'ARTA DE GONZALEZ S.R.L.'."
        )

    # ------------------------------------------------------
    # Protegemos el nombre de fantasía canónico.
    # ------------------------------------------------------

    if (
        arta.nombre_fantasia
        != "Arta Verduleros"
    ):

        raise ValueError(
            "El nombre de fantasía canónico de Arta debe "
            "ser 'Arta Verduleros'."
        )

    # ------------------------------------------------------
    # La palabra AARTA puede existir en alias de búsqueda,
    # pero nunca en la razón social oficial.
    # ------------------------------------------------------

    if "AARTA" in arta.razon_social.upper():

        raise ValueError(
            "AARTA solo puede existir como alias de "
            "reconocimiento."
        )

    # ------------------------------------------------------
    # FIN DE LAS VALIDACIONES ESPECIALES DE ARTA
    # ------------------------------------------------------

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN validar_catalogo()
# ----------------------------------------------------------


# ----------------------------------------------------------
# Ejecutamos la validación automáticamente cuando Python
# importa supplier_catalog.py.
#
# Si todo el catálogo es correcto, no se muestra nada.
#
# Si existe una inconsistencia, la importación se detiene con
# una excepción clara.
#
# Esto evita que supplier_detector.py o invoice_parser.py
# trabajen con datos corruptos.
# ----------------------------------------------------------

validar_catalogo(
    PROVEEDORES.values()
)


# ==========================================================
# FIN DEL BLOQUE DE VALIDACIÓN DEFENSIVA
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================