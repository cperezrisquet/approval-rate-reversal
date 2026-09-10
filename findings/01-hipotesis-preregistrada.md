# Hipótesis, fijada ANTES de ver los datos

Segmentación elegida: **loan_purpose** (compra / mejora / refinanciación /
cash-out refi / otro).

Mecanismo esperado, a priori: el volumen de refinanciación se mueve con los
tipos de interés mucho más que el de compra, y las refis tienen tasa de
aprobación distinta (más denegaciones por crédito y por colateral). Si entre
2024 y 2025 la composición se desplaza hacia refi, la tasa agrupada puede
caer aunque cada propósito mejore su propia tasa.

Predicción: componente de mezcla negativo y de magnitud mayor que el
componente intra-estrato.

Esto NO es un barrido en busca de la segmentación que revierte. La
segmentación se fija por el mecanismo; el barrido sobre las demás va después
y se reporta como distribución completa, no como máximo.

Definición de la tasa: (1 + 2) / (1 + 2 + 3) sobre action_taken.
Excluidas 4 (retirada), 5 (incompleta) y 6 (comprada): no son decisiones
del prestamista.
