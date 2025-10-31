import '../App.css';

import React, { useState, useRef } from 'react';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [ingredients, setIngredients] = useState([]);
  const [loading, setLoading]= useState(false);
  const [jobId, setJobId] = useState(null);
  const [results, setResults] = useState(null);
  const [failing, setFailing] = useState(null);
  const [status, setStatus] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [uploadingIngredients, setUploadingIngredients] = useState(false);
  const [filters, setFilters] = useState([

  { id: "lactose", name: "Lactose Intolerant", image: "lactose.png", checked: false },

  { id: "vegan", name: "Vegan", image: "vegan.png", checked: false },

  { id: "vegetarian", name: "Vegetarian", image: "vegetarian.png", checked: false },

  { id: "halal", name: "Halal", image: "halal.png", checked: false },

  { id: "lowsugar", name: "Low-Sugar", image: "low-sugar.png", checked: false },

  { id: "glutenfree", name: "Gluten-Free", image: "gluten-free.png", checked: false },

  ]);
  const hasSelectedFilters = filters.some(f => f.checked);
  const fileInputRef = useRef(null);
  const handleUploadFile = () => {
    fileInputRef.current.click();
  }

  // user picks file, we set it and save it
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
    setSelectedFile(file);
    // console.log('File selected:', file.name);
    const reader = new FileReader();
    reader.onloadend = () => {
    setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
    }
  };
  // send image to backend
  const handleUploadSubmit = async () => {
    if (!selectedFile) {
      alert("Please select a file first!");
      return;
    }
    const formData = new FormData();
    formData.append('file', selectedFile);
    setUploadingIngredients(true);
    try {
      const uploadResponse = await fetch('http://127.0.0.1:5002/api/upload', {
      method: 'POST',
      body: formData, // do NOT stringify
    });
    const { job_id, ingredients } = await uploadResponse.json();
    console.log("Backend ingredients value:", ingredients);
    setIngredients(ingredients);
    setJobId(job_id);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file. Please try again.');
    } finally {
      setUploadingIngredients(false);
    }
  };

  // select & deselect filter
  const handleFilterToggle = (id) => {
    setFilters(prevFilters =>
      prevFilters.map(filter => filter.id === id ? { ...filter, checked: !filter.checked } : filter));
  };

  const analyzeIngredients = async () => {
    if (!ingredients) {
      alert("No ingredients to analyze.")
      return;
    }

    const selectedFilters = filters
    .filter(f => f.checked)
    .map(f => f.name);
    if (selectedFilters.length === 0) {
    alert("Please select at least one filter");
    return;
    }

    console.log({selectedFilters})
    // ingredients and filters
    const response = await fetch("http://127.0.0.1:5002/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        job_id: jobId,
        ingredients: ingredients,
        filters: selectedFilters
      })
    });
    const data = await response.json();
    setStatus("pending");
    const interval = setInterval(async () => {
    try {
      const statusResponse = await fetch(`http://127.0.0.1:5002/api/status/${jobId}`);
      const statusData = await statusResponse.json();
      if (statusData.status === "complete") {
        setStatus("complete");
        // Fetch final results
        const resultsResponse = await fetch(`http://127.0.0.1:5002/api/results/${jobId}`);
        const resultsData = await resultsResponse.json();
          setResults(resultsData['results']);
          setFailing(resultsData['failing']);
          clearInterval(interval); // stop polling
      }
    } catch (err) {
      setStatus("error");
      clearInterval(interval);
    }
    }, 2000); // poll every 2 seconds
  }

    return (
    <div className="App">
      <h1>Nutrition Scanner</h1>
      <div className="home">
        <div className="home-left">
          <div className="upload-file">
            <h2>1. Upload Photo</h2>
            <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/*"
            style={{ display: 'none' }}
            />

            {/* select image */}
            <button onClick={handleUploadFile} disabled={uploadingIngredients} className="choose-btn">Select File
            </button>
            {/* upload image & get ingredients */}

            <button onClick={handleUploadSubmit} disabled={!selectedFile || uploadingIngredients} className="submit-btn">
              {uploadingIngredients ? 'Loading...' : 'Get Ingredients'}
            </button>
            <p>Selected File: {selectedFile ? `${selectedFile.name}` : "No file chosen"}</p>
          </div>

          <h2>2. Choose Filters</h2>
          <div className="filters-container">
          {filters.map(filter => (
          <label
          key={filter.id}
          className={`filter-option ${filter.checked ? 'checked' : ''}`}
          >
            
          <input
          type="checkbox"
          checked={filter.checked}
          onChange={() => handleFilterToggle(filter.id)}
          />
          <img src={`/icons/${filter.image}`} alt={filter.name} />
          <span>{filter.name}</span>
          </label>
          ))}
          </div>
        </div>

        {/* right side - image, buttons, ingredients */}
        <div className="home-right">
          <div className='image-label'>
            {selectedFile ? <img src={imagePreview}></img> : <p>Upload an image</p>}
          </div>

          {/* <div className="ingredients">
          {ingredients ? <p>{ingredients}</p> : <p>No ingredients to analyze</p>}
          </div> */}

            <div className="ingredients">
              {uploadingIngredients ? (
              <div style={{ textAlign: 'center' }}>
              <div className="small-spinner"></div>
              <p style={{ marginTop: '10px', color: '#666' }}>Extracting ingredients...</p>
              </div>
              ) : ingredients && ingredients?.length > 0 ? (
              <div style={{ width: '100%' }}>
              <h3 style={{ marginTop: 0, marginBottom: '15px' }}>{ingredients.length} Ingredients Found!</h3>
              </div>
              ) : (
              <p>No ingredients to analyze</p>
              )}
            </div>
          </div>
        </div>
        <button className="analyze-btn" disabled={ingredients.length===0 || !hasSelectedFilters} onClick={analyzeIngredients}>Analyze</button>
        
        <div className="results">
          <h1>Ingredients</h1>
          <div className="ingredients-grid">
            {ingredients.map((ingredient, index) => (
              <div key={index} className="ingredient-item">{ingredient}</div>
            ))}
          </div>
          <h1>Results</h1>
          {results && Object.keys(results).length > 0 ? (
          <ul className="results-list">
            {Object.entries(results).map(([filter, value]) => (
              <li key={filter}>
                {filter}: {value ? "✅ Pass" : "❌ Fail"}
              </li>
            ))}
          </ul>
        ) : (
          <p>No results yet.</p>
        )}

        </div>
    </div>
  );
}

export default App;