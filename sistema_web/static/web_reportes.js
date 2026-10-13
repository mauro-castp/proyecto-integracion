(() => {
  const aviso = document.getElementById('grafica-aviso');
  if (!window.Highcharts) {
    aviso.textContent = 'No se pudo cargar Highcharts. Puedes consultar la tabla y exportar los datos.';
    return;
  }
  const estados = JSON.parse(document.getElementById('datos-estados').textContent);
  const dias = JSON.parse(document.getElementById('datos-diarios').textContent);
  Highcharts.chart('grafica-estados', {
    chart: { type: 'column' }, title: { text: 'Pedidos por estado' },
    xAxis: { categories: estados.map(r => r.estado) },
    yAxis: { min: 0, allowDecimals: false, title: { text: 'Pedidos' } },
    series: [{ name: 'Pedidos', data: estados.map(r => r.cantidad) }]
  });
  Highcharts.chart('grafica-diaria', {
    chart: { type: 'line' }, title: { text: 'Pedidos por día' },
    xAxis: { categories: dias.map(r => r.dia) },
    yAxis: { min: 0, allowDecimals: false, title: { text: 'Pedidos' } },
    series: [{ name: 'Pedidos', data: dias.map(r => r.cantidad) }]
  });
  aviso.textContent = 'Las gráficas reflejan todos los pedidos del filtro, independientemente de la página.';
})();
