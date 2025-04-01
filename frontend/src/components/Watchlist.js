import React, { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar"; // Import Sidebar
import Header from "./Header";
import "./styles/Dashboard.css"; // Import styles

export const useWatchlist = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const [watchlist, setWatchlist] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWatchlist = async () => {
      try {
        const response = await axios.get("http://localhost:5000/watchlist", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setWatchlist(response.data); // Set the watchlist with data from the API
      } catch (err) {
        setError("Error fetching watchlist");
        if (err.response?.status === 401) {
          navigate("/login");
        }
      }
    };

    if (token) fetchWatchlist(); // Fetch watchlist if a token exists
  }, [token, navigate]);

  // Function to handle deleting a stock from the watchlist
  const handleDeleteStock = async (symbol) => {
    try {
      await axios.post(
        "http://localhost:5000/watchlist/remove",
        { symbol },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setWatchlist(watchlist.filter((stock) => stock.symbol !== symbol)); // Update the state after deletion
    } catch (error) {
      setError("Error removing stock from watchlist");
    }
  };

  return (
    <div className="dashboard-layout">
      <Sidebar /> {/* Include Sidebar */}
      <div className="main-content">
        <Header /> {/* Include Header */}
        <div className="dashboard-container">
          <div className="stock-table">
            <h1>Your Watchlist</h1>
            {error && <div className="error">{error}</div>} {/* Display error message */}
            {watchlist.length > 0 ? (
              <div className="table-container">
                <table className="styled-table">
                  <thead>
                    <tr>
                      <th>📌 Symbol</th>
                      <th>📈 Name</th>
                      <th>💲 Price</th>
                      <th>🔄 Change</th>
                      <th>❌ Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {watchlist.map((stock) => (
                      <tr key={stock.symbol}>
                        <td>{stock.symbol}</td>
                        <td>{stock.name}</td>
                        <td className="price-column">${stock.price.toFixed(2)}</td>
                        <td style={{ color: stock.change >= 0 ? "green" : "red" }}>
                          {stock.change.toFixed(2)}
                        </td>
                        <td>
                          <button className="add-btn" onClick={() => handleDeleteStock(stock.symbol)}>
                           Remove
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>Your watchlist is empty.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default useWatchlist;
