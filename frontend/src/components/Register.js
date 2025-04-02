import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./styles/Register.css"; 

const Register = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isRobot, setIsRobot] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" });
  const navigate = useNavigate();

  function isValidPassword(password) {
    var passwordRegex = /^(?=.*\d)(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
    return passwordRegex.test(password);
  }

  const sendOTP = async () => {
    if (!email || !password || !confirmPassword) {
      setMessage({ text: "⚠️ All fields are required!", type: "error" });
      return;
    }

    if (!isValidPassword(password)) {
      setMessage({
        text: "❌ Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character (!@#$%^&*).",
        type: "error",
      });
      return;
    }

    if (password !== confirmPassword) {
      setMessage({ text: "❌ Passwords do not match!", type: "error" });
      return;
    }

    if (!isRobot) {
      setMessage({ text: "⚠️ Please confirm that you are not a robot!", type: "error" });
      return;
    }

    try {
      const response = await axios.post("http://localhost:5000/register", {
        email_id: email,
        password: password,
      });
      setMessage({ text: "✅ " + response.data.message, type: "success" });
      navigate("/verify-otp", { state: { email, password } });
    } catch (error) {
      setMessage({
        text: "❌ Error: " + (error.response?.data?.error || "Registration failed"),
        type: "error",
      });
    }
  };

  return (
    <div className="register-container">
      <div className="register-box">
        <h2>SIGN UP</h2>
        <input
          type="email"
          placeholder="Email ID"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
        />
        <label className="robot-checkbox">
          <input
            type="checkbox"
            checked={isRobot}
            onChange={() => setIsRobot(!isRobot)}
          />
          <span className="checkmark"></span> I am not a robot
        </label>
        <button onClick={sendOTP} className="register-btn">
          Submit
        </button>
        {message.text && <p className={`message ${message.type}`}>{message.text}</p>}

        <p className="login-link">
          Already have an account?{" "}
          <span onClick={() => navigate("/login")}>Login</span>
        </p>
      </div>
    </div>
  );
};

export default Register;
