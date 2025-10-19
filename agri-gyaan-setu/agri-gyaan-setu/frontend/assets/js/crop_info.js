window.onload = async function() {
  const cropSelect = document.getElementById('cropSelect');
  const res = await fetch('http://localhost:8000/api/crops/');
  const crops = await res.json();
  cropSelect.innerHTML = crops.map(crop =>
    `<option value="${crop.id}">${crop.name}</option>`
  ).join('');
  cropSelect.onchange = async function() {
    const cropId = cropSelect.value;
    const resp = await fetch(`http://localhost:8000/api/crops/${cropId}/info/`);
    const info = await resp.json();
    document.getElementById('cropDetails').innerHTML = `
      <b>Cost & Investment:</b> ${info.cost}<br>
      <b>Market Price:</b> ${info.price}<br>
      <b>MSP:</b> ${info.msp}<br>
      <b>Yield:</b> ${info.yield}<br>
      <b>Best Uses:</b> <ul>${info.uses.map(u => `<li>${u}</li>`).join('')}</ul>
    `;
  };
  cropSelect.onchange();
};
