(async function () {
  const token = localStorage.getItem('token');
  const res = await fetch('http://localhost:8000/api/farmer/me/', {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (res.ok) {
    const farmer = await res.json();
    document.getElementById('welcome').innerText = `Welcome, ${farmer.name} (${farmer.language})`;
  }
})();
