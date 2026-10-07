---
name: probar-hipotesis
description: Probar una hipótesis o una regla de datos contra el archivo antes de aplicarla, sin cargar el Excel completo en la conversación.
---

# Probar una hipótesis contra los datos

Antes de afirmar algo sobre los datos o de implementar una regla, se comprueba con código y se muestra la evidencia.

1. **Formular la hipótesis en una frase verificable.** Por ejemplo: "Cumplimiento = Resultado / Meta en todos los indicadores".
2. **Clasificar cada fila** con `np.select` en casos mutuamente excluyentes. Por ejemplo: `= Resultado/Meta`, `= Resultado (escala)`, `meta 0`, `no se explica`.
3. **Cruzar por indicador** (`pd.crosstab`) y mostrar 3 o 4 ejemplos de cada caso raro. Nunca se imprimen hojas completas.
4. **Decidir con el humano:**
   - **Cuándo aplicar:** la regla se aplica solo donde la evidencia es inequívoca.
   - **Qué hacer con el resto:** se conserva y se documenta.
   - **Antecedente:** recalcular todo como Resultado / Meta inventaba valores (Regulatorio topa en 1; Índice AQR's está en otra unidad), así que solo se recalcularon las encuestas.
5. **Registrar** la prueba y la decisión con la skill `bitacora-ia`, con las cifras.

Una afirmación sin prueba (por ejemplo "son el mismo frente" o "ese valor es imposible") no entra al código ni al README.
