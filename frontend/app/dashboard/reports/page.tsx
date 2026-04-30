"use client";

import React, { useState, useEffect } from "react";
import { reportService, authService } from "@/services/api";
import { Loader2, FileText, Calendar, User, Briefcase, Users, LayoutGrid } from "lucide-react";

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [userRole, setUserRole] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [reportData, userData] = await Promise.all([
        reportService.getReports(),
        authService.getCurrentUser()
      ]);
      setReports(reportData);
      setUserRole(userData.role);
    } catch (err) {
      setError("Failed to load reports");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <LayoutGrid size={32} className="text-primary" /> Daily Progress Reports
          </h1>
          <p className="subtitle">Detailed activity logs across all projects and teams</p>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="animate-spin text-primary" size={48} />
        </div>
      ) : error ? (
        <div className="glass-card text-center py-10">
          <p className="text-error">{error}</p>
          <button className="mt-4" onClick={fetchData}>Retry</button>
        </div>
      ) : (
        <div className="glass-card" style={{ maxWidth: '100%' }}>
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date & Time</th>
                  <th>Task Name</th>
                  <th>Project</th>
                  <th>Team</th>
                  {userRole === 'admin' && <th>Employee</th>}
                  <th>Update Description</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {reports.length > 0 ? (
                  reports.map((report) => (
                    <tr key={report.ReportId}>
                      <td style={{ whiteSpace: 'nowrap', fontSize: '0.85rem' }}>
                        <div className="flex items-center gap-2">
                          <Calendar size={14} className="text-muted" />
                          {new Date(report.created_at).toLocaleString()}
                        </div>
                      </td>
                      <td style={{ fontWeight: 600 }}>
                        <div className="flex items-center gap-2">
                          <FileText size={16} className="text-primary" />
                          {report.task_name || "Unknown Task"}
                        </div>
                      </td>
                      <td>
                        <div className="flex items-center gap-2">
                          <Briefcase size={14} className="text-muted" />
                          {report.project_name || "N/A"}
                        </div>
                      </td>
                      <td>
                        <div className="flex items-center gap-2">
                          <Users size={14} className="text-muted" />
                          {report.team_name || "N/A"}
                        </div>
                      </td>
                      {userRole === 'admin' && (
                        <td style={{ fontWeight: 500 }}>
                          <div className="flex items-center gap-2">
                            <User size={14} className="text-muted" />
                            {report.employee_name || "Unknown"}
                          </div>
                        </td>
                      )}
                      <td style={{ minWidth: '200px', fontSize: '0.9rem' }}>
                        {report.UpdateContent}
                      </td>
                      <td>
                        <span className={`badge ${report.Status === 'Completed' ? 'badge-active' : 'badge-pending'}`}>
                          {report.Status}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={userRole === 'admin' ? 7 : 6} className="text-center py-10 text-muted">
                      No reports found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
