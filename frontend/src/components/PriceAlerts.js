import React, { useState } from "react";
import axios from "axios";

const PriceAlerts = ({ watchlist }) => {
  const [alertData, setAlertData] = useState({ symbol: "", price: "" });

  const handleSetAlert = async () => {
    try {
      await axios.post("http://localhost:5000/api/alerts", alertData, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      alert("✅ Alert Set Successfully!");
    } catch (error) {
      console.error("Error setting alert", error);
    }
  };

  return (
    <div className="alerts-container">
      <h3>Set Price Alert</h3>
      <select
        onChange={(e) => setAlertData({ ...alertData, symbol: e.target.value })}
      >
        <option value="">Select Stock</option>
        {watchlist.map((stock) => (
          <option key={stock.symbol} value={stock.symbol}>
            {stock.symbol}
          </option>
        ))}
      </select>
      <input
        type="number"
        placeholder="Target Price"
        onChange={(e) => setAlertData({ ...alertData, price: e.target.value })}
      />
      <button onClick={handleSetAlert}>🔔 Set Alert</button>
    </div>
  );
};

export default PriceAlerts;
