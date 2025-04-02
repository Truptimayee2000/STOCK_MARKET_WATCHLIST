import React from "react";
import { Link } from "react-router-dom";

const Sidebar = () => {
  return (
    <div className="sidebar">
      <ul className="sidebar-menu">
        <li><Link to="/dashboard1">Dashboard</Link></li>
        <li><Link to="/watchlist">Watchlist</Link></li>
      </ul>
    </div>
  );
};

export default Sidebar;
