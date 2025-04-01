import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import "./styles/Login.css";
import { FaEnvelope, FaLock } from "react-icons/fa"; 

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState({ text: "", type: "" });
  const navigate = useNavigate();

  const handleLogin = async () => {
    setMessage({ text: "", type: "" }); // Reset message on login attempt
  
    try {
      const response = await axios.post("http://localhost:5000/login", {
        email_id: email,
        password: password,
      });
  
      setMessage({ text: "✅ " + response.data.message, type: "success" });
  
      // Store the JWT token in local storage
      localStorage.setItem("token", response.data.access_token);
  
      // Redirect to the dashboard after a short delay
      setTimeout(() => navigate("/dashboard1"), 2000);
    } catch (error) {
      setMessage({ 
        text: "❌ " + (error.response?.data.error || "Login failed"), 
        type: "error" 
      });
    }
  };
  

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>🔐 Login</h2>

        <div className="input-group">
          <i><FaEnvelope /></i>
          <input
            type="email"
            placeholder="Enter Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="input-group">
          <i><FaLock /></i>
          <input
            type="password"
            placeholder="Enter Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>

        <button onClick={handleLogin} className="login-btn">🚀 Login</button>

        {message.text && <p className={`message ${message.type}`}>{message.text}</p>}

        <div className="extra-links">
          <Link to="/forgot-password">🔗 Forgot Password?</Link>
          <p>
            🆕 New here? <Link to="/register">Create an Account</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
