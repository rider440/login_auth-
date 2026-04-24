"use client";

import React, { useEffect, useState } from "react";
import { authService } from "@/services/api";
import { User, Phone, MapPin, Building, Loader2 } from "lucide-react";

interface UserData {
  name: string;
  phone: string;
  address: string;
  city: string;
}

export default function DashboardPage() {
  const [user, setUser] = useState<UserData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await authService.getCurrentUser();
        setUser(data);
      } catch (err: any) {
        setError("Failed to load user profile. Please login again.");
        // Redirect to login if unauthorized
        if (err.response?.status === 401) {
          localStorage.removeItem("token");
          window.location.href = "/login";
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchUser();
  }, []);


  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <Loader2 className="animate-spin text-primary" size={48} />
        <p className="mt-4 text-muted">Loading your profile...</p>
      </div>
    );
  }

  if (error || !user) {
    return (
      <div className="glass-card text-center">
        <h2 className="text-error mb-4">Error</h2>
        <p className="subtitle">{error || "User data not found."}</p>
        <button onClick={() => window.location.href = "/login"}>Back to Login</button>
      </div>
    );
  }

  return (
    <div >
      <div className="page-header">
        <div>
          <h1 style={{ marginBottom: '0.25rem' }}>Dashboard</h1>
          <p className="subtitle" style={{ marginBottom: 0 }}>Welcome back, {user.name.split(' ')[0]}!</p>
        </div>
      </div>

      <div className="glass-card" style={{ maxWidth: '100%' }}>
        <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>My Profile</h2>
        <div style={{ display: 'grid', gap: '1.25rem' }}>
          <div className="profile-item">
            <label>Full Name</label>
            <div className="profile-value">
              <User size={20} className="icon" />
              <span>{user.name}</span>
            </div>
          </div>

          <div className="profile-item">
            <label>Phone Number</label>
            <div className="profile-value">
              <Phone size={20} className="icon" />
              <span>{user.phone}</span>
            </div>
          </div>

          <div className="profile-item">
            <label>Address</label>
            <div className="profile-value">
              <MapPin size={20} className="icon" />
              <span>{user.address || "Not provided"}</span>
            </div>
          </div>

          <div className="profile-item">
            <label>City</label>
            <div className="profile-value">
              <Building size={20} className="icon" />
              <span>{user.city || "Not provided"}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

  );
}
