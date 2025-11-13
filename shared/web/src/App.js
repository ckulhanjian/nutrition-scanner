// Import React (optional in newer React versions, but good practice)
import React from 'react';
// Import BrowserRouter from react-router-dom
import { BrowserRouter } from 'react-router-dom';
// Import your NutritionScanner component
import NutritionScanner from './components/NutritionScanner.jsx'; // adjust the path if it's in a different folder
import Original from './components/original.jsx';

function App() {
  return (
    <BrowserRouter>
      <div>
        {/* <NutritionScanner /> */}
        <Original />
      </div>
    </BrowserRouter>
  );
}

export default App;