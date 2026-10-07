---
applyTo: "**/*.md"
description: Cómo escribir el README y los documentos
---

# Documentación

- **Un solo `README.md` en la raíz**, de máximo 2 páginas, con tabla de contenido. Cubre: cómo ejecutar, supuestos, problemas de calidad y respuestas de 1.1, hallazgos, solución técnica, decisiones tecnológicas y uso de IA.
- **Para analistas:** frases cortas, tablas antes que párrafos y títulos afirmativos.
- **Cifras** tomadas de los notebooks ejecutados o de los Excel publicados.
- **Categorías de calidad** como insignias de color: Faltantes `9063cd`, Duplicados `59cbe8`, Formato `fdda24`, Catálogo `ff7f41`, Valores `f5b6cd`.
- **Diagramas Mermaid `erDiagram`:** los atributos van como `nombre tipo [PK|FK] "comentario"`. `PK` y `FK` son palabras reservadas: nunca se usan como nombre o tipo. Valide el diagrama con el parser de Mermaid antes de publicarlo.
