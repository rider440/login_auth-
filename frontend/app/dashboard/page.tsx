"use client";

import React, { useEffect, useState } from "react";
import { authService, taskService, reportService } from "@/services/api";
import { User, Phone, MapPin, Building, Loader2, CheckSquare, History, FileText } from "lucide-react";

interface UserData {
  id: number;
  name: string;
  phone: string;
  address?: string;
  city?: string;
  role: "admin" | "employee";
  company_id: number;
}

export default function DashboardPage() {
  const [user, setUser] = useState<UserData | null>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [recentReports, setRecentReports] = useState<any[]>([]);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const userData = await authService.getCurrentUser();
      setUser(userData);

      const [taskData, reportData] = await Promise.all([
        userData.role === "employee" ? taskService.getTasks() : Promise.resolve([]),
        reportService.getReports()
      ]);
      
      setTasks(taskData);
      setRecentReports(reportData.slice(0, 5)); // Only show last 5 reports
    } catch (err: any) {
      setError("Failed to load data. Please login again.");
      if (err.response?.status === 401) {
        localStorage.removeItem("token");
        window.location.href = "/login";
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleUpdateStatus = async (taskId: number, newStatus: string) => {
    try {
      await taskService.updateTask(taskId, { status: newStatus });
      fetchData(); // Refresh tasks
    } catch (err) {
      alert("Failed to update status");
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <Loader2 className="animate-spin text-primary" size={48} />
        <p className="mt-4 text-muted">Loading...</p>
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
          <h1 style={{ marginBottom: '0.25rem' }}>{user.role === 'admin' ? 'Admin Dashboard' : 'Employee Dashboard'}</h1>
          <p className="subtitle" style={{ marginBottom: 0 }}>Welcome back, {user.name.split(' ')[0]}!</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem' }}>
        {/* Profile Card */}
        <div className="glass-card" style={{ height: 'fit-content' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem' }}>My Profile</h2>
          <div style={{ display: 'grid', gap: '1.25rem' }}>
            <div className="profile-item">
              <label>{user.role === 'admin' ? 'Company Name' : 'Full Name'}</label>
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

            {user.role === 'admin' && (
              <>
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
              </>
            )}

            <div className="profile-item">
              <label>Company ID</label>
              <div className="profile-value">
                <Building size={20} className="icon" />
                <span>{user.company_id}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Reports & Tasks Container */}
        <div className="flex flex-col gap-8">
          {/* Recent Activity (Reports) */}
          <div className="glass-card" style={{ maxWidth: '100%' }}>
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <History size={24} /> Recent Activity
            </h2>
            {recentReports.length > 0 ? (
              <div className="history-list">
                {recentReports.map((report: any) => (
                  <div key={report.ReportId} className="history-item">
                    <div className="flex justify-between items-start">
                      <div className="flex flex-col">
                        <span className="date">{new Date(report.created_at).toLocaleString()}</span>
                        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--primary)', marginTop: '0.25rem' }}>
                          {report.task_name} {report.project_name ? `(${report.project_name})` : ''}
                        </span>
                      </div>
                      <span className={`badge ${report.Status === 'Completed' ? 'badge-active' : 'badge-pending'}`} style={{ fontSize: '0.6rem' }}>
                        {report.Status}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
                      <strong>Update:</strong> {report.UpdateContent}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted">No recent updates logged.</p>
            )}
          </div>

          {/* Employee Task List */}
          {user.role === 'employee' && (
            <div className="glass-card" style={{ maxWidth: '100%' }}>
              <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <CheckSquare size={24} /> My Assigned Tasks
              </h2>
              
              {tasks.length === 0 ? (
                <p className="text-muted">No tasks assigned to you yet.</p>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Task</th>
                        <th>Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tasks.map(task => (
                        <tr key={task.TaskId}>
                          <td style={{ fontWeight: 500 }}>{task.TaskName}</td>
                          <td>
                            <span className={`badge ${task.status === 'Completed' ? 'badge-active' : 'badge-pending'}`}>
                              {task.status}
                            </span>
                          </td>
                          <td>
                            <button className="btn-small" onClick={() => window.location.href = "/dashboard/tasks"}>
                               <FileText size={16} /> View
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
