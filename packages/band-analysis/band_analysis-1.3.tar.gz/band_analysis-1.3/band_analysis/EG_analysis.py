import cv2
import numpy as np
import random
import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

import cv2

print('Paquete EG_analysis importado correctamente')

# Función para cargr imagenes de geles de electroforesis en formato png
def open_cv2_image(ruta_imagen, show=False, escala_grises=False):
    """
    Carga una imagen usando OpenCV.

    Parámetros:
    - ruta_imagen: str, ruta de la imagen a cargar.
    - escala_grises: bool, si es True, carga la imagen en escala de grises.

    Retorna:
    - imagen: numpy array con la imagen cargada.
    """
    
    # Cargar la imagen en color o en escala de grises según el parámetro
    flag = cv2.IMREAD_GRAYSCALE if escala_grises else cv2.IMREAD_COLOR
    imagen = cv2.imread(ruta_imagen, flag)

    # Validar que la imagen se haya cargado correctamente
    if imagen is None:
        raise FileNotFoundError(f"No se pudo cargar la imagen en la ruta: {ruta_imagen}")
    
    # Mostrar la imagen con las bandas coloreadas si se quiere
    if show == True:
        cv2.imshow("Imagen a procesar", imagen)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    


    return imagen

# Función para redimensionar las imagenes de geles de electroforesis
def resize_image(ruta_imagen, porcentaje_reduccion=0):
    """
    Carga y redimensiona una imagen usando OpenCV.

    Parámetros:
    - ruta_imagen: str, ruta de la imagen a cargar.
    - porcentaje_reduccion: float, porcentaje de reducción del tamaño (0 a 100).

    Retorna:
    - imagen_redimensionada: numpy array con la imagen redimensionada.
    """

    # Cargar la imagen
    imagen_cv2 = cv2.imread(ruta_imagen)
    if imagen_cv2 is None:
        raise FileNotFoundError(f"No se pudo cargar la imagen en la ruta: {ruta_imagen}")

    # Calcular el nuevo tamaño
    nuevo_ancho = int(imagen_cv2.shape[1] * ((100 - porcentaje_reduccion) / 100))
    nuevo_alto = int(imagen_cv2.shape[0] * ((100 - porcentaje_reduccion) / 100))

    # Redimensionar la imagen
    imagen_redimensionada = cv2.resize(imagen_cv2, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_AREA)

    return imagen_redimensionada

# Función para asignar nombres a archivos de salida en base al nombre de la imagen original
def get_new_name(ruta_original, sufijo="_modificada", formato=".png"):
    """
    Genera un nuevo nombre de archivo basado en la ruta original, agregando un sufijo y cambiando el formato si es necesario.

    Parámetros:
    - ruta_original: Ruta completa del archivo original, incluyendo su nombre y extensión.
    - sufijo (opcional): Texto adicional que se agregará al final del nombre del archivo original antes de la nueva extensión. 
      Por defecto, es "_modificada".
    - formato (opcional): Extensión del nuevo archivo, incluyendo el punto (ejemplo: ".png", ".jpg", ".xlsx").
      Por defecto, es ".png".

    Retorna:
    - nueva_ruta: Ruta completa del nuevo archivo con el sufijo y el formato especificado.
    """

    # Extraer el directorio, el nombre del archivo y la extensión
    directorio, nombre_archivo = os.path.split(ruta_original)
    nombre_base, _ = os.path.splitext(nombre_archivo)
    
    # Crear el nuevo nombre de archivo
    nuevo_nombre = f"{nombre_base}{sufijo}{formato}"
    nueva_ruta = os.path.join(directorio, nuevo_nombre)
    
    # Devolver la nueva ruta del archivo modificado
    return nueva_ruta

