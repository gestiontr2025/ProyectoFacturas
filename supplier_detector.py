"""
==========================================================
PROYECTO
==========================================================

Proyecto Facturas

Archivo
-------
supplier_detector.py

Descripción
-----------
Este módulo se encarga de identificar qué proveedor emitió
una factura a partir del texto extraído desde su archivo PDF.

El módulo no mantiene su propia lista de proveedores.

Todos los datos oficiales se obtienen desde:

    supplier_catalog.py

Esto convierte a supplier_catalog.py en la única fuente de
verdad para:

- Identificadores internos.
- Razones sociales oficiales.
- Nombres de fantasía.
- CUIT.
- Alias de reconocimiento.
- Información fiscal observada.

Responsabilidades
-----------------
Este módulo puede:

- Recibir texto extraído desde un PDF.
- Normalizar el texto para realizar comparaciones.
- Buscar CUIT de proveedores conocidos.
- Buscar razones sociales y alias conocidos.
- Excluir los datos de la empresa receptora.
- Asignar puntajes según la evidencia encontrada.
- Comparar varios candidatos.
- Detectar ambigüedades.
- Seleccionar un proveedor únicamente cuando la evidencia
  sea suficiente.
- Devolver siempre datos canónicos del catálogo.
- Generar advertencias cuando existan contradicciones.

No debe
-------
Este módulo no debe:

- Conectarse con Gmail.
- Descargar archivos.
- Leer directamente archivos PDF.
- Crear carpetas.
- Guardar archivos.
- Renombrar facturas.
- Extraer importes, fechas o números de comprobante.
- Mantener datos duplicados de proveedores.
- Inventar un proveedor cuando la evidencia sea insuficiente.

Flujo general
-------------
El flujo esperado es:

    PDF
      ↓
    pdf_reader.py extrae el texto
      ↓
    supplier_detector.py analiza el texto
      ↓
    supplier_catalog.py aporta los datos oficiales
      ↓
    se devuelve un proveedor canónico o un resultado
    defensivo de proveedor no reconocido

Programación defensiva
----------------------
Los archivos PDF pueden presentar:

- Texto desordenado.
- CUIT sin guiones.
- Razones sociales separadas en varias líneas.
- Errores tipográficos.
- Caracteres duplicados.
- Texto repetido por original, duplicado y triplicado.
- Información del receptor antes que la del emisor.
- Varios proveedores mencionados dentro del mismo texto.
- Alias demasiado cortos o ambiguos.

Por ese motivo:

1. El CUIT tiene mayor valor que una coincidencia textual.

2. La empresa receptora nunca puede ser seleccionada como
   proveedor.

3. Una coincidencia textual aislada no siempre es
   suficiente.

4. Si dos candidatos tienen el mismo puntaje principal, no
   se elige arbitrariamente uno.

5. Si el CUIT señala un proveedor y la razón social señala
   otro, el resultado se marca como contradictorio.

6. Es preferible devolver proveedor no reconocido antes que
   registrar una identidad incorrecta.

Regla especial de Arta
----------------------
El catálogo define:

    Identificador:
        arta_verduleros

    Razón social canónica:
        ARTA DE GONZALEZ S.R.L.

    Nombre de fantasía:
        Arta Verduleros

El texto defectuoso:

    AARTA DE GONZALEZ S.R.L.

puede utilizarse únicamente como alias de reconocimiento.

El resultado final nunca debe contener:

    AARTA VERDULEROS
    Aarta Verduleros

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
# Esta importación permite utilizar anotaciones modernas de
# tipos sin que Python deba resolver inmediatamente todas
# las clases mencionadas.
#
# Por ejemplo:
#
#     list[CandidatoProveedor]
#     str | None
#
# También mejora la compatibilidad de las anotaciones cuando
# una clase todavía se encuentra en proceso de definición.
# ----------------------------------------------------------

from __future__ import annotations


# ----------------------------------------------------------
# Importamos re.
#
# re pertenece a la biblioteca estándar de Python y permite
# trabajar con expresiones regulares.
#
# En este módulo se utiliza para:
#
# - Extraer números de CUIT.
# - Comparar CUIT con y sin guiones.
# - Normalizar grupos de espacios.
# - Buscar alias respetando límites de palabras.
# - Evitar coincidencias parciales peligrosas.
# ----------------------------------------------------------

import re


# ----------------------------------------------------------
# Importamos dataclass y field.
#
# dataclass permite crear estructuras especializadas para
# almacenar resultados intermedios.
#
# En este módulo se utiliza para representar a cada
# candidato encontrado durante la detección.
#
# field permite crear listas independientes para cada
# candidato.
#
# Sin field(default_factory=list), varias instancias podrían
# compartir accidentalmente una misma lista.
# ----------------------------------------------------------

from dataclasses import dataclass, field


# ----------------------------------------------------------
# Importamos Optional.
#
# Optional[str] significa que un valor puede contener:
#
# - Un texto.
# - None.
#
# None representa que el dato no se encontró o no pudo
# determinarse de manera segura.
# ----------------------------------------------------------

from typing import Optional


# ----------------------------------------------------------
# Importamos business_config.
#
# Este módulo contiene los datos oficiales de la empresa
# receptora:
#
#     MADERO ROOF TOP S.A.
#     CUIT 30-71834746-3
#
# supplier_detector.py utiliza esos datos para impedir que el
# receptor sea confundido con un proveedor.
# ----------------------------------------------------------

import business_config


# ----------------------------------------------------------
# Importamos supplier_catalog.
#
# supplier_catalog.py contiene:
#
# - Todos los proveedores conocidos.
# - Sus razones sociales oficiales.
# - Sus CUIT.
# - Sus nombres de fantasía.
# - Sus alias de búsqueda.
#
# Este detector nunca debe volver a escribir manualmente esos
# valores.
#
# Así evitamos inconsistencias como que un archivo diga:
#
#     ARTA DE GONZALEZ S.R.L.
#
# y otro diga:
#
#     AARTA DE GONZALEZ S.R.L.
# ----------------------------------------------------------

import supplier_catalog


# ==========================================================
# FIN DEL BLOQUE DE IMPORTACIONES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE CONSTANTES
# ==========================================================


# ----------------------------------------------------------
# Puntaje asignado cuando aparece el CUIT exacto de un
# proveedor.
#
# El CUIT es la evidencia de mayor peso porque identifica
# fiscalmente al emisor.
# ----------------------------------------------------------

PUNTAJE_CUIT = 6


# ----------------------------------------------------------
# Puntaje asignado cuando aparece la razón social canónica o
# un alias de razón social suficientemente específico.
# ----------------------------------------------------------

PUNTAJE_RAZON_SOCIAL = 3


# ----------------------------------------------------------
# Puntaje asignado cuando aparece únicamente el nombre de
# fantasía.
#
# Tiene menos peso que la razón social porque algunos nombres
# comerciales pueden ser cortos o aparecer en otros
# contextos.
# ----------------------------------------------------------

PUNTAJE_NOMBRE_FANTASIA = 2


# ----------------------------------------------------------
# Puntaje adicional cuando CUIT y razón social apuntan al
# mismo proveedor.
#
# Esta combinación representa la evidencia más confiable.
# ----------------------------------------------------------

BONIFICACION_CUIT_Y_NOMBRE = 2


# ----------------------------------------------------------
# Longitud mínima recomendada para utilizar un alias textual.
#
# Los alias demasiado cortos, como:
#
#     DBA
#
# pueden aparecer accidentalmente dentro de otro texto.
#
# Los alias cortos no se descartan por completo, pero se
# buscan mediante reglas más estrictas.
# ----------------------------------------------------------

LONGITUD_ALIAS_CORTO = 4


# ==========================================================
# FIN DEL BLOQUE DE CONSTANTES
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE ESTRUCTURAS INTERNAS
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA CLASE CandidatoProveedor
# ----------------------------------------------------------

@dataclass
class CandidatoProveedor:
    """
    Representar un proveedor candidato durante el análisis.

    Esta estructura es interna.

    No es el resultado final que recibe main.py.

    Atributos
    ---------
    proveedor:

        Objeto canónico obtenido desde supplier_catalog.py.

    coincide_cuit:

        True si el CUIT oficial del proveedor aparece en el
        texto.

    alias_encontrados:

        Alias del proveedor encontrados en el texto.

    coincide_razon_social:

        True si alguna coincidencia corresponde a la razón
        social o a una variante suficientemente descriptiva.

    coincide_nombre_fantasia:

        True si se encontró el nombre comercial.

    puntaje:

        Valor calculado según la fuerza de las evidencias.

    evidencias:

        Lista descriptiva de las coincidencias encontradas.

    advertencias:

        Problemas o situaciones especiales detectadas para
        este candidato.
    """

    proveedor: supplier_catalog.Proveedor

    coincide_cuit: bool = False
    alias_encontrados: list[str] = field(
        default_factory=list
    )

    coincide_razon_social: bool = False
    coincide_nombre_fantasia: bool = False

    puntaje: int = 0

    evidencias: list[str] = field(
        default_factory=list
    )

    advertencias: list[str] = field(
        default_factory=list
    )


    # ------------------------------------------------------
    # INICIO DE LA FUNCIÓN calcular_puntaje()
    # ------------------------------------------------------

    def calcular_puntaje(self) -> int:
        """
        Calcular el puntaje total del candidato.

        Reglas
        ------
        - CUIT exacto:
              PUNTAJE_CUIT

        - Razón social o alias descriptivo:
              PUNTAJE_RAZON_SOCIAL

        - Nombre de fantasía:
              PUNTAJE_NOMBRE_FANTASIA

        - CUIT y nombre coincidentes:
              BONIFICACION_CUIT_Y_NOMBRE

        Retorna
        -------
        int

            Puntaje total actualizado.
        """

        puntaje = 0

        if self.coincide_cuit:

            puntaje += PUNTAJE_CUIT

        if self.coincide_razon_social:

            puntaje += PUNTAJE_RAZON_SOCIAL

        elif self.coincide_nombre_fantasia:

            puntaje += PUNTAJE_NOMBRE_FANTASIA

        if (
            self.coincide_cuit
            and
            (
                self.coincide_razon_social
                or
                self.coincide_nombre_fantasia
            )
        ):

            puntaje += BONIFICACION_CUIT_Y_NOMBRE

        self.puntaje = puntaje

        return puntaje

    # ------------------------------------------------------
    # FIN DE LA FUNCIÓN calcular_puntaje()
    # ------------------------------------------------------


# ----------------------------------------------------------
# FIN DE LA CLASE CandidatoProveedor
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE ESTRUCTURAS INTERNAS
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE FUNCIONES DE NORMALIZACIÓN
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN normalizar_texto()
# ----------------------------------------------------------

def normalizar_texto(texto: object) -> str:
    """
    Normalizar un texto para realizar búsquedas.

    Esta función utiliza la misma normalización definida por:

        supplier_catalog.normalizar_texto_busqueda()

    De esta forma, el catálogo y el detector comparan los
    textos bajo las mismas reglas.

    Parámetros
    ----------
    texto:

        Texto que deseamos analizar.

    Retorna
    -------
    str

        Texto normalizado para búsquedas.
    """

    return supplier_catalog.normalizar_texto_busqueda(
        texto
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN normalizar_texto()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN obtener_digitos_texto()
# ----------------------------------------------------------

def obtener_digitos_texto(texto: object) -> str:
    """
    Obtener todos los dígitos contenidos en un texto.

    Ejemplo
    -------
    Si recibe:

        CUIT: 30-71867492-8

    devuelve:

        30718674928

    Esta forma permite reconocer un CUIT aunque aparezca:

    - Con guiones.
    - Sin guiones.
    - Con espacios.
    - Separado por saltos de línea.

    Parámetros
    ----------
    texto:

        Texto original.

    Retorna
    -------
    str

        Cadena formada únicamente por dígitos.
    """

    if texto is None:
        return ""

    return re.sub(
        r"\D",
        "",
        str(texto)
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN obtener_digitos_texto()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE FUNCIONES DE NORMALIZACIÓN
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE FUNCIONES DE BÚSQUEDA
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN alias_aparece_en_texto()
# ----------------------------------------------------------

def alias_aparece_en_texto(
    alias: str,
    texto_normalizado: str
) -> bool:
    """
    Comprobar si un alias aparece dentro del texto.

    La búsqueda cambia según la longitud del alias.

    Alias largos
    ------------
    Se buscan como una secuencia normal dentro del texto.

    Alias cortos
    ------------
    Se exigen límites de palabra para reducir falsos
    positivos.

    Ejemplo
    -------
    El alias:

        DBA

    no debería coincidir accidentalmente dentro de una
    palabra más extensa.

    Parámetros
    ----------
    alias:

        Alias ya normalizado.

    texto_normalizado:

        Texto completo ya normalizado.

    Retorna
    -------
    bool

        True si el alias aparece de manera aceptable.
    """

    if not alias:
        return False

    if not texto_normalizado:
        return False

    alias = alias.strip()

    if not alias:
        return False

    if len(alias) <= LONGITUD_ALIAS_CORTO:

        patron = (
            r"(?<![A-Z0-9])"
            +
            re.escape(alias)
            +
            r"(?![A-Z0-9])"
        )

        return re.search(
            patron,
            texto_normalizado
        ) is not None

    return alias in texto_normalizado

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN alias_aparece_en_texto()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN es_alias_razon_social()
# ----------------------------------------------------------

def es_alias_razon_social(
    proveedor: supplier_catalog.Proveedor,
    alias: str
) -> bool:
    """
    Determinar si un alias representa la razón social.

    La función compara el alias con variantes normalizadas de
    la razón social canónica.

    También considera algunos alias extensos que contienen
    palabras características de entidades jurídicas, como:

    - SRL
    - SA
    - SAS
    - SOCIEDAD
    - SOLUTIONS

    Parámetros
    ----------
    proveedor:

        Proveedor canónico.

    alias:

        Alias normalizado encontrado.

    Retorna
    -------
    bool

        True si se considera evidencia de razón social.
    """

    razon_normalizada = normalizar_texto(
        proveedor.razon_social
    )

    if alias == razon_normalizada:
        return True

    # ------------------------------------------------------
    # Comparamos versiones sin espacios.
    #
    # Esto ayuda cuando el PDF une o separa las siglas:
    #
    #     S.R.L.
    #     S R L
    #     SRL
    # ------------------------------------------------------

    alias_sin_espacios = alias.replace(
        " ",
        ""
    )

    razon_sin_espacios = razon_normalizada.replace(
        " ",
        ""
    )

    if alias_sin_espacios == razon_sin_espacios:
        return True

    palabras_juridicas = {
        "SRL",
        "SA",
        "SAU",
        "SAS",
        "SOCIEDAD",
        "SOLUTIONS",
    }

    palabras_alias = set(
        alias.split()
    )

    if (
        len(alias) >= 10
        and
        palabras_alias.intersection(
            palabras_juridicas
        )
    ):

        return True

    return False

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN es_alias_razon_social()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN es_alias_nombre_fantasia()
# ----------------------------------------------------------

def es_alias_nombre_fantasia(
    proveedor: supplier_catalog.Proveedor,
    alias: str
) -> bool:
    """
    Determinar si un alias representa el nombre de fantasía.

    Parámetros
    ----------
    proveedor:

        Proveedor canónico.

    alias:

        Alias encontrado.

    Retorna
    -------
    bool

        True si coincide con el nombre comercial.
    """

    if not proveedor.nombre_fantasia:
        return False

    nombre_normalizado = normalizar_texto(
        proveedor.nombre_fantasia
    )

    return alias == nombre_normalizado

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN es_alias_nombre_fantasia()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN analizar_candidato()
# ----------------------------------------------------------

def analizar_candidato(
    proveedor: supplier_catalog.Proveedor,
    texto_normalizado: str,
    digitos_texto: str
) -> CandidatoProveedor:
    """
    Analizar un proveedor individual contra el texto.

    La función comprueba:

    - Si aparece el CUIT.
    - Qué alias aparecen.
    - Si la coincidencia corresponde a la razón social.
    - Si la coincidencia corresponde al nombre de fantasía.
    - Qué evidencias se encontraron.
    - Cuál es el puntaje final.

    Parámetros
    ----------
    proveedor:

        Proveedor que deseamos analizar.

    texto_normalizado:

        Texto preparado para búsquedas.

    digitos_texto:

        Todos los dígitos del texto original.

    Retorna
    -------
    CandidatoProveedor

        Resultado interno del análisis.
    """

    candidato = CandidatoProveedor(
        proveedor=proveedor
    )

    # ------------------------------------------------------
    # Comprobamos el CUIT.
    #
    # El CUIT del proveedor se encuentra almacenado en forma
    # canónica, pero se compara sin guiones.
    # ------------------------------------------------------

    cuit_digitos = proveedor.cuit_sin_guiones()

    if (
        cuit_digitos
        and
        cuit_digitos in digitos_texto
    ):

        candidato.coincide_cuit = True

        candidato.evidencias.append(
            "CUIT del proveedor encontrado en el texto."
        )

    # ------------------------------------------------------
    # Recorremos todos los alias registrados.
    # ------------------------------------------------------

    for alias in proveedor.alias_busqueda:

        if not alias_aparece_en_texto(
            alias,
            texto_normalizado
        ):
            continue

        if alias not in candidato.alias_encontrados:

            candidato.alias_encontrados.append(
                alias
            )

        if es_alias_razon_social(
            proveedor,
            alias
        ):

            candidato.coincide_razon_social = True

        if es_alias_nombre_fantasia(
            proveedor,
            alias
        ):

            candidato.coincide_nombre_fantasia = True

    if candidato.coincide_razon_social:

        candidato.evidencias.append(
            "Razón social o alias jurídico encontrado."
        )

    if candidato.coincide_nombre_fantasia:

        candidato.evidencias.append(
            "Nombre de fantasía encontrado."
        )

    candidato.calcular_puntaje()

    return candidato

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN analizar_candidato()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN obtener_candidatos()
# ----------------------------------------------------------

def obtener_candidatos(
    texto: object
) -> list[CandidatoProveedor]:
    """
    Obtener todos los proveedores con evidencia positiva.

    Un proveedor se considera candidato cuando obtiene un
    puntaje mayor que cero.

    La empresa receptora se excluye defensivamente incluso si
    por error estuviera presente en el catálogo.

    Parámetros
    ----------
    texto:

        Texto extraído desde el PDF.

    Retorna
    -------
    list

        Lista de candidatos ordenada de mayor a menor
        puntaje.
    """

    texto_original = (
        ""
        if texto is None
        else str(texto)
    )

    texto_normalizado = normalizar_texto(
        texto_original
    )

    digitos_texto = obtener_digitos_texto(
        texto_original
    )

    candidatos: list[CandidatoProveedor] = []

    for proveedor in supplier_catalog.listar_proveedores():

        # --------------------------------------------------
        # Protección adicional:
        #
        # Aunque supplier_catalog.py ya impide registrar al
        # receptor como proveedor, volvemos a comprobarlo.
        #
        # Esta doble protección es intencional.
        # --------------------------------------------------

        if business_config.es_cuit_receptor(
            proveedor.cuit
        ):

            continue

        candidato = analizar_candidato(
            proveedor,
            texto_normalizado,
            digitos_texto
        )

        if candidato.puntaje > 0:

            candidatos.append(
                candidato
            )

    candidatos.sort(
        key=lambda candidato: (
            candidato.puntaje,
            candidato.coincide_cuit,
            candidato.coincide_razon_social,
            candidato.coincide_nombre_fantasia,
            candidato.proveedor.identificador,
        ),
        reverse=True
    )

    return candidatos

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN obtener_candidatos()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE FUNCIONES DE BÚSQUEDA
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE EVALUACIÓN DE RESULTADOS
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN determinar_metodo_deteccion()
# ----------------------------------------------------------

def determinar_metodo_deteccion(
    candidato: CandidatoProveedor
) -> str:
    """
    Determinar qué combinación de evidencias permitió la
    detección.

    Posibles resultados:

        razon_social_y_cuit
        nombre_fantasia_y_cuit
        cuit
        razon_social
        nombre_fantasia
        coincidencia_multiple

    Parámetros
    ----------
    candidato:

        Candidato seleccionado.

    Retorna
    -------
    str

        Nombre interno del método.
    """

    if (
        candidato.coincide_cuit
        and
        candidato.coincide_razon_social
    ):

        return "razon_social_y_cuit"

    if (
        candidato.coincide_cuit
        and
        candidato.coincide_nombre_fantasia
    ):

        return "nombre_fantasia_y_cuit"

    if candidato.coincide_cuit:

        return "cuit"

    if candidato.coincide_razon_social:

        return "razon_social"

    if candidato.coincide_nombre_fantasia:

        return "nombre_fantasia"

    return "coincidencia_multiple"

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN determinar_metodo_deteccion()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN determinar_nivel_confianza()
# ----------------------------------------------------------

def determinar_nivel_confianza(
    candidato: CandidatoProveedor
) -> str:
    """
    Asignar un nivel de confianza al candidato seleccionado.

    Reglas generales
    ----------------
    alta:

        CUIT y nombre coinciden, o el puntaje es muy alto.

    media:

        CUIT aislado o razón social suficientemente
        descriptiva.

    baja:

        Solamente existe una coincidencia textual débil.

    Parámetros
    ----------
    candidato:

        Candidato seleccionado.

    Retorna
    -------
    str

        alta, media o baja.
    """

    if (
        candidato.coincide_cuit
        and
        (
            candidato.coincide_razon_social
            or
            candidato.coincide_nombre_fantasia
        )
    ):

        return "alta"

    if candidato.puntaje >= 8:

        return "alta"

    if candidato.coincide_cuit:

        return "media"

    if candidato.coincide_razon_social:

        return "media"

    return "baja"

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN determinar_nivel_confianza()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN hay_contradiccion_cuit_nombre()
# ----------------------------------------------------------

def hay_contradiccion_cuit_nombre(
    candidatos: list[CandidatoProveedor]
) -> bool:
    """
    Detectar si el CUIT apunta a un proveedor y la razón
    social apunta claramente a otro.

    Ejemplo conceptual
    ------------------
    Candidato A:

        Coincide por CUIT.

    Candidato B:

        Coincide por razón social.

    Si ambos son proveedores diferentes, el documento podría
    contener información contradictoria o mezclada.

    Parámetros
    ----------
    candidatos:

        Lista ordenada de candidatos.

    Retorna
    -------
    bool

        True si existe contradicción importante.
    """

    candidatos_por_cuit = [
        candidato
        for candidato in candidatos
        if candidato.coincide_cuit
    ]

    candidatos_por_razon = [
        candidato
        for candidato in candidatos
        if candidato.coincide_razon_social
    ]

    if not candidatos_por_cuit:
        return False

    if not candidatos_por_razon:
        return False

    identificadores_cuit = {
        candidato.proveedor.identificador
        for candidato in candidatos_por_cuit
    }

    identificadores_razon = {
        candidato.proveedor.identificador
        for candidato in candidatos_por_razon
    }

    # ------------------------------------------------------
    # Si existe al menos un proveedor respaldado por ambas
    # fuentes, no consideramos automáticamente que exista una
    # contradicción.
    # ------------------------------------------------------

    if identificadores_cuit.intersection(
        identificadores_razon
    ):

        return False

    return True

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN hay_contradiccion_cuit_nombre()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN existe_empate_principal()
# ----------------------------------------------------------

def existe_empate_principal(
    candidatos: list[CandidatoProveedor]
) -> bool:
    """
    Comprobar si los dos mejores candidatos tienen el mismo
    puntaje.

    Un empate impide elegir arbitrariamente un proveedor.

    Parámetros
    ----------
    candidatos:

        Lista ordenada de candidatos.

    Retorna
    -------
    bool

        True si hay empate en el primer lugar.
    """

    if len(candidatos) < 2:
        return False

    primero = candidatos[0]
    segundo = candidatos[1]

    return primero.puntaje == segundo.puntaje

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN existe_empate_principal()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE EVALUACIÓN DE RESULTADOS
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE CONSTRUCCIÓN DE RESPUESTAS
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN crear_resultado_no_detectado()
# ----------------------------------------------------------

def crear_resultado_no_detectado(
    metodo: str,
    advertencias: Optional[list[str]] = None,
    candidatos: Optional[list[CandidatoProveedor]] = None
) -> dict:
    """
    Crear un resultado defensivo de proveedor no detectado.

    Esta función mantiene una estructura compatible con
    main.py.

    Parámetros
    ----------
    metodo:

        Motivo interno por el cual no se seleccionó un
        proveedor.

    advertencias:

        Lista opcional de observaciones.

    candidatos:

        Lista opcional de candidatos encontrados.

    Retorna
    -------
    dict

        Resultado estructurado con proveedor_detectado=False.
    """

    advertencias = (
        list(advertencias)
        if advertencias
        else []
    )

    candidatos_resumidos = []

    if candidatos:

        for candidato in candidatos[:5]:

            candidatos_resumidos.append(
                {
                    "identificador": (
                        candidato.proveedor.identificador
                    ),
                    "razon_social": (
                        candidato.proveedor.razon_social
                    ),
                    "cuit": candidato.proveedor.cuit,
                    "puntaje": candidato.puntaje,
                    "coincide_cuit": (
                        candidato.coincide_cuit
                    ),
                    "coincide_razon_social": (
                        candidato.coincide_razon_social
                    ),
                    "coincide_nombre_fantasia": (
                        candidato.coincide_nombre_fantasia
                    ),
                }
            )

    return {
        "proveedor_detectado": False,
        "identificador": None,
        "nombre_proveedor": None,
        "razon_social_encontrada": None,
        "cuit_encontrado": None,
        "metodo_deteccion": metodo,
        "nivel_confianza": "ninguna",
        "puntaje": 0,
        "advertencias": advertencias,
        "candidatos": candidatos_resumidos,
    }

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN crear_resultado_no_detectado()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN crear_resultado_detectado()
# ----------------------------------------------------------

def crear_resultado_detectado(
    candidato: CandidatoProveedor,
    advertencias: Optional[list[str]] = None
) -> dict:
    """
    Crear el resultado final para un proveedor detectado.

    Los valores se obtienen siempre desde supplier_catalog.py.

    Nunca se devuelve como razón social el alias encontrado
    dentro del PDF.

    Esto garantiza que, por ejemplo, el texto:

        AARTA DE GONZALEZ S.R.L.

    produzca:

        ARTA DE GONZALEZ S.R.L.

    Parámetros
    ----------
    candidato:

        Candidato seleccionado.

    advertencias:

        Observaciones adicionales.

    Retorna
    -------
    dict

        Resultado compatible con main.py.
    """

    proveedor = candidato.proveedor

    advertencias_finales = list(
        candidato.advertencias
    )

    if advertencias:

        advertencias_finales.extend(
            advertencias
        )

    # ------------------------------------------------------
    # Eliminamos advertencias duplicadas conservando su
    # orden original.
    # ------------------------------------------------------

    advertencias_finales = list(
        dict.fromkeys(
            advertencias_finales
        )
    )

    return {
        "proveedor_detectado": True,
        "identificador": proveedor.identificador,

        # --------------------------------------------------
        # nombre_proveedor mantiene compatibilidad con el
        # main.py actual.
        #
        # Si existe nombre de fantasía, se utiliza ese valor.
        #
        # En caso contrario, se utiliza la razón social.
        # --------------------------------------------------

        "nombre_proveedor": proveedor.nombre_preferido(),

        # --------------------------------------------------
        # Aunque la clave se llame razon_social_encontrada
        # por compatibilidad histórica, devolvemos la razón
        # social canónica.
        #
        # No devolvemos el alias defectuoso extraído.
        # --------------------------------------------------

        "razon_social_encontrada": proveedor.razon_social,

        "cuit_encontrado": proveedor.cuit,

        "metodo_deteccion": determinar_metodo_deteccion(
            candidato
        ),

        "nivel_confianza": determinar_nivel_confianza(
            candidato
        ),

        "puntaje": candidato.puntaje,

        # --------------------------------------------------
        # Campos adicionales para depuración y futuras
        # versiones.
        #
        # main.py puede ignorarlos sin romperse.
        # --------------------------------------------------

        "nombre_fantasia": proveedor.nombre_fantasia,
        "razon_social_canonica": proveedor.razon_social,
        "cuit_canonico": proveedor.cuit,
        "alias_encontrados": tuple(
            candidato.alias_encontrados
        ),
        "evidencias": tuple(
            candidato.evidencias
        ),
        "advertencias": advertencias_finales,
    }

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN crear_resultado_detectado()
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE CONSTRUCCIÓN DE RESPUESTAS
# ==========================================================


# ==========================================================
# INICIO DE LA FUNCIÓN PÚBLICA PRINCIPAL
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN detectar_proveedor()
# ----------------------------------------------------------

def detectar_proveedor(texto: object) -> dict:
    """
    Detectar el proveedor emisor dentro del texto de una
    factura.

    Esta es la función pública principal del módulo.

    Flujo
    -----
    1. Valida el texto recibido.
    2. Obtiene todos los candidatos.
    3. Excluye al receptor.
    4. Comprueba contradicciones.
    5. Comprueba empates.
    6. Evalúa la fuerza del mejor candidato.
    7. Devuelve datos canónicos si la detección es segura.
    8. Devuelve proveedor no reconocido si existe
       ambigüedad.

    Parámetros
    ----------
    texto:

        Texto extraído desde el PDF.

    Retorna
    -------
    dict

        Diccionario compatible con el main.py actual.
    """

    # ------------------------------------------------------
    # Validamos que el valor pueda convertirse en texto útil.
    # ------------------------------------------------------

    if texto is None:

        return crear_resultado_no_detectado(
            metodo="texto_ausente",
            advertencias=[
                "No se recibió texto para analizar."
            ]
        )

    texto_original = str(
        texto
    )

    if not texto_original.strip():

        return crear_resultado_no_detectado(
            metodo="texto_vacio",
            advertencias=[
                "El texto recibido está vacío."
            ]
        )

    candidatos = obtener_candidatos(
        texto_original
    )

    if not candidatos:

        return crear_resultado_no_detectado(
            metodo="sin_coincidencias",
            advertencias=[
                (
                    "No se encontró ningún CUIT, razón "
                    "social o alias de proveedor conocido."
                )
            ]
        )

    # ------------------------------------------------------
    # Si existe una contradicción fuerte entre CUIT y razón
    # social, no elegimos un proveedor automáticamente.
    # ------------------------------------------------------

    if hay_contradiccion_cuit_nombre(
        candidatos
    ):

        return crear_resultado_no_detectado(
            metodo="evidencia_contradictoria",
            advertencias=[
                (
                    "El CUIT encontrado y la razón social "
                    "encontrada parecen corresponder a "
                    "proveedores diferentes."
                ),
                (
                    "El documento requiere revisión manual "
                    "antes de asignar un proveedor."
                ),
            ],
            candidatos=candidatos
        )

    # ------------------------------------------------------
    # Un empate entre los mejores candidatos se considera
    # ambiguo.
    # ------------------------------------------------------

    if existe_empate_principal(
        candidatos
    ):

        return crear_resultado_no_detectado(
            metodo="candidatos_empatados",
            advertencias=[
                (
                    "Se encontraron varios proveedores con "
                    "el mismo nivel de evidencia."
                ),
                (
                    "No se seleccionó ninguno para evitar "
                    "una asignación incorrecta."
                ),
            ],
            candidatos=candidatos
        )

    mejor_candidato = candidatos[0]

    # ------------------------------------------------------
    # Una coincidencia exclusivamente por nombre de fantasía
    # corto se considera evidencia débil.
    #
    # Por ejemplo, DBA puede aparecer en otros contextos.
    # ------------------------------------------------------

    if (
        mejor_candidato.coincide_nombre_fantasia
        and
        not mejor_candidato.coincide_cuit
        and
        not mejor_candidato.coincide_razon_social
        and
        mejor_candidato.puntaje
        <= PUNTAJE_NOMBRE_FANTASIA
    ):

        return crear_resultado_no_detectado(
            metodo="coincidencia_textual_debil",
            advertencias=[
                (
                    "Solo se encontró un nombre de fantasía "
                    "sin CUIT ni razón social suficiente."
                ),
                (
                    "La evidencia no alcanza para asignar "
                    "el proveedor automáticamente."
                ),
            ],
            candidatos=candidatos
        )

    advertencias: list[str] = []

    # ------------------------------------------------------
    # Si solo encontramos el CUIT, la detección puede ser
    # válida porque el CUIT es único, pero dejamos constancia
    # de que no se confirmó textualmente la razón social.
    # ------------------------------------------------------

    if (
        mejor_candidato.coincide_cuit
        and
        not mejor_candidato.coincide_razon_social
        and
        not mejor_candidato.coincide_nombre_fantasia
    ):

        advertencias.append(
            (
                "El proveedor fue identificado por CUIT, "
                "pero no se encontró su razón social ni su "
                "nombre de fantasía en el texto."
            )
        )

    # ------------------------------------------------------
    # Si solo existe razón social sin CUIT, aceptamos la
    # detección con confianza media.
    # ------------------------------------------------------

    if (
        mejor_candidato.coincide_razon_social
        and
        not mejor_candidato.coincide_cuit
    ):

        advertencias.append(
            (
                "El proveedor fue identificado por razón "
                "social o alias, pero su CUIT no apareció "
                "en el texto."
            )
        )

    return crear_resultado_detectado(
        mejor_candidato,
        advertencias=advertencias
    )

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN detectar_proveedor()
# ----------------------------------------------------------


# ==========================================================
# FIN DE LA FUNCIÓN PÚBLICA PRINCIPAL
# ==========================================================


# ==========================================================
# INICIO DEL BLOQUE DE PRUEBAS MANUALES
# ==========================================================


# ----------------------------------------------------------
# INICIO DE LA FUNCIÓN mostrar_resultado_prueba()
# ----------------------------------------------------------

def mostrar_resultado_prueba(
    titulo: str,
    texto: str
) -> None:
    """
    Ejecutar una prueba manual y mostrar su resultado.

    Esta función solamente se utiliza al ejecutar:

        python supplier_detector.py

    No se ejecutará cuando main.py importe el módulo.

    Parámetros
    ----------
    titulo:

        Nombre descriptivo de la prueba.

    texto:

        Texto simulado de una factura.
    """

    resultado = detectar_proveedor(
        texto
    )

    print("=" * 70)
    print(titulo)
    print("=" * 70)

    for clave, valor in resultado.items():

        print(f"{clave}: {valor}")

    print()

# ----------------------------------------------------------
# FIN DE LA FUNCIÓN mostrar_resultado_prueba()
# ----------------------------------------------------------


# ----------------------------------------------------------
# INICIO DEL PUNTO DE ENTRADA DE PRUEBAS
# ----------------------------------------------------------

if __name__ == "__main__":
    """
    Estas pruebas comprueban:

    - Detección de Arta por razón social y CUIT.
    - Normalización del alias defectuoso AARTA.
    - Detección de Colppy.
    - Detección de Storni.
    - Exclusión del receptor.
    - Proveedor desconocido.
    """

    texto_arta = """
    FACTURA A
    MADERO ROOF TOP S.A.
    CUIT 30-71834746-3
    AARTA DE GONZALEZ S.R.L.
    CUIT 30-71867492-8
    """

    texto_colppy = """
    FACTURA A
    Colppy - All Online Solutions SAU
    CUIT 30-71246122-1
    Cliente MADERO ROOF TOP S.A.
    CUIT 30-71834746-3
    """

    texto_storni = """
    FACTURA C
    STORNI MARIA
    CUIT 27-30595013-6
    Receptor MADERO ROOF TOP S.A.
    CUIT 30-71834746-3
    """

    texto_solo_receptor = """
    MADERO ROOF TOP S.A.
    CUIT 30-71834746-3
    """

    texto_desconocido = """
    FACTURA DE PROVEEDOR DESCONOCIDO
    CUIT 30-00000000-0
    """

    mostrar_resultado_prueba(
        "PRUEBA 1 - ARTA CON ALIAS DEFECTUOSO",
        texto_arta
    )

    mostrar_resultado_prueba(
        "PRUEBA 2 - COLPPY",
        texto_colppy
    )

    mostrar_resultado_prueba(
        "PRUEBA 3 - STORNI MARIA",
        texto_storni
    )

    mostrar_resultado_prueba(
        "PRUEBA 4 - SOLO RECEPTOR",
        texto_solo_receptor
    )

    mostrar_resultado_prueba(
        "PRUEBA 5 - PROVEEDOR DESCONOCIDO",
        texto_desconocido
    )

# ----------------------------------------------------------
# FIN DEL PUNTO DE ENTRADA DE PRUEBAS
# ----------------------------------------------------------


# ==========================================================
# FIN DEL BLOQUE DE PRUEBAS MANUALES
# ==========================================================


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================