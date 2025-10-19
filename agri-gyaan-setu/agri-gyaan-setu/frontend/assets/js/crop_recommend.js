document.getElementById('recommendForm').onsubmit = async function(e) {
  e.preventDefault();
  const token = localStorage.getItem('token');
  const body = {
    location: document.getElementById('location').value,
    soil_type: document.getElementById('soilType').value,
    soil_ph: document.getElementById('soilPH').value,
    land_size: document.getElementById('landSize').value,
    test_crop: document.getElementById('testCrop').value,
  };
  const res = await fetch('http://localhost:8000/api/recommendation/', {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(body)
  });
  if (res.ok) {
    const list = await res.json();
    document.getElementById('recommendResults').innerHTML =
      list.map(r => `<div>
        <b>${r.crop}</b> - Match: ${r.match_percent}%, Profit: ${r.profit_potential}<br>
        Price: ${r.price}, Season: ${r.season}
      </div>`).join('<hr>');
  } else {
    alert('Recommendation failed');
  }
};
