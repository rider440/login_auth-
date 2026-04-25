"use client";

import React, { useState } from "react";
import { User, Phone, MapPin, Building, ArrowRight } from "lucide-react";
import Link from "next/link";
import { authService } from "@/services/api";

export default function RegisterForm() {
  const [formData, setFormData] = useState({
    name: "",
    number: "",
    address: "",
    city: ""
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      // Map 'number' to 'phone' for the backend
      const { number, ...rest } = formData;
      await authService.register({
        ...rest,
        phone: number
      });

      alert("Registration Successful! Please login.");
      window.location.href = "/login";
    } catch (err: any) {
      setError(err.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value;
    if (e.target.id === "number") {
      value = value.replace(/\D/g, "").slice(0, 10);
    }
    setFormData({
      ...formData,
      [e.target.id]: value
    });
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
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Company Name</label>
          <div style={{ position: 'relative' }}>
            <User size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              id="name"
              type="text"
              placeholder="Company Name"
              value={formData.name}
              onChange={handleChange}
              style={{ paddingLeft: '2.75rem' }}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="number">Phone Number</label>
          <div style={{ position: 'relative' }}>
            <Phone size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              id="number"
              type="tel"
              placeholder="1234567890"
              value={formData.number}
              onChange={handleChange}
              maxLength={10}
              style={{ paddingLeft: '2.75rem' }}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="address">Address</label>
          <div style={{ position: 'relative' }}>
            <MapPin size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              id="address"
              type="text"
              placeholder="Street name, area"
              value={formData.address}
              onChange={handleChange}
              style={{ paddingLeft: '2.75rem' }}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="city">City</label>
          <div style={{ position: 'relative' }}>
            <Building size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              id="city"
              type="text"
              placeholder="Your City"
              value={formData.city}
              onChange={handleChange}
              style={{ paddingLeft: '2.75rem' }}
              required
            />
          </div>
        </div>

        <button type="submit" disabled={isLoading || formData.number.length !== 10}>
          {isLoading ? "Creating Account..." : "Register Now"}
          {!isLoading && <ArrowRight size={18} />}
        </button>

        <div className="auth-footer">
          Already have an account? <Link href="/login" className="text-link">Login</Link>
        </div>
      </form>
    </div>
  );
}
