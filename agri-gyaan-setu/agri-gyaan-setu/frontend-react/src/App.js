import './App.css';
import CropForm from './CropForm'; // Import your CropForm component

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Crop Recommendation System</h1>
        <CropForm /> {/* This displays your crop recommendation form */}
      </header>
    </div>
  );
}

export default App;
