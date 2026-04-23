"use client";

import React, { useState, useRef, useEffect } from "react";
import { Phone, ArrowRight, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import { authService } from "@/services/api";

export default function LoginForm() {
  const [phone, setPhone] = useState("");
  const [step, setStep] = useState(1); // 1: Phone, 2: OTP
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const otpRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleSendOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (phone.length < 10) return;

    setIsLoading(true);
    setError(null);
    
    try {
      const response = await authService.sendOtp(phone);
      console.log("----------------------------");
      console.log(`🔑 ${response.message}`);
      if (response.otp) {
        console.log(`OTP (Dev Only): ${response.otp}`);
      }
      console.log("----------------------------");
      setStep(2);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to send OTP. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleOtpChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;
    
    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);

    // Focus next input
    if (value && index < 5) {
      otpRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus();
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      const otpString = otp.join("");
      const response = await authService.verifyOtp(phone, otpString);
      
      // Store token
      localStorage.setItem("token", response.access_token);
      
      alert("Login Successful!");
      window.location.href = "/dashboard";
    } catch (err: any) {
      setError(err.response?.data?.detail || "Invalid OTP. Please try again.");
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
        <form onSubmit={handleSendOtp}>
          <div className="form-group">
            <label htmlFor="phone">Phone Number</label>
            <div style={{ position: 'relative' }}>
              <Phone size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                id="phone"
                type="tel"
                placeholder="Enter your number"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                style={{ paddingLeft: '2.75rem' }}
                required
              />
            </div>
          </div>
          <button type="submit" disabled={isLoading || phone.length < 10}>
            {isLoading ? "Sending..." : "Get OTP"}
            {!isLoading && <ArrowRight size={18} />}
          </button>
        </form>
      ) : (
        <form onSubmit={handleVerify}>
          <label className="text-center" style={{ marginBottom: '1rem' }}>Enter Verification Code</label>
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
            {isLoading ? "Verifying..." : "Verify & Login"}
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
