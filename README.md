
# Análisis Sintáctico LL(1) y SLR(1)

## 1. Información de los Estudiantes del equipo

- **Nombre del estudiante:** Camilo Álvarez Villegas, Sara Echeverri  
- **Número de clase:**  
  - Camilo Álvarez Villegas (Lunes de 6pm-9pm 7308)  
  - Sara Echeverri (Miércoles de 6pm-9pm)

## 2. Versiones del Sistema Operativo, Lenguaje de Programación y Herramientas

- **Sistema Operativo:** Windows 10 (64-bit)  
- **Lenguaje de Programación:** Python 3.9.7  
- **Herramientas y Librerías Utilizadas:**
  - Biblioteca estándar de Python (no requiere instalación adicional)

## 3. Instrucciones para Ejecutar la Implementación

1. Descargar o clonar el repositorio con los archivos:
   - `grammar.py`
   - `ll1_parser.py`
   - `slr1_parser.py`
   - `main.py`

2. Asegurarse de tener Python 3 instalado.

3. Ejecutar el script principal desde la terminal con el comando:

   ```bash
   python main.py
   ```

   o usar la extensión **Code Runner** en Visual Studio Code para ejecutar `main.py`.

4. Ingresar la gramática según el formato descrito a continuación.

5. El programa indicará si la gramática es LL(1), SLR(1), ambas o ninguna. Luego permitirá probar cadenas de entrada.

## Formato de Entrada

La entrada debe seguir el siguiente formato:

```
N
NT1 -> producción1 producción2 ...
NT2 -> producción1 producción2 ...
...
```

- `N`: Número de no terminales
- Cada producción está separada por espacios
- Las producciones se escriben en una sola línea por no terminal
- `e` representa la cadena vacía (ε)

### Ejemplo:

```
3
S -> S+T T
T -> T*F F
F -> (S) i
```

Tras ingresar la gramática, el programa indicará qué tipo de análisis es aplicable y pedirá ingresar cadenas. Las cadenas deben terminar en `$` o se agregará automáticamente.

## 4. Explicación del Algoritmo

### Análisis LL(1)

El analizador **LL(1)** usa una tabla de predicción generada a partir de los conjuntos FIRST y FOLLOW. El proceso:

- Se crea una tabla que asocia (no_terminal, terminal) con una producción.
- La pila del parser simula derivaciones.
- Se avanza por la cadena de entrada comparando con el símbolo en la cima de la pila.
- Si la tabla tiene ambigüedades (conflictos), la gramática **no es LL(1)**.

### Análisis SLR(1)

El analizador **SLR(1)** se basa en autómatas LR(0):

- Se construye una **gramática aumentada** para iniciar.
- Se generan los conjuntos de items LR(0) y las transiciones (colección canónica).
- Se construyen las tablas ACTION y GOTO.
- El parser simula el análisis usando una pila de estados y acciones (`shift`, `reduce`, `accept`).
- Si hay conflictos en la tabla ACTION, la gramática **no es SLR(1)**.

### Resultado

El programa determina si la gramática ingresada es:

- **LL(1)**
- **SLR(1)**
- **Ambas**
- **Ninguna**

Y permite ingresar cadenas para verificar si son aceptadas por la gramática, utilizando el analizador correspondiente.
