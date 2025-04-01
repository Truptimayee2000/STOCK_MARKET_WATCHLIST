import React, { useState, useEffect } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";
import "./styles/VarifyOTP.css"; // Import CSS for styling

const VerifyOTP = () => {
  const [otp, setOtp] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false); // ⏳ Show loading indicator
  const location = useLocation();
  const navigate = useNavigate();

  // Get email & password from state
  const email = location.state?.email || "";
  const password = location.state?.password || "";

  // Redirect to register if no email is found
  useEffect(() => {
    if (!email) {
      setMessage("⚠️ Email not found. Please register again.");
      setTimeout(() => navigate("/register"), 3000);
    }
  }, [email, navigate]);

  const verifyOTP = async () => {
    if (!otp || otp.length !== 6) {
      setMessage("⚠️ Please enter a valid 6-digit OTP.");
      return;
    }

    setLoading(true); // Show loading

    try {
      const response = await axios.post(
        "http://localhost:5000/verify-otp",
        { email_id: email, otp: otp, password: password },
        { headers: { "Content-Type": "application/json" } }
      );

      setMessage("✅ " + response.data.message);
      setTimeout(() => navigate("/login"), 2000); // Redirect to login
    } catch (error) {
      const errorMsg = error.response?.data?.error || "Something went wrong.";
      setMessage("❌ OTP verification failed: " + errorMsg);
    } finally {
      setLoading(false); // Hide loading
    }
  };

  return (
    <div className="verify-container">
      <div className="verify-box">
        <h2>🔑 Verify OTP</h2>
        <p className="email-text">
          OTP sent to: <strong>{email}</strong>
        </p>
        <input
          type="text"
          placeholder="Enter OTP"
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
          maxLength={6} // Fix: Proper JSX syntax
          required
        />
        <button onClick={verifyOTP} className="verify-btn" disabled={loading}>
          {loading ? "Verifying..." : "Verify"}
        </button>

        {message && <p className="message">{message}</p>}
      </div>
    </div>
  );
};

export default VerifyOTP;
