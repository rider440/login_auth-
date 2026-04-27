"use client";

import React, { useState, useRef, useEffect } from "react";
import { Phone, ArrowRight, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { authService } from "@/services/api";

export default function LoginForm() {
  const [phone, setPhone] = useState("");
  const [step, setStep] = useState(1); // 1: Phone, 2: OTP/Code
  const [userType, setUserType] = useState<"admin" | "employee" | "none">("none");
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [loginCode, setLoginCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handlePhoneSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (phone.length !== 10) return;

    setIsLoading(true);
    setError(null);
    
    try {
      const check = await authService.checkPhone(phone);
      if (!check.exists) {
        setError("Phone number not registered. Please register first.");
        return;
      }

      setUserType(check.user_type);
      
      if (check.user_type === "admin") {
        const response = await authService.sendOtp(phone);
        console.log("----------------------------");
        console.log(`🔑 ${response.message}`);
        if (response.otp) {
          console.log(`OTP (Dev Only): ${response.otp}`);
        }
        console.log("----------------------------");
      }
      
      setStep(2);
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleOtpChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;
    
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);

    if (value && index < 5) {
      setTimeout(() => otpRefs.current[index + 1]?.focus(), 10);
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  const handleVerifyAdmin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      const otpString = otp.join("");
      const response = await authService.verifyOtp(phone, otpString);
      localStorage.setItem("token", response.access_token);
      alert("Admin Login Successful!");
      window.location.href = "/dashboard";
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid OTP. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyEmployee = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await authService.employeeLogin(phone, loginCode);
      localStorage.setItem("token", response.access_token);
      alert("Employee Login Successful!");
      window.location.href = "/dashboard";
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid Login Code. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      {error && (
        <div style={{ 
          background: 'rgba(239, 68, 68, 0.1)', 
          color: '#ef4444', 
          padding: '0.75rem', 
          borderRadius: '0.5rem', 
          marginBottom: '1rem',
          fontSize: '0.875rem',
          border: '1px solid rgba(239, 68, 68, 0.2)'
        }}>
          {error}
        </div>
      )}
      {step === 1 ? (
        <form onSubmit={handlePhoneSubmit}>
          <div className="form-group">
            <label htmlFor="phone">Phone Number</label>
            <div style={{ position: 'relative' }}>
              <Phone size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                id="phone"
                type="tel"
                placeholder="Enter your number"
                value={phone}
                onChange={(e) => {
                  const val = e.target.value.replace(/\D/g, "").slice(0, 10);
                  setPhone(val);
                }}
                maxLength={10}
                style={{ paddingLeft: '2.75rem' }}
                required
              />
            </div>
          </div>
          <button type="submit" disabled={isLoading || phone.length !== 10}>
            {isLoading ? "Verifying..." : "Continue"}
            {!isLoading && <ArrowRight size={18} />}
          </button>
        </form>
      ) : userType === "admin" ? (
        <form onSubmit={handleVerifyAdmin}>
          <label className="text-center" style={{ marginBottom: '1rem' }}>Enter Admin OTP</label>
          <div className="otp-container">
            {otp.map((digit, index) => (
              <input
                key={index}
                ref={(el) => { otpRefs.current[index] = el; }}
                type="text"
                className="otp-digit"
                value={digit}
                onChange={(e) => handleOtpChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                maxLength={1}
                required
              />
            ))}
          </div>
          <button type="submit" disabled={isLoading || otp.some(d => !d)}>
            {isLoading ? "Verifying..." : "Verify Admin Login"}
            {!isLoading && <CheckCircle2 size={18} />}
          </button>
          <button 
            type="button" 
            onClick={() => setStep(1)}
            style={{ 
              background: 'transparent', 
              color: 'var(--text-muted)', 
              boxShadow: 'none',
              marginTop: '0.5rem',
              fontSize: '0.875rem'
            }}
          >
            Change Number
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerifyEmployee}>
          <div className="form-group">
            <label htmlFor="loginCode">Enter Employee Login Code</label>
            <div style={{ position: 'relative' }}>
              <input
                id="loginCode"
                type="text"
                placeholder="EmpXXXX"
                value={loginCode}
                onChange={(e) => setLoginCode(e.target.value)}
                required
              />
            </div>
          </div>
          <button type="submit" disabled={isLoading || !loginCode}>
            {isLoading ? "Verifying..." : "Login as Employee"}
            {!isLoading && <CheckCircle2 size={18} />}
          </button>
          <button 
            type="button" 
            onClick={() => setStep(1)}
            style={{ 
              background: 'transparent', 
              color: 'var(--text-muted)', 
              boxShadow: 'none',
              marginTop: '0.5rem',
              fontSize: '0.875rem'
            }}
          >
            Change Number
          </button>
        </form>
      )}

      <div className="auth-footer">
        Don't have an account? <Link href="/register" className="text-link">Register</Link>
      </div>
    </div>
  );
}
