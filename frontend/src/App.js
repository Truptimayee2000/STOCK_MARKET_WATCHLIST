import React from "react";
import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import Register from "./components/Register";
import VerifyOTP from "./components/VerifyOTP";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard1";
import Watchlist from "./components/Watchlist";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />  
        <Route path="/register" element={<Register />} />
        <Route path="/verify-otp" element={<VerifyOTP />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard1" element={<Dashboard />} />
        <Route path="/watchlist" element={<Watchlist />} />
      </Routes>
    </Router>
  );
}

export default App;
