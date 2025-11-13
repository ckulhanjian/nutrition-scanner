import React, { useState, useRef } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';

import HomeView from './Home';
import LoadingView from './Loading';
import ResultsView from './Results';
// import { FILTER_ICONS, API_BASE } from './constants'; // adjust path as needed

function NutritionScanner() {
  const navigate = useNavigate();

  // State management
  const [selectedFile, setSelectedFile] = useState(null);
  const [ingredients, setIngredients] = useState([]);
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

  // --- Handlers ---

  const handleReset = () => {
    // Reset all states and navigate home
    setSelectedFile(null);
    setIngredients([]);
    setJobId(null);
    setResults(null);
    setFailing(null);
    setStatus(null);
    setImagePreview(null);
    setUploadingIngredients(false);
    setFilters(prevFilters => prevFilters.map(f => ({ ...f, checked: false })));
    navigate('/');
  };

  const handleUploadFile = () => {
    fileInputRef.current.click();
  }

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUploadSubmit = async () => {
    if (!selectedFile) {
      alert("Please select a file first!");
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    setUploadingIngredients(true);

    try {
      const uploadResponse = await fetch("http://127.0.0.1:5002/api/upload", {
        method: 'POST',
        body: formData,
      });

      if (!uploadResponse.ok) {
         throw new Error(`Upload failed with status: ${uploadResponse.status}`);
      }

      const { job_id, ingredients } = await uploadResponse.json();

      setIngredients(ingredients || []);
      setJobId(job_id);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Error uploading file. Please try again.');
      setIngredients([]);
    } finally {
      setUploadingIngredients(false);
    }
  };

  const handleFilterToggle = (id) => {
    setFilters(prevFilters =>
      prevFilters.map(filter =>
        filter.id === id
          ? { ...filter, checked: !filter.checked }
          : filter
      )
    );
  };

  const analyzeIngredients = async () => {
    if (ingredients.length === 0) {
      alert("No ingredients to analyze.");
      return;
    }

    const selectedFilters = filters
      .filter(f => f.checked)
      .map(f => f.name);

    if (selectedFilters.length === 0) {
      alert("Please select at least one filter.");
      return;
    }

    // 1. Initiate Loading Screen using React Router
    navigate('/loading');

    try {
      // 2. Start Analysis Job
      const response = await fetch("http://127.0.0.1:5002/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_id: jobId,
          ingredients: ingredients,
          filters: selectedFilters
        })
      });

      if (!response.ok) {
         throw new Error("Failed to start analysis job.");
      }

      // 3. Start Polling
      setStatus("pending");

      const interval = setInterval(async () => {
        try {
          const statusResponse = await fetch(`http://127.0.0.1:5002/api/status/${jobId}`);
          const statusData = await statusResponse.json();

          if (statusData.status === "complete") {
            setStatus("complete");
            clearInterval(interval); // stop polling

            // 4. Fetch final results
            const resultsResponse = await fetch(`http://127.0.0.1:5002/api/results/${jobId}`);
            const resultsData = await resultsResponse.json();

            setResults(resultsData['results'] || {});
            setFailing(resultsData['failing'] || []);

            // 5. Transition to Results View using React Router
            navigate('/results');
          }
        } catch (err) {
          console.error("Polling error:", err);
          setStatus("error");
          clearInterval(interval);
          navigate('/'); // Navigate back home on error
          alert("An error occurred during analysis polling.");
        }
      }, 2000); // poll every 2 seconds

    } catch (error) {
      console.error('Error initiating analysis:', error);
      alert('Error initiating analysis. Please try again.');
      navigate('/'); // Go back home on initiation failure
    }
  }

  // Define props to pass to each routed component
  const sharedProps = { filters, handleFilterToggle, handleReset };
  const homeViewProps = { ...sharedProps, fileInputRef, selectedFile, handleFileChange, handleUploadFile, handleUploadSubmit, uploadingIngredients, imagePreview, ingredients, hasSelectedFilters, analyzeIngredients };
  const loadingViewProps = { status };
  const resultsViewProps = { ...sharedProps, results, failing };


  // 6. Define Routes
  return (
    <main>
      <Routes>
        <Route path="/" element={<HomeView {...homeViewProps} />} />
        <Route path="/loading" element={<LoadingView {...loadingViewProps} />} />
        <Route path="/results" element={<ResultsView {...resultsViewProps} />} />
        {/* Fallback route */}
        <Route path="*" element={
          <div>
            <h2>404 - Page Not Found</h2>
            <p>The page you are looking for does not exist.</p>
            <button onClick={() => navigate('/')}>Go Home</button>
          </div>
        } />
      </Routes>
    </main>
  );
}

export default NutritionScanner;