const color = nombre => getComputedStyle(document.documentElement).getPropertyValue(nombre).trim();
const coma = valor => String(valor).replace(".", ",");

function enDosLineas(texto) {
  const palabras = texto.split(" ");
  if (palabras.length < 4) return texto;
  const mitad = Math.ceil(palabras.length / 2);
  return [palabras.slice(0, mitad).join(" "), palabras.slice(mitad).join(" ")];
}

const COLOR_LECTURA = {
  "parece bajo, supera a sus pares": "--verde",
  "parece bien, está bajo sus pares": "--naranja",
  "coincide": "--gris",
};

const valoresAlFinal = {
  id: "valoresAlFinal",
  afterDatasetsDraw(grafica) {
    const { ctx } = grafica;
    ctx.save();
    ctx.font = `800 ${grafica.options.tamanoValor || 22}px ${color("--display")}`;
    ctx.fillStyle = color("--texto");
    ctx.textBaseline = "middle";
    grafica.getDatasetMeta(0).data.forEach((barra, i) => {
      ctx.fillText(`${Math.round(grafica.data.datasets[0].data[i])}%`, barra.x + 10, barra.y);
    });
    ctx.restore();
  },
};

const cuadrantes = {
  id: "cuadrantes",
  beforeDatasetsDraw(grafica) {
    const { ctx, chartArea: area, scales: { x, y } } = grafica;
    const { corte_cumplimiento: corte, margen } = grafica.options.entornos;
    const xCorte = x.getPixelForValue(corte);
    const yCero = y.getPixelForValue(0);
    const ySobre = y.getPixelForValue(margen);
    const yBajo = y.getPixelForValue(-margen);

    ctx.save();
    ctx.fillStyle = "rgba(0, 166, 118, 0.08)";
    ctx.fillRect(area.left, area.top, xCorte - area.left, ySobre - area.top);
    ctx.fillStyle = "rgba(232, 105, 43, 0.09)";
    ctx.fillRect(xCorte, yBajo, area.right - xCorte, area.bottom - yBajo);

    ctx.strokeStyle = color("--suave");
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(xCorte, area.top);
    ctx.lineTo(xCorte, area.bottom);
    ctx.moveTo(area.left, yCero);
    ctx.lineTo(area.right, yCero);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.font = `700 12px ${color("--cuerpo")}`;
    ctx.fillStyle = color("--verde");
    ctx.fillText("Cumplen poco, pero superan a sus pares", area.left + 10, area.top + 18);
    ctx.fillStyle = color("--naranja");
    ctx.textAlign = "right";
    ctx.fillText("Cumplen mucho, pero están bajo sus pares", area.right - 10, area.bottom - 12);
    ctx.restore();
  },
  afterDatasetsDraw(grafica) {
    const { ctx } = grafica;
    ctx.save();
    ctx.font = `600 12px ${color("--cuerpo")}`;
    ctx.fillStyle = color("--texto");
    ctx.strokeStyle = color("--fondo");
    ctx.lineWidth = 4;
    ctx.lineJoin = "round";
    grafica.data.datasets.forEach((serie, d) => {
      if (!serie.etiquetar) return;
      grafica.getDatasetMeta(d).data.forEach((punto, i) => {
        const x = punto.x + punto.options.radius + 4;
        ctx.strokeText(serie.data[i].entorno, x, punto.y + 4);
        ctx.fillText(serie.data[i].entorno, x, punto.y + 4);
      });
    });
    ctx.restore();
  },
};

const banda2026 = {
  id: "banda2026",
  beforeDatasetsDraw(grafica) {
    const { ctx, chartArea: area, scales: { x } } = grafica;
    const inicio = grafica.data.labels.findIndex(mes => mes.startsWith("2026"));
    if (inicio < 1) return;

    const izquierda = (x.getPixelForValue(inicio - 1) + x.getPixelForValue(inicio)) / 2;
    ctx.save();
    ctx.fillStyle = "rgba(253, 218, 36, 0.22)";
    ctx.fillRect(izquierda, area.top, area.right - izquierda, area.bottom - area.top);
    ctx.font = `700 12px ${color("--cuerpo")}`;
    ctx.fillStyle = color("--texto");
    ctx.fillText("2026: meta más alta", izquierda + 8, area.bottom - 10);
    ctx.restore();
  },
};

function prepararChart() {
  Chart.defaults.font.family = color("--cuerpo");
  Chart.defaults.color = color("--suave");
}

function graficaFactores(id, variacion, tamanoEtiqueta = 15) {
  return new Chart(document.getElementById(id), {
    type: "bar",
    data: {
      labels: variacion.map(f => enDosLineas(f.grupo)),
      datasets: [{ data: variacion.map(f => f.pct), backgroundColor: variacion.map((_, i) => (i === 0 ? color("--azul") : color("--gris"))), borderRadius: 8, barPercentage: 0.7 }],
    },
    options: {
      indexAxis: "y",
      maintainAspectRatio: false,
      tamanoValor: tamanoEtiqueta + 7,
      layout: { padding: { right: 80 } },
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: c => `Explica el ${Math.round(c.raw)}% de la variación en metas cumplidas` } } },
      scales: {
        x: { display: false, min: 0, max: Math.max(...variacion.map(f => f.pct)) },
        y: { grid: { display: false }, border: { display: false }, ticks: { color: color("--texto"), font: { size: tamanoEtiqueta, weight: 600 } } },
      },
    },
    plugins: [valoresAlFinal],
  });
}

function graficaEntornos(id, entornos) {
  const radio = equipos => 6 + equipos * 1.6;
  const serie = (lectura, etiquetar) => ({
    data: entornos.filas.filter(f => f.lectura === lectura).map(f => ({ x: f.cumplimiento, y: f.frente_a_pares, ...f })),
    backgroundColor: color(COLOR_LECTURA[lectura]),
    order: etiquetar ? 0 : 1,
    pointRadius: ctx => radio(ctx.raw?.equipos ?? 1),
    pointHoverRadius: ctx => radio(ctx.raw?.equipos ?? 1) + 3,
    etiquetar,
  });

  return new Chart(document.getElementById(id), {
    type: "scatter",
    data: {
      datasets: [
        serie("coincide", false),
        serie("parece bajo, supera a sus pares", true),
        serie("parece bien, está bajo sus pares", true),
      ],
    },
    options: {
      maintainAspectRatio: false,
      entornos,
      layout: { padding: { right: 40 } },
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: c => {
          const f = c.raw;
          const signo = f.frente_a_pares > 0 ? "+" : "";
          return [
            `${f.entorno} · ${f.equipos} equipo${f.equipos > 1 ? "s" : ""}`,
            `Metas cumplidas: ${coma(f.cumplimiento)}% (puesto ${f.puesto_cumplimiento})`,
            `Frente a sus pares: ${signo}${coma(f.frente_a_pares)} puntos (puesto ${f.puesto_justo})`,
          ];
        } } },
      },
      scales: {
        x: { min: 0, max: 80, title: { display: true, text: "% de metas cumplidas →", color: color("--texto"), font: { weight: 600 } }, ticks: { callback: v => `${v}%` }, grid: { display: false } },
        y: { min: -15, max: 25, title: { display: true, text: "Puntos frente a sus pares →", color: color("--texto"), font: { weight: 600 } }, ticks: { callback: v => (v > 0 ? `+${v}` : v) }, grid: { color: color("--linea") } },
      },
    },
    plugins: [cuadrantes],
  });
}

function graficaSeguimiento(id, seguimiento) {
  return new Chart(document.getElementById(id), {
    type: "line",
    data: {
      labels: seguimiento.map(f => f.mes),
      datasets: [
        { label: "Resultado de los equipos", data: seguimiento.map(f => f.resultado), borderColor: color("--azul"), backgroundColor: color("--azul"), borderWidth: 3, tension: 0.3, pointRadius: 0, pointHoverRadius: 5 },
        { label: "Meta", data: seguimiento.map(f => f.meta), borderColor: color("--texto"), backgroundColor: color("--texto"), borderWidth: 2.5, borderDash: [7, 5], pointRadius: 0, pointHoverRadius: 5 },
      ],
    },
    options: {
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { position: "bottom", labels: { color: color("--texto"), usePointStyle: true, pointStyle: "line", font: { size: 13 } } },
        tooltip: { callbacks: {
          label: c => `${c.dataset.label}: ${coma(c.raw.toFixed(2))}%`,
          afterBody: c => `Cumplieron: ${Math.round(seguimiento[c[0].dataIndex].cumplieron)}% de los equipos`,
        } },
      },
      scales: {
        y: { min: 98.6, max: 100, ticks: { callback: v => `${coma(v.toFixed(1))}%` }, grid: { color: color("--linea") } },
        x: { grid: { display: false }, ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 7 } },
      },
    },
    plugins: [banda2026],
  });
}

function sinConexion() {
  document.querySelectorAll(".lienzo").forEach(lienzo => {
    lienzo.style.height = "auto";
    lienzo.innerHTML = '<p class="etiqueta">La gráfica necesita conexión a internet para cargar Chart.js.</p>';
  });
}
