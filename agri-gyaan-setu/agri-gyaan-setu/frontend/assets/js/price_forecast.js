window.onload = async function () {
  const cropSelect = document.getElementById('forecastCropSelect');
  const res = await fetch('http://localhost:8000/api/crops/');
  const crops = await res.json();
  cropSelect.innerHTML = crops.map(crop =>
    `<option value="${crop.id}">${crop.name}</option>`
  ).join('');
  cropSelect.onchange = async function () {
    const cropId = cropSelect.value;
    const resp = await fetch(`http://localhost:8000/api/forecast/crop/${cropId}/`);
    const info = await resp.json();
    document.getElementById('priceForecastResults').innerHTML = `
      <b>Current Price:</b> ${info.current_price}<br>
      <b>Government MSP:</b> ${info.msp}<br>
      <b>Price Trend:</b> ${info.trend}<br>
    `;
    // If you use Chart.js, plot forecast here
  };
  cropSelect.onchange();
};
