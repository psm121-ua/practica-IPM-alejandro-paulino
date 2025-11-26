## Juego Serio de Rehabilitación Controlado por Movimientos Corporales

Este proyecto es un juego serio desarrollado en Python que utiliza visión por computador (MediaPipe + OpenCV) para la interacción persona-máquina. Está diseñado con fines de rehabilitación física y evaluación de capacidades motoras.

## Propósito del Juego Serio

Este juego tiene como objetivo:

-Rehabilitación física: Mejorar la coordinación mano-ojo y el movimiento de extremidades

-Evaluación motora: Medir la capacidad de respuesta y precisión de movimientos

-Estimulación cognitiva: Requiere toma de decisiones rápidas y coordinación

-Entretenimiento terapéutico: Hacer la rehabilitación más amena y motivadora

## Estructura del Proyecto

text
.
├── 📂 __pycache__/          # Archivos cache de Python (no modificar)
├── 📂 models/               # Modelos de MediaPipe descargados
├── 🐍 app.py                # Código principal del juego
├── 🍎 manzanas.png          # Imagen de manzanas para el juego
├── 🍐 pera.png              # Imagen de peras para el juego
├── ⚽ balon.png             # Imagen de balones para el juego
├── ⚙️ config.py             # Configuración del proyecto
├── 📥 download_models.py    # Script para descargar modelos
├── 📖 README.md             # Este archivo
├── 📋 requirements.txt      # Dependencias de Python
└── .gitignore              # Archivos ignorados por Git

## Requisitos del Sistema

-Python 3.8 o superior

-Cámara web funcionando

-Sistema operativo: Windows, macOS o Linux

## Instalación y Configuración

1. Descargar todos los archivos del proyecto
Asegúrate de tener todos los archivos en la misma carpeta.

2. Crear y activar entorno virtual (recomendado)
bash
python -m venv venv

#### Windows
venv\Scripts\activate

#### macOS/Linux
source venv/bin/activate

3. Instalar dependencias
bash
pip install -r requirements.txt

4. Descargar modelos de MediaPipe
bash
python download_models.py
Nota: Si download_models.py no existe, el modelo se descargará automáticamente al ejecutar el juego por primera vez.

## Cómo Ejecutar el Juego

bash
python app.py

## Flujo del Juego

1. Selección de Dificultad

FÁCIL: Velocidad reducida (×0.6)

MEDIO: Velocidad normal (×1.0)

DIFÍCIL: Velocidad aumentada (×1.5)

2. Selección de Duración

30 SEGUNDOS: Partida rápida

60 SEGUNDOS: Partida estándar

90 SEGUNDOS: Partida larga

3. Selección de Modo de Juego

SOLO MANOS: Solo se usan las manos para interactuar

CUERPO ENTERO: Se utilizan tanto manos como pies

4. Desarrollo del Juego

Objetos que caen:

-Manzanas: Deben atraparse con la mano derecha

-Peras: Deben atraparse con la mano izquierda

-Balones: Solo en modo "CUERPO ENTERO", se atrapan con cualquier pie

Mecánica:

-Los objetos caen desde la parte superior de la pantalla

-El jugador debe mover sus extremidades para interceptarlos

-Cada objeto atrapado suma 1 punto

-El tiempo restante y puntuación se muestran en tiempo real

## Controles

-Navegación por menús: Colocar la mano izquierda sobre la opción deseada durante 1 segundo

-Durante el juego: Mover manos y pies para atrapar objetos

-ESC: Salir del juego en cualquier momento

-ENTER: Reiniciar después de terminar una partida

## Tecnologías Utilizadas

MediaPipe Pose Landmarker: Detección de 33 puntos corporales en tiempo real

OpenCV: Procesamiento de video y visualización

NumPy: Cálculos matemáticos y detección de colisiones

## Modelo de Detección Corporal

El juego utiliza MediaPipe Pose que detecta 33 puntos clave del cuerpo:

-Manos: Muñecas (puntos 15,17,19,21 y 16,18,20,22)

-Piernas: Tobillos, rodillas, caderas (puntos 27,28,31,32)

-Tronco: Caderas, hombros, cabeza

-Pies: Tobillos y puntos de referencia inferiores

## Aplicación en Salud y Rehabilitación

Este juego serio puede utilizarse para:

-Terapia ocupacional: Mejora de coordinación motora fina

-Rehabilitación post-operatoria: Ejercicios controlados de extremidades

-Prevención de fragilidad: Mantenimiento de capacidad motora en adultos mayores

-Estimulación cognitivo-motora: Integración de decisión y movimiento

## Estructura del Código Principal

El archivo app.py contiene:

-Configuración MediaPipe para detección de poses

-Clase FallingObject para gestionar objetos que caen

-Sistemas de menús interactivos (dificultad, duración, modo)

-Loop principal del juego con detección de colisiones

-Sistema de puntuación y temporización

## Notas Técnicas

-El juego requiere buena iluminación para una detección óptima

-Se recomienda mantenerse a 2-3 metros de la cámara, donde se vea el cuerpo entero en caso de elegir la opción con pies.

-La detección funciona mejor con ropa que contraste con el fondo

-En caso de problemas de detección, verificar que la cámara tenga suficiente resolución

-Los modelos se almacenan en la carpeta models/ después de la primera ejecución


#### Desarrollado para la asignatura de Interacción Persona-Máquina - Universidad de Alicante por Paulino Sanchiz y Alejandro López
