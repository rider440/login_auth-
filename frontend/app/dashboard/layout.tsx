"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, CheckSquare, LogOut, Menu, X, Briefcase, Settings, User as UserIcon, ChevronDown, Bell, FileText } from "lucide-react";
import { authService } from "@/services/api";

interface UserData {
  id: number;
  name: string;
  phone: string;
  role: "admin" | "employee";
  company_id: number;
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [user, setUser] = useState<UserData | null>(null);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await authService.getCurrentUser();
        setUser(data);
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
    { name: "Projects", href: "/dashboard/projects", icon: Briefcase },
    { name: "Teams", href: "/dashboard/teams", icon: Users, adminOnly: true },
    { name: "Employees", href: "/dashboard/employees", icon: UserIcon, adminOnly: true },
    { name: "Tasks", href: "/dashboard/tasks", icon: CheckSquare },
    { name: "Reports", href: "/dashboard/reports", icon: FileText },
  ];

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
  };

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${isMobileMenuOpen ? "open" : ""}`}>
        <div className="sidebar-header">
          <div className="logo-text">Employee Task Manager</div>
          <button
            className="mobile-close"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <X size={24} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {menuItems
            .filter(item => !item.adminOnly || user?.role === "admin")
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
                  <Icon size={22} />
                  <span>{item.name}</span>
                </Link>
              );
            })}
        </nav>

        <div className="sidebar-footer">
          <div className="nav-item" style={{ cursor: 'default', opacity: 0.7 }}>
            <Settings size={20} />
            <span>Settings</span>
          </div>
        </div>
      </aside>

      {/* Main Wrapper */}
      <div className="main-wrapper">
        {/* Top Navbar */}
        <header className="top-navbar">
          <div className="flex items-center gap-4">
            <div className="action-btn" style={{ padding: '0.5rem', borderRadius: '50%', background: 'rgba(255,255,255,0.05)' }}>
              <Bell size={20} />
            </div>

            <div className="user-profile-trigger" onClick={() => setIsProfileOpen(!isProfileOpen)}>
              <div className="avatar">
                {user ? getInitials(user.name) : <UserIcon size={20} />}
              </div>
              <div className="hidden-mobile" style={{ textAlign: 'left' }}>
                <span className="name" style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600 }}>{user?.name}</span>
                <span className="role" style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>{user?.role}</span>
              </div>
              <ChevronDown size={16} className={`transition-all ${isProfileOpen ? 'rotate-180' : ''}`} />

              {isProfileOpen && (
                <div className="user-dropdown">
                  <div className="dropdown-header">
                    <span className="name">{user?.name}</span>
                    <span className="role-badge">{user?.role}</span>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{user?.phone}</p>
                  </div>

                  <Link href="/dashboard/profile" className="dropdown-item">
                    <UserIcon size={18} />
                    <span>My Profile</span>
                  </Link>
                  <div className="dropdown-item" onClick={() => alert("Settings coming soon")}>
                    <Settings size={18} />
                    <span>Settings</span>
                  </div>
                  <div className="dropdown-item logout" onClick={handleLogout}>
                    <LogOut size={18} />
                    <span>Logout</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Content Container */}
        <div className="content-container">
          {children}
        </div>
      </div>
    </div>
  );
}
