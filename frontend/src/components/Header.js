import React from "react";
import { useNavigate } from "react-router-dom";

const Header = () => {
  const navigate = useNavigate();
  
  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <div className="header">
      <h1>Stock Dashboard</h1>
      <button className="logout-btn" onClick={handleLogout}>Logout</button>
    </div>
  );
};

export default Header;
