"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, CheckSquare, LogOut, Menu, X } from "lucide-react";
import { authService } from "@/services/api";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [userRole, setUserRole] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await authService.getCurrentUser();
        setUserRole(data.role);
      } catch (err) {
        // Unauthorized handled in api.ts
      }
    };
    fetchUser();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  const menuItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Employees", href: "/dashboard/employees", icon: Users, adminOnly: true },
    { name: "Tasks", href: "/dashboard/tasks", icon: CheckSquare },
  ];

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${isMobileMenuOpen ? "open" : ""}`}>
        <div className="sidebar-header">
          <div className="logo-text">WorkSpace</div>
          <button
            className="mobile-close"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <X size={24} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {menuItems
            .filter(item => !item.adminOnly || userRole === "admin")
            .map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || (pathname.startsWith(item.href) && item.href !== "/dashboard");

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`nav-item ${isActive ? "active" : ""}`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Icon size={20} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
        </nav>

        <div className="sidebar-footer">
          <button className="nav-item logout-btn" onClick={handleLogout}>
            <LogOut size={20} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-wrapper">
        {/* Mobile Header */}
        <header className="mobile-header">
          <button onClick={() => setIsMobileMenuOpen(true)}>
            <Menu size={24} />
          </button>
          <div className="logo-text" style={{ fontSize: "1.2rem" }}>WorkSpace</div>
        </header>

        {/* Content */}
        <div className="content-container">
          {children}
        </div>
      </div>
    </div>
  );
}
