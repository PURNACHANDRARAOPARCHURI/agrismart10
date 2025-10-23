(async function () {
    const token = localStorage.getItem('token');
    const res = await fetch('http://localhost:8000/api/farmer/me/', {
        headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) {
        const farmer = await res.json();
        // Set personalized greeting
        document.getElementById('welcome').innerText = `Welcome, ${farmer.name} (${farmer.language})`;
    }
})();

document.getElementById('logoutBtn').onclick = function() {
    localStorage.removeItem('token');  // Clear auth token
    window.location.href = 'login.html'; // Redirect to login (change filename if needed)
};
