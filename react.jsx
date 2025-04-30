// src/App.jsx
import React, { useState } from 'react';

export default function App() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setImage(file);
    setPreview(URL.createObjectURL(file));
    setResult('');
  };

  const handleSubmit = async () => {
    if (!image) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('image', image);

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult(data.result);
    } catch (error) {
      console.error('Error:', error);
      setResult('Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        backgroundImage: "url('https://hips.hearstapps.com/hmg-prod/images/assortment-of-colorful-ripe-tropical-fruits-top-royalty-free-image-1738552076.pjpeg?resize=1200:*')", // put your background in public folder
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        minHeight: '90vh',
      }}
      className="flex flex-col items-center justify-center px-4 py-8 text-white bg-opacity-100 backdrop-blur"
    >
      <h1 className="text-3xl font-bold mb-6 bg-black/50 p-3 rounded">Stale Fruit Detector</h1>

      <input
        type="file"
        accept="image/*"
        onChange={handleImageChange}
        className="mb-4"
      />

      {preview && (
        <img
          src={preview}
          alt="Selected"
          className="w-64 h-64 object-cover rounded shadow-lg mb-4 border-4 border-white"
        />
      )}

      <button
        onClick={handleSubmit}
        disabled={loading}
        className="bg-green-600 hover:bg-green-700 text-white font-semibold px-6 py-2 rounded shadow"
      >
        {loading ? 'Analyzing...' : 'Detect Freshness'}
      </button>

      {result && (
        <div className="mt-6 text-xl font-bold bg-black/60 px-4 py-2 rounded">
          Result: <span className={result === 'fresh' ? 'text-green-400' : 'text-red-400'}>{result}</span>
        </div>
      )}
    </div>
  );
}
