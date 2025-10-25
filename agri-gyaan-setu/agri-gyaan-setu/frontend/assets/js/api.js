(function () {
  const API_BASE = window.location.origin + '/api';

  async function apiGet(path) {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
    return await res.json();
  }

  async function apiPost(path, body) {
    // Attach CSRF token for Django session authentication and send cookies
    function getCookie(name) {
      const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
      return v ? v.pop() : '';
    }
    const csrf = getCookie('csrftoken');
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf },
      body: JSON.stringify(body)
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`POST ${path} failed: ${res.status} ${text}`);
    }
    return await res.json();
  }

  async function getCrops() { return apiGet('/crops/'); }
  async function getCropInfo(cropId) { return apiGet(`/crops/${cropId}/`); }
  async function getForecast(cropId) { return apiGet(`/forecast/${cropId}/`); }
  // recommendCrop accepts either an array of features OR an object { features: [...], farmer_id: 1 }
  async function recommendCrop(payload) {
    if (Array.isArray(payload)) {
      return apiPost('/recommend/', { features: payload });
    }
    // otherwise assume object
    return apiPost('/recommend/', payload);
  }

  // Expose on window for non-module pages
  window.api = {
    getCrops: getCrops,
    getCropInfo: getCropInfo,
    getForecast: getForecast,
    recommendCrop: recommendCrop
  };
})();
