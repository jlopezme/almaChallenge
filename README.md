# Alma Challenge


## Overview

El desafio es hacer un simple bot que se conecte a ReMarkets de Rofex utilizando WebSocket (a traves de la libreria pyRofex) y que busque oportunidades de arbitraje de tasas de interes.

Se tomo la decision de utilizar 4 contratos forward (GGAL/Dic21, YPFD/Dic21, DLR/Dic21, PAMP/Dic21) y sus respectivos precios spot para calcular las tasas

## Funcionamiento

1) El programa establece una conexion con REMARKETS utilizando websocket con ayuda de la libreria pyRofex para recibir las actualizaciones de los precios de los forwards en tiempo real.
2) El sistema checkea cada 1 segundo si hubo cambios en los precios de los forwards y los spots
4) Si efectivamente hubo cambios, pasamos a usar estos updates de precios para calcular las nuevas tasas implicitas y las printeamos por consola
5) Nos fijamos si con las nuevas tasas existen oportunidades de arbritaje entre las tasas colocadoras y tomadoras
6) Finalmente, si hay oportunidades entonces imprimimos por consola los datos necesarios para generar el trade del arbitraje en cuestion


## Instrucciones

- Para correr el mini bot hayque estar ubicado en un environment que tenga instaladas por lo menos las librerias pyRofex y yfinance.
- Al estar utilizando Remarkets, nos encontramos con el problema de que no todas las puntas tienen cotizacion (a menos que uno se conecte a traves de LIVE), entonces tienen que asegurarse que por lo menos 3 de los contratos forwards que utilicen (los pueden cambiar en el codigo) tengan precios `bid` y `offer` en remarkets (yo agregue precios artificialmente ya que es una simulacion). Esta es una precondicion para que corra bien el programa.
- Luego, simplemente ejecutar:

```
python tasas.py
```

- Para correr los dos tests (hubo que ponerlos en distintos archivos por un problema con websocket y la libreria pyRofex) ejecutar:

```
python test_oportunidades.py
```
```
python test_tasas.py
```
