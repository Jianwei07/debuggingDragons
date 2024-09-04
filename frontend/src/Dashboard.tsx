// src/components/Dashboard.tsx
import React, { useState } from "react";
import axios from "axios";

const Dashboard: React.FC = () => {
  const [prData, setPrData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  // Function to fetch data from Flask backend
  const fetchData = async () => {
    setLoading(true); // Set loading state to true when fetching data
    try {
      const response = await axios.get("http://localhost:5000/summary"); // Update URL if different
      setPrData(response.data);
      setError(null); // Clear any previous errors
    } catch (err) {
      setError("Error fetching data from backend.");
      console.error(err);
    } finally {
      setLoading(false); // Set loading state back to false after fetching data
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Code Review Dashboard</h1>
      <button
        className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        onClick={fetchData} // Call the fetchData function when the button is clicked
      >
        Fetch Latest PR Review
      </button>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {prData && (
        <div>
          <h2>Latest Pull Request Review:</h2>
          <pre>{JSON.stringify(prData, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
