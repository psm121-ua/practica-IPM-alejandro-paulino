# Falling Objects Pose Game

**Juego controlado por pose (MediaPipe + OpenCV)**

Este repositorio contiene un juego en Python donde objetos (manzanas, peras, balones) caen desde la parte superior de la cámara y el jugador los "atrapa" con las manos o pies usando los landmarks detectados por MediaPipe.

---

## Requisitos previos

* Python 3.8+ (recomendado 3.9 o 3.10)
* Cámara Web funcionando (con permisos de acceso)
* Paquetes Python:

  * `opencv-python` (OpenCV)
  * `mediapipe` (la versión que incluya `mp.tasks` y `PoseLandmarker` — normalmente MediaPipe >= 0.10+)
  * `numpy`

Puedes instalar los paquetes con pip. Se incluye ejemplo de `requirements.txt` abajo.

### requirements.txt (sugerido)

```
opencv-python>=4.5.5
mediapipe>=1.0.0
numpy>=1.19.0
```

Instalación rápida en un entorno virtual:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Imágenes/Assets

* Las imágenes `manzanas.png`, `pera.png` y `balon.png` están en la misma carpeta que el script en formato PNG.
* El script redimensiona las imágenes a `100x100` (línea `target_size = (100,100)`).

---

## Ejecución

1. Asegúrate de activar el entorno virtual (si usaste uno).
2. Ejecuta el script:

```bash
python app.py
```

### Flujo del juego

* Aparecerá una ventana de cámara con el menú inicial para seleccionar dificultad. Mantén la mano izquierda sobre la opción durante 1 segundo para confirmar.

  * `FACIL`, `MEDIO`, `DIFICIL` — esto ajusta la velocidad de los objetos (el multiplicador `speed_multiplier`).
* Selecciona la duración: `30 SEG`, `60 SEG`, `90 SEG` del mismo modo.
* Selecciona el modo: `SOLO MANOS` (solo uso de manos para atrapar frutas) o `CUERPO ENTERO` (se permiten pies para los balones).
* El juego comenzará y verás el HUD con tiempo restante y puntos.
* Cuando finalice el tiempo aparecerá la puntuación final. Presiona ENTER para reiniciar o ESC para salir.

### Controles

* `ESC` (tecla): salir del juego en cualquier menú o durante la partida.
* `ENTER` (tecla): reiniciar después de terminar la partida.
* Selecciones en menús: coloca la mano (derecha o izquierda) sobre el botón visual y mantenla 1s.

---

### Modelo Utilizado

* El modelo utilizado pertenece a la API moderna de MediaPipe (mp.tasks.vision) y se llama PoseLandmarker.
Este modelo está basado en la arquitectura BlazePose, altamente optimizada para detección rápida y precisa del cuerpo humano.

* El Pose Landmarker detecta 33 puntos clave del cuerpo, incluyendo:
    * Manos (muñecas y dedos)
    * Pies (tobillos y dedos)
    * Hombros, brazos y codos
    * Caderas, rodillas y piernas
    * Cabeza y torso

* El juego utiliza estos puntos para:
    1. Navegar por los menús moviendo la mano y manteniéndola sobre una opción.
    2. Atraparlos objetos:
        * Manzana → mano derecha
        * Pera → mano izquierda
        * Balón → pies (modo cuerpo entero)