# Función para obtener las coordenadas en el eje vertical de las bandas del marcador de peso molecular
def get_exp_ladder(imagen_cv2):
    """
    Extrae las posiciones verticales (coordenadas Y) de las bandas del ladder experimental en una imagen de electroforesis.

    Parámetros:
    - imagen_cv2: Imagen en formato OpenCV (matriz numpy) que representa un gel de electroforesis. 
      Debe estar cargada correctamente, de lo contrario, se lanzará un error.

    Retorna:
    - ladder_exp: Lista de coordenadas Y correspondientes a las bandas detectadas en el ladder experimental.
    """

    # Verificar que la imagen se cargó correctamente
    if imagen_cv2 is None:
        raise ValueError("No se pudo cargar la imagen. Verifique la ruta del archivo.")

    # Convertir la imagen a escala de grises y aplicar umbralización de Otsu
    imagen_gris = cv2.cvtColor(imagen_cv2, cv2.COLOR_BGR2GRAY)
    _, imagen_binaria = cv2.threshold(imagen_gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Identificar componentes conectados (bandas)
    num_labels, labels = cv2.connectedComponents(imagen_binaria)

    # Asignar colores aleatorios a cada componente (excepto el fondo)
    imagen_coloreada = cv2.cvtColor(imagen_binaria, cv2.COLOR_GRAY2BGR)
    colores_rgb = {i: (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(1, num_labels)}

    # Listas auxiliares
    x_puntos = []  # Almacena las posiciones en X para identificar columnas
    colores_asignados = []  # Guarda los colores asignados a cada banda
    ladder_exp = []  # Guarda las coordenadas Y del ladder experimental

    # Iterar sobre cada banda detectada (excepto el fondo)
    for label in range(1, num_labels):
        y_coords, x_coords = np.where(labels == label)
        if len(x_coords) > 0 and len(y_coords) > 0:
            centro_x = int(np.mean(x_coords))  # Coordenada X del centro de la banda
            centro_y = int(np.mean(y_coords))  # Coordenada Y del centro de la banda

        # Asignar un color aleatorio
        color_asignado = colores_rgb[label]

        # Evitar que bandas cercanas tengan colores distintos
        for num in x_puntos:
            if abs(centro_x - num) <= 5:
                color_asignado = colores_asignados[x_puntos.index(num)]
                break

        # La primera banda detectada se deja en blanco (ladder)
        if label == 1:
            color_asignado = (255, 255, 255)

        # Si la banda es del ladder, guardar su coordenada Y
        if color_asignado == (255, 255, 255):
            ladder_exp.append(centro_y)

        # Registrar coordenadas y colores
        x_puntos.append(centro_x)
        colores_asignados.append(color_asignado)

    return ladder_exp

# Función para agrupar pixeles pertenecientes a una misma banda y contar el número total de estas
def get_band_info(imagen_cv2):
    """
    Procesa una imagen de electroforesis para detectar y segmentar bandas mediante umbralización de Otsu y análisis de componentes conectados.

    Parámetros:
    - imagen_cv2: Imagen en formato OpenCV (matriz numpy). Debe estar correctamente cargada, de lo contrario, se lanzará un error.

    Retorna:
    - band_info: Tupla que contiene:
        * num_labels (int): Número total de bandas detectadas (incluyendo el fondo).
        * labels (numpy.ndarray): Matriz de etiquetas donde cada píxel está asignado a un componente identificado.
    """

    # Verificar que la imagen se cargó correctamente
    if imagen_cv2 is None:
        raise ValueError("No se pudo cargar la imagen. Verifique la ruta del archivo.")

    # Convertir la imagen a escala de grises y aplicar umbralización de Otsu
    imagen_gris = cv2.cvtColor(imagen_cv2, cv2.COLOR_BGR2GRAY)
    _, imagen_binaria = cv2.threshold(imagen_gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Identificar componentes conectados (bandas)
    num_labels, labels = cv2.connectedComponents(imagen_binaria)

    # Retornar información de las bandas detectadas
    return num_labels, labels

# Función para verificar la correcta agrupación y alineamiento de bandas
def verify_correct_gel(ruta_imagen, show=False):
    """
    Verifica si una imagen de electroforesis en gel es válida, segmentando las bandas y resaltando sus centros con colores.

    Parámetros:
    - ruta_imagen (str): Ruta del archivo de imagen que se analizará.
    - show (bool): Indica si se quiere mostrar la imagen de verificación o no

    Retorna:
    - imagen_coloreada (numpy.ndarray): Imagen procesada con bandas coloreadas y centros de masa resaltados.

    Procedimiento:
    1. Carga la imagen usando OpenCV.
    2. Convierte la imagen a escala de grises y aplica umbralización de Otsu.
    3. Identifica componentes conectados en la imagen binaria.
    4. Asigna colores aleatorios a cada banda detectada.
    5. Dibuja un círculo rojo en el centro de cada banda.
    6. Guarda y muestra la imagen procesada.
    """

    # Cargar la imagen usando OpenCV
    imagen_cv2 = cv2.imread(ruta_imagen)
    if imagen_cv2 is None:
        raise ValueError("No se pudo cargar la imagen. Verifique la ruta del archivo.")

    # Convertir la imagen a escala de grises y aplicar umbralización de Otsu
    imagen_gris = cv2.cvtColor(imagen_cv2, cv2.COLOR_BGR2GRAY)
    _, imagen_binaria = cv2.threshold(imagen_gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Identificar componentes conectados (bandas)
    num_labels, labels = cv2.connectedComponents(imagen_binaria)
    print(f"Número de componentes detectadas (incluyendo el fondo): {num_labels}")

    # Asignar colores aleatorios a cada banda (excepto el fondo)
    imagen_coloreada = cv2.cvtColor(imagen_binaria, cv2.COLOR_GRAY2BGR)
    colores_rgb = {i: (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(1, num_labels)}

    x_puntos = []
    colores_asignados = []

    # Procesar cada banda detectada
    for label in range(1, num_labels):
        y_coords, x_coords = np.where(labels == label)
        if len(x_coords) > 0 and len(y_coords) > 0:
            centro_x = int(np.mean(x_coords))
            centro_y = int(np.mean(y_coords))

        # Asignar color único a la banda
        color_asignado = colores_rgb[label]
        for num in x_puntos:
            if abs(centro_x - num) <= 5:
                color_asignado = colores_asignados[x_puntos.index(num)]
                break

        # La primera banda se deja en blanco
        if label == 1:
            color_asignado = (255, 255, 255)

        # Colorear la banda y marcar el centro con un círculo rojo
        imagen_coloreada[labels == label] = color_asignado
        cv2.circle(imagen_coloreada, (centro_x, centro_y), radius=5, color=(0, 0, 255), thickness=-1)

        x_puntos.append(centro_x)
        colores_asignados.append(color_asignado)

    # Guardar la imagen procesada
    cv2.imwrite(get_new_name(ruta_imagen, sufijo="_verificado", formato=".png"), imagen_coloreada)

    # Mostrar la imagen con las bandas coloreadas si se quiere
    if show == True:
        cv2.imshow("Imagen Procesada", imagen_coloreada)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return imagen_coloreada

# Función para realizar una regresión cuadrática a partir de la distribución de bandas en el marcador de peso molecular
def get_calib_param(ladder, ladder_exp, ruta_imagen, show=False):
    """
    Calcula los parámetros de calibración para la estimación del peso molecular
    ajustando una curva cuadrática a los datos experimentales.

    Parámetros:
    - ladder (list): Lista con los valores teóricos del peso molecular del marcador.
    - ladder_exp (list): Lista con las posiciones experimentales del marcador en el gel.
    - ruta_imagen (str): Ruta de la imagen asociada al gel de electroforesis.
    - show (bool): Indica si se quiere mostrar la imagen de la curva o no

    Retorna:
    - parametros (tuple): Tupla con los coeficientes óptimos (a, b, c) del ajuste cuadrático.

    Procedimiento:
    1. Convierte las listas de entrada a arrays de NumPy.
    2. Define un modelo cuadrático de ajuste.
    3. Ajusta la curva utilizando `curve_fit` para encontrar los parámetros óptimos.
    4. Genera una curva de ajuste basada en los parámetros calculados.
    5. Grafica los datos experimentales junto con la curva ajustada.
    6. Guarda la gráfica en un archivo y la muestra en pantalla.
    """

    # Convertir listas a arrays de NumPy
    x_data = np.array(ladder_exp)
    y_data = np.array(ladder)

    # Definir la función modelo (se propone un modelo cuadrático)
    def modelo(x, a, b, c):
        return a * (x**2) + b * x + c

    # Ajustar la curva
    parametros, _ = curve_fit(modelo, x_data, y_data)
    a_opt, b_opt, c_opt = parametros

    # Crear puntos para graficar la curva ajustada
    x_fit = np.linspace(min(x_data), max(x_data), 100)
    y_fit = modelo(x_fit, a_opt, b_opt, c_opt)

    # Graficar los datos originales y la curva ajustada
    plt.scatter(x_data, y_data, label="Datos", color="red")
    plt.plot(x_fit, y_fit, label=f"Ajuste: y = {a_opt:.4f}x^2 + {b_opt:.4f}x + {c_opt:.4f}", color="blue")
    plt.xlabel("Marcador de peso molecular teórico (bp)")
    plt.ylabel("Marcador de peso molecular experimental (bp)")
    plt.legend()
    plt.grid()

    # Guardar la gráfica con un nombre modificado
    plt.savefig(get_new_name(ruta_imagen, sufijo="_calibration", formato=".png"))

    if show == True:
        plt.show()

    return parametros

# Función para marcar cada banda con su peso molecular aproximado
def assign_mol_wei(ruta_imagen, imagen_coloreada, band_info, parametros, show=False):
    """
    Asigna un peso molecular a cada componente identificado en la imagen de electroforesis,
    colorea las bandas y etiqueta cada banda con el peso molecular estimado.

    Parámetros:
    - ruta_imagen: Ruta de la imagen original utilizada para la anotación.
    - imagen_coloreada: Imagen donde se asignarán los colores a las bandas detectadas.
    - band_info: Tupla que contiene el número total de etiquetas (num_labels) y la matriz de etiquetas (labels).
    - parametros: Tupla con los coeficientes (a_opt, b_opt, c_opt) de la función cuadrática para estimar el peso molecular.
    - show (bool): Indica si se quiere mostrar la imagen anotada o no

    Retorna:
    - imagen_texto: Imagen con las bandas coloreadas y los pesos moleculares etiquetados.
    """

    # Cargar imagen para mostrar los pesos moleculares
    imagen_texto = open_cv2_image(ruta_imagen)
    # Cargar parámetros de la curva de calibración
    a_opt, b_opt, c_opt = parametros
    # Cargar número de bandas y lista de bandas
    num_labels, labels = band_info

    # Listas para almacenar coordenadas y colores asignados
    x_puntos = []
    colores_asignados = []
    colores_rgb = {i: (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(1, num_labels)}

    for label in range(1, num_labels):
        # Obtener coordenadas de los píxeles de la etiqueta actual
        y_coords, x_coords = np.where(labels == label)
        
        if len(x_coords) > 0 and len(y_coords) > 0:
            # Calcular el centro de masa del componente
            centro_x = int(np.mean(x_coords))
            centro_y = int(np.mean(y_coords))

            # Calcular peso molecular aproximado
            aprox_wei = round(a_opt * (centro_y**2) + b_opt * centro_y + c_opt, 1)

            # Asignar color
            color_asignado = colores_rgb[label]

            # Evitar colores duplicados en bandas cercanas
            for num in x_puntos:
                if abs(centro_x - num) <= 5:
                    color_asignado = colores_asignados[x_puntos.index(num)]  
                    break

            # La primera banda se deja en blanco
            if label == 1:
                color_asignado = (255, 255, 255)

            # Agregar texto a la imagen si la banda no es blanca
            if color_asignado != (255, 255, 255):
                cv2.putText(imagen_texto, str(aprox_wei), (centro_x - 20, centro_y), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 2)

            # Aplicar color a la imagen
            imagen_coloreada[labels == label] = color_asignado

            # Registrar el color asignado
            x_puntos.append(centro_x)
            colores_asignados.append(color_asignado)
    
    # Guardar imagen coloreada
    cv2.imwrite(get_new_name(ruta_imagen, sufijo="_anotado", formato=".png"), imagen_texto)

    # Mostrar imagen si se quiere
    if show == True:
        cv2.imshow("Imagen anotada", imagen_texto)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    return imagen_texto

# Función para generar una matriz interactiva que muestre el peso molecular aproximado de bandas seleccionadas con el ratón
def interactive_image(imagen_cv2, ladder):
    """
    Abre una imagen de electroforesis interactiva donde, al hacer clic en una banda, se muestra su peso molecular estimado.

    Parámetros:
    - imagen_cv2: imagen del gel de electroforesis, previamente cargada.
    - ladder (list): Lista con los valores teóricos del peso molecular del marcador.
    """
    # Convertir imagen a escala de grises
    imagen_gris = cv2.cvtColor(imagen_cv2, cv2.COLOR_BGR2GRAY)

    # Aplicar umbralización de Otsu
    _, imagen_binaria = cv2.threshold(imagen_gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Identificar componentes conectados
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(imagen_binaria)

    # Definir el ladder de calibración
    ladder_teorico = np.array(ladder)
    ladder_experimental = [int(c[1]) for c in centroids[1:len(ladder_teorico) + 1]]  # Tomamos el eje Y de cada centro

    # Ajustar la curva de calibración (modelo cuadrático)
    def modelo(x, a, b, c):
        return a * (x ** 2) + b * x + c

    parametros, _ = curve_fit(modelo, ladder_experimental, ladder_teorico)
    a_opt, b_opt, c_opt = parametros

    # Función de callback para manejar clics
    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # Si se hace clic izquierdo
            label = labels[y, x]  # Identificar el componente en la posición del clic
            if label > 0:  # Evitar el fondo
                peso_molecular = round(a_opt * (y ** 2) + b_opt * y + c_opt, 1)
                print(f"Componente en ({x}, {y}) - Peso molecular aproximado: {peso_molecular} pb")

                # Dibujar un círculo donde se hizo clic
                cv2.circle(imagen_cv2, (x, y), 5, (0, 0, 255), -1)

                # Mostrar el peso molecular en la imagen
                cv2.putText(imagen_cv2, f"{peso_molecular} pb", (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                cv2.imshow("Selecciona una banda", imagen_cv2)

    # Crear la ventana y asignar la función de clic
    cv2.imshow("Selecciona una banda", imagen_cv2)
    cv2.setMouseCallback("Selecciona una banda", on_mouse)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Función para convertir una lista de listas de tuplas a un diccionario, representativo de las columnas de la imagen
def listas_a_diccionario(lista_de_listas):
    """
    Convierte una lista de listas de tuplas en un diccionario ordenado.

    :param lista_de_listas: Lista que contiene sublistas de tuplas (x, y).
    :return: Diccionario ordenado con claves del 1 en adelante.
    """
    # Ordenar la lista de listas según la primera coordenada (x) de la primera tupla de cada sublista
    lista_ordenada = sorted(lista_de_listas, key=lambda sublista: sublista[0][0])

    # Convertir a diccionario con claves en orden ascendente
    diccionario_ordenado = {i + 1: sublista for i, sublista in enumerate(lista_ordenada)}

    return diccionario_ordenado

# Función para generar un archivo de excel con el peso molecular aproximado de cada banda, en cada columna
def excel_band_results(ruta_imagen, ladder):
    """
    Analiza una imagen de electroforesis en gel y genera un archivo Excel con las bandas detectadas,
    asignando pesos moleculares a cada columna.

    Parámetros:
    - ruta_imagen (str): Ruta de la imagen a analizar.
    - ladder (list): Lista con los valores teóricos del peso molecular del marcador.
    """

    # Cargar la imagen
    imagen = cv2.imread(ruta_imagen)
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Aplicar umbralización de Otsu
    _, imagen_binaria = cv2.threshold(imagen_gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Identificar componentes conectados
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(imagen_binaria)

    # Diccionario para almacenar las columnas detectadas
    columnas = {}
    lista_coords = []

    # Colores aleatorios para cada banda, excluyendo el fondo (label 0)
    colores_rgb = {i: (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(1, num_labels)}
    lista_id = [i for i in range(1, num_labels + 1)]

    # Variables auxiliares para la identificación de columnas
    x_puntos = []  # Lista para agrupar columnas por posición X
    colores_asignados = []  # Lista de colores usados
    id_usados = []  # Lista de id usados
    ladder_exp = []  # Lista de posiciones Y del ladder
    cont = 0

    # Iterar sobre cada componente detectado (excluyendo el fondo)
    for label in range(1, num_labels):
        cont += 1
        y_coords, x_coords = np.where(labels == label)  # Obtener coordenadas de la banda
        if len(x_coords) > 0 and len(y_coords) > 0:
            centro_x = int(np.mean(x_coords))  # Centro de masa en X
            centro_y = int(np.mean(y_coords))  # Centro de masa en Y

            color_asignado = colores_rgb[label]  # Asignar color aleatorio
            columna_id = lista_id[cont - 1]

            # Verificar si la banda pertenece a una columna ya identificada
            for num in x_puntos:
                if abs(centro_x - num) <= 5:
                    color_asignado = colores_asignados[x_puntos.index(num)]  # Usar el mismo color de la banda anterior
                    columna_id = id_usados[x_puntos.index(num)]
                    cont -= 1
                    break

            if label == 1:
                color_asignado = (255, 255, 255)

            if color_asignado == (255, 255, 255):
                ladder_exp.append(centro_y)

            # Guardar la banda en su columna
            while len(lista_coords) <= columna_id:
                lista_coords.append([])  # Agregar sublistas vacías según sea necesario

            # Agregar el valor a la sublista correspondiente
            lista_coords[columna_id].append((centro_x, centro_y))

            x_puntos.append(centro_x)
            colores_asignados.append(color_asignado)
            id_usados.append(columna_id)

    # Convertir lista de coordenadas a diccionario
    lista_coords.remove(lista_coords[0])
    columnas = listas_a_diccionario(lista_coords)  # Asegúrate de tener esta función definida

    # Definir el ladder de calibración teórico
    ladder_teorico = np.array(ladder)
    ladder_experimental = np.array(sorted(ladder_exp))  # Ordenar los valores de Y

    # Ajustar la curva de calibración
    def modelo(x, a, b, c):
        return a * (x ** 2) + b * x + c

    parametros, _ = curve_fit(modelo, ladder_experimental, ladder_teorico)
    a_opt, b_opt, c_opt = parametros

    # Convertir alturas de las bandas a pesos moleculares
    for col_id in columnas:
        columnas[col_id] = [round(a_opt * (y ** 2) + b_opt * y + c_opt, 1) for x, y in sorted(columnas[col_id])]

    # Obtener la longitud máxima de las listas
    max_length = max(len(bandas) for bandas in columnas.values())

    # Rellenar las listas más cortas con NaN
    for col_id in columnas:
        while len(columnas[col_id]) < max_length:
            columnas[col_id].append(np.nan)

    # Crear DataFrame con las columnas ordenadas
    df = pd.DataFrame(dict(sorted(columnas.items())))

    df.rename(columns=lambda x: "MW" if x == 1 else f"Columna {x - 1}", inplace=True)

    # Guardar en Excel
    nombre_excel = get_new_name(ruta_imagen, sufijo="_results", formato=".xlsx")
    df.to_excel(nombre_excel, index=False)

    print(f"Archivo Excel generado con éxito: {nombre_excel}")