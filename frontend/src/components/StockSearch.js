import React, { useState } from "react";
import axios from "axios";

const StockSearch = ({ fetchWatchlist }) => {
  const [query, setQuery] = useState("");

  const handleSearch = async () => {
    try {
      await axios.post("http://localhost:5000/api/watchlist/add", 
        { symbol: query }, 
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }}
      );
      fetchWatchlist(); // Refresh Watchlist
    } catch (error) {
      console.error("Error adding stock", error);
    }
  };

  return (
    <div className="search-container">
      <input
        type="text"
        placeholder="Search Stock Symbol..."
        value={query}
        onChange={(e) => setQuery(e.target.value.toUpperCase())}
      />
      <button onClick={handleSearch}>➕ Add</button>
    </div>
  );
};

export default StockSearch;
