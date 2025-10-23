import axios from 'axios';
import { useState } from 'react';

function CropForm() {
  const [crop, setCrop] = useState('');
  const [form, setForm] = useState({
    N: '', P: '', K: '', temperature: '', humidity: '', ph: '', rainfall: ''
  });

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = e => {
    e.preventDefault();
    // Only send the features your model expects, in the correct order!
    axios.post('http://127.0.0.1:8000/api/recommend/', {
      features: [
        Number(form.ph),
        Number(form.N),
        Number(form.P),
        Number(form.K)
      ]
    })
    .then(res => setCrop(res.data.recommended_crop))
    .catch(err => console.log(err));
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="N" value={form.N} onChange={handleChange} placeholder="N" />
      <input name="P" value={form.P} onChange={handleChange} placeholder="P" />
      <input name="K" value={form.K} onChange={handleChange} placeholder="K" />
      <input name="ph" value={form.ph} onChange={handleChange} placeholder="ph" />
      <button type="submit">Recommend Crop</button>
      {crop && <div>Recommended Crop: {crop}</div>}
    </form>
  );
}

export default CropForm;
