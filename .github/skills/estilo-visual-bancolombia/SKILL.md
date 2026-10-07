---
name: estilo-visual-bancolombia
description: Paleta, tipografía y reglas de accesibilidad para gráficas de notebooks, la presentación HTML y mockups. Cargar antes de escribir una gráfica, HTML o CSS.
---

# Estilo visual (inspirado en el sistema de diseño de Bancolombia)

## Colores
| Token | Hex | Uso |
|---|---|---|
| amarillo | `#fdda24` | Acento y estados activos; nunca texto sobre blanco |
| verde | `#00c389` | Cumple / positivo |
| naranja | `#ff7f41` | Alerta / por debajo de la meta |
| morado | `#9063cd` | Serie secundaria, elementos de IA |
| azul | `#59cbe8` | Serie de datos / información |
| rosado | `#f5b6cd` | Acentos suaves |
| negro | `#2a2625` | Texto principal y superficies oscuras |
| rojo | `#e03c31` | "Falta" / "no está en el catálogo" |
| grises | `#9e9a99`, `#e6e3e2` | Sin dato, ejes, bordes |

## Reglas
- **Texto:** negro sobre claro o blanco sobre oscuro. Los colores de marca son rellenos y marcas, no texto.
- **Estados fijos:** verde = cumple, naranja = alerta, gris = sin dato. Nunca se codifica un estado solo con color: se agrega etiqueta o símbolo (✓ ≈ ✗).
- **Series:** máximo 5, en orden azul, morado, verde, naranja, rosado; el resto va en "Otros".
- **Gráficas:**
  - etiquetas directas antes que leyendas;
  - barras desde cero;
  - sin 3D ni cuadrícula recargada;
  - se quitan los bordes superior y derecho;
  - título a la izquierda que dice la conclusión.
- **Diapositivas:**
  - una idea por diapositiva;
  - máximo 25 palabras de texto;
  - los números más grandes que las palabras;
  - máximo 3 diapositivas y 2 gráficas.
- **Tipografía:** `"Open Sans", "Segoe UI", system-ui, sans-serif`. Negrita solo para títulos y cifras clave.
