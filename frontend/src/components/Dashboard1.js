import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import io from "socket.io-client";  
import "./styles/Dashboard.css";
import useWatchlist from "./Watchlist";

const socket = io.connect('http://localhost:5000', {
  transports: ['websocket']
});

socket.on("connect", () => {
  console.log("Connected to WebSocket server");
});

socket.on("disconnect", () => {
  console.log("Disconnected from WebSocket server");
});

socket.on("price_update", (data) => {
  console.log("Price update received:", data);
});

const Dashboard1 = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");
  const [symbol, setSymbol] = useState(""); 
  const [watchlist, setWatchlist] = useState([]);
  const [searchResult, setSearchResult] = useState(null);
  const [searchError, setSearchError] = useState("");

  const handleAddStock = async (symbol) => {
    try {
      console.log("Symbol:", symbol);
      if (!symbol || symbol.trim() === "") {
        setSearchError("Symbol is required.");
        return;
      }

      if (!token) {
        setSearchError("User authentication required.");
        return;
      }

      console.log("Token:", token);
      const response = await axios.post(
        "http://localhost:5000/watchlist/add",
        { symbol },
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        }
      );

      console.log("Response:", response);

      if (response.status === 201) {
        setWatchlist((prevWatchlist) => [
          ...prevWatchlist,
          { symbol },
        ]);
        setSearchResult(null);
      }

    } catch (error) {
      console.error("Error adding stock:", error);
      if (error.response) {
        if (error.response.status === 404) {
          setSearchError("Stock not found");
        } else if (error.response.status === 400) {
          setSearchError("Stock already in watchlist");
        } else if (error.response.status === 422) {
          setSearchError("Unprocessable entity - check symbol format");
        } else {
          setSearchError("Error adding stock to watchlist");
        }
      } else {
        setSearchError("Network error");
      }
    }
  };

  useEffect(() => {
    const fetchWatchlist = async () => {
      try {
        const response = await axios.get("http://localhost:5000/watchlist", {
          headers: { Authorization: `Bearer ${token}` },
        });
        setWatchlist(response.data); 
      } catch (err) {
        console.error("Error fetching watchlist:", err);
      }
    };

    if (token) fetchWatchlist(); 
  }, [token]);

  const [allStocks, setAllStocks] = useState([]);

  useEffect(() => {
    const fetchAllStocks = async () => {
      try {
        const response = await axios.get("http://localhost:5000/stocks");
        setAllStocks(response.data);
      } catch (error) {
        console.error("Error fetching all stocks", error);
      }
    };

    fetchAllStocks();
  }, []);

  return (
    <div className="dashboard-layout">
      <div className="sidebar">
        <ul className="sidebar-menu">
          <li><Link to="/dashboard1">Dashboard</Link></li>
          <li><Link to="/watchlist">Watchlist</Link></li>
        </ul>
      </div>

      <div className="main-content">
        <div className="header">
          <h1>Stock Dashboard</h1>
          <button className="logout-btn" onClick={() => {
            localStorage.removeItem("token");
            navigate("/login");
          }}>Logout</button>
        </div>

        <div className="dashboard-container">
          <div className="stock-table">
            <h2>📊 All Available Stocks</h2>
            {allStocks.length > 0 ? (
              <div className="table-container">
                <table className="styled-table">
                  <thead>
                    <tr>
                      <th>📌 Symbol</th>
                      <th>📈 Name</th>
                      <th>💲 Price</th>
                      <th>🔄 Change</th>
                      <th>➕ Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allStocks.map((stock) => (
                      <tr key={stock.symbol}>
                        <td>{stock.symbol}</td>
                        <td>{stock.name}</td>
                        <td className="price-column">${stock.price.toFixed(2)}</td>
                        <td style={{ color: stock.change >= 0 ? "green" : "red" }}>
                          {stock.change.toFixed(2)}
                        </td>
                        <td>
                          <button
                            className={`add-btn ${watchlist.some(item => item.symbol === stock.symbol) ? "added" : ""}`}
                            onClick={() => handleAddStock(stock.symbol)}
                            disabled={watchlist.some(item => item.symbol === stock.symbol)} 
                          >
                            {watchlist.some(item => item.symbol === stock.symbol) ? "Added" : "Add Stock"}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>No stocks available.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard1;
