"use client";

import React from "react";

interface AuthCardProps {
  children: React.ReactNode;
  title: string;
  subtitle: string;
}

export default function AuthCard({ children, title, subtitle }: AuthCardProps) {
  return (
    <div className="glass-card">
      <h1>{title}</h1>
      <p className="subtitle">{subtitle}</p>
      {children}
    </div>
  );
}
