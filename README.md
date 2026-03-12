# R₀ Animation — Panel de propagación de enfermedades

Panel gráfico animado que muestra el **número reproductivo básico (R₀)** de distintas enfermedades infecciosas, con simulaciones de propagación en una comunidad de **100 personas** durante los **primeros 10 días después del inicio del brote**.

![Simulación R₀ - Panel completo](assets/r0_simulation.gif)

## Características

- **19 enfermedades** con nombres en español y valores de R₀
- **Simulación basada en agentes**: 100 puntos que se mueven aleatoriamente y **colisionan** entre sí
- **R₀ por intervalo**: cuando hay rango (ej. 12–18), se muestra el intervalo y se usa el punto medio para la simulación
- **Colores**: Susceptible (gris oscuro) → Infectado (verde) → Recuperado (gris)
- **Transmisión por contacto**: cuando un susceptible está cerca de un infectado, puede contagiarse según el R₀
- **Resultado final**: al terminar cada simulación aparece el **número total de infectados** (acumulado) en grande
- **Botón Reiniciar** en cada tarjeta para repetir la simulación

## Datos

Los datos provienen de la tabla de Wikipedia: [Basic reproduction number](https://en.wikipedia.org/wiki/Basic_reproduction_number) — "Values of R₀ and herd immunity thresholds (HITs) of contagious diseases prior to intervention".

## Cómo usar

1. **Abrir directamente**: Abre `index.html` en tu navegador.

2. **Con servidor local** (recomendado):
   ```bash
   python serve.py
   ```
   Se abrirá automáticamente en http://localhost:8765

## Generar GIF y video

```bash
pip install -r requirements.txt
python generate_gif.py
```

- **GIF**: `assets/r0_simulation.gif` — panel completo con las 19 enfermedades en grid 5×4
- **Video MP4**: `assets/r0_simulation.mp4` — requiere imagenio + ffmpeg (o imageio-ffmpeg)

El GIF incluye:
- Simulación de 10 días en todas las enfermedades
- Panel final con "Infectados tras 10 dias del inicio del brote"
- Cada celda muestra el número total de infectados al final del período
- Créditos con logo de GitHub en la parte inferior derecha

## Estructura del proyecto

```
R0_animation/
├── index.html      # Dashboard interactivo con animaciones
├── data/
│   └── diseases.json   # Datos de enfermedades
├── assets/
│   ├── r0_simulation.gif   # Animación para README
│   └── r0_simulation.mp4   # Video
├── generate_gif.py # Genera GIF y video
├── serve.py       # Servidor HTTP local
├── requirements.txt
└── README.md
```

## Referencia

Inspirado en la visualización del Guardian: [Watch how the measles outbreak spreads](https://www.theguardian.com/society/ng-interactive/2015/feb/05/-sp-watch-how-measles-outbreak-spreads-when-kids-get-vaccinated)

---

[![GitHub](https://github.com/favicon.ico)](https://github.com/JDConejeros/R0_animation) **JDConejeros/R0_animation**
