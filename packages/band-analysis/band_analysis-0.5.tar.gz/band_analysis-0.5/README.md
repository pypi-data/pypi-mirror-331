# Análisis de Imágenes de Electroforesis

## Descripción

Este paquete en Python permite el análisis de imágenes de electroforesis en gel, proporcionando herramientas para:

- Detección automática de bandas incluso en condiciones de bajo contraste.
- Identificación del marcador de peso molecular y ajuste de curvas en base a su distribución de bandas.
- Identificación de carriles y asignación automática del peso molecular aproximado de cada banda.
- Construcción automática de dataframes para análisis masivo de datos de imagen de geles de electroforesis.

## Funciones principales
- `interactive_image`: función para generar una matriz interactiva que muestre el peso molecular aproximado de bandas seleccionadas con el ratón.
- `excel_band_results`: función para generar un dataframe y archivo en excel con el peso molecular aproximado de cada banda, en cada uno de los carriles identificados.
- `get_exp_ladder`: función para obtener las coordenadas en el eje vertical de las bandas del marcador de peso molecular.
- `get_band_info`: función para agrupar pixeles pertenecientes a una misma banda y contar el número total de estas.
- `get_calib_param`: función para realizar una regresión cuadrática a partir de la distribución de bandas en el marcador de peso molecular.
- `assign_mol_wei`: función para marcar cada banda con su peso molecular aproximado.

Cada función dentro del paquete está titulada con su propósito y contiene la descripción de las variables de entrada y salida.

## Instalación y uso

1. Descarga el archivo EG_analysis.py y colócalo en el mismo directorio que el script desde el cual deseas ejecutarlo.
2. Importa el archivo en tu código y llama a la función deseada.

El código puede probarse con la imagen del gel subida al repositorio llamada [electro_gel_test](electro_gel_test.png).

### Ejemplo básico de uso:
```bash
import EG_Analysis as eg

ruta_imagen = "ruta/al/archivo.png"
imagen_PAGE = eg.open_cv2_image(ruta_imagen, escala_grises=False)
ladder = [1200,1000,900,800,700,600,500,400,300]
eg.interactive_image(imagen_PAGE, ladder)
```
## Requisitos

### Este paquete requiere las siguientes dependencias:

- Python 3.8+

- OpenCV

- NumPy

- SciPy

- Matplotlib

Para instalarlas:

```bash
pip install -r requirements.txt
```

## Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un fork del repositorio.

2. Crea una nueva rama (git checkout -b nueva-funcionalidad).

3. Realiza tus cambios y haz commit (git commit -m "Descripción del cambio").

4. Envía un pull request.

## Licencia
Este proyecto está bajo la licencia MIT.

---
Este paquete facilita la automatización del análisis de geles de electroforesis, asegurando precisión en la detección de bandas y asignación de pesos moleculares. ¡Esperamos que sea de utilidad!

