document.getElementById('loginForm').onsubmit = async function (e) {
  e.preventDefault();
  const res = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: document.getElementById('email').value,
      password: document.getElementById('password').value
    }),
  });
  if (res.ok) {
    const data = await res.json();
    localStorage.setItem('token', data.token);
    window.location.href = "dashboard.html";
  } else {
    alert('Login failed');
  }
};

window.setLang = function(lang) {
  localStorage.setItem('lang', lang);
  location.reload();
}
