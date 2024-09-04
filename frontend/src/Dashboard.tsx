// src/components/Dashboard.tsx
import React, { useEffect, useState } from "react";
import axios from "axios";

const Dashboard: React.FC = () => {
  const [prData, setPrData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Function to fetch data from Flask backend
  const fetchData = async () => {
    try {
      const response = await axios.get("http://localhost:5000/summary"); // Update URL if different
      setPrData(response.data);
    } catch (err) {
      setError("Error fetching data from backend.");
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Code Review Dashboard</h1>
      {error && <p className="text-red-500">{error}</p>}
      {prData ? (
        <div>
          <h2>Latest Pull Request Review:</h2>
          <pre>{JSON.stringify(prData, null, 2)}</pre>
        </div>
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );
};

export default Dashboard;
