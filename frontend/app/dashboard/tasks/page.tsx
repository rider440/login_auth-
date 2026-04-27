"use client";

import React, { useState, useEffect } from "react";
import { taskService, employeeService, authService, projectService, teamService, reportService } from "@/services/api";
import { Loader2, Plus, CheckSquare, Edit, Trash2, Users, Briefcase, FileText, Send, History } from "lucide-react";

export default function TasksPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [teams, setTeams] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  
  // Daily Report Modal
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportTask, setReportTask] = useState<any>(null);
  const [reportContent, setReportContent] = useState("");
  const [reportStatus, setReportStatus] = useState("In Progress");
  const [taskReports, setTaskReports] = useState<any[]>([]);
  const [isLoadingReports, setIsLoadingReports] = useState(false);

  const [formData, setFormData] = useState({
    TaskName: "",
    description: "",
    status: "Pending",
    priority: "Normal",
    project_id: 0,
    team_id: 0
  });
  const [userRole, setUserRole] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [taskData, projData, teamData, userData] = await Promise.all([
        taskService.getTasks(),
        projectService.getProjects(),
        teamService.getTeams(),
        authService.getCurrentUser()
      ]);
      setTasks(taskData);
      setProjects(projData);
      setTeams(teamData);
      setUserRole(userData.role);
    } catch (err) {
      setError("Failed to load data");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const dataToSend = {
      ...formData,
      project_id: formData.project_id || null,
      team_id: formData.team_id || null
    };
    
    try {
      if (editingId) {
        await taskService.updateTask(editingId, dataToSend);
      } else {
        await taskService.createTask(dataToSend);
      }
      handleCloseModal();
      fetchData();
    } catch (err) {
      alert(`Failed to ${editingId ? 'update' : 'create'} task`);
    }
  };

  const fetchTaskReports = async (taskId: number) => {
    try {
      setIsLoadingReports(true);
      const data = await reportService.getReports({ task_id: taskId });
      setTaskReports(data);
    } catch (err) {
      console.error("Failed to fetch reports", err);
    } finally {
      setIsLoadingReports(false);
    }
  };

  const handleOpenReport = (task: any) => {
    setReportTask(task);
    setReportStatus(task.status);
    setTaskReports([]);
    setShowReportModal(true);
    fetchTaskReports(task.TaskId);
  };

  const handleReportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reportTask) return;
    try {
      await reportService.createReport({
        task_id: reportTask.TaskId,
        UpdateContent: reportContent,
        Status: reportStatus
      });
      setShowReportModal(false);
      setReportContent("");
      fetchData();
    } catch (err) {
      alert("Failed to submit report");
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
    setFormData({ TaskName: "", description: "", status: "Pending", priority: "Normal", project_id: 0, team_id: 0 });
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Tasks</h1>
          <p className="subtitle">Project tasks and team assignments</p>
        </div>
        {userRole === 'admin' && (
          <button className="btn-small" onClick={() => setShowModal(true)}>
            <Plus size={20} />
            Add Task
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="animate-spin text-primary" size={48} />
        </div>
      ) : (
        <div className="glass-card" style={{ maxWidth: '100%' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Task</th>
                <th>Project/Team</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map(task => (
                <tr key={task.TaskId}>
                  <td>
                    <div style={{ fontWeight: 600 }}>{task.TaskName}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{task.description}</div>
                  </td>
                  <td>
                    <div className="flex flex-col gap-1">
                      <span style={{ fontSize: '0.85rem' }}>
                        <Briefcase size={14} style={{ display: 'inline', marginRight: '4px' }} />
                        {projects.find(p => p.ProjectId === task.project_id)?.ProjectName || "No Project"}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <Users size={12} style={{ display: 'inline', marginRight: '4px' }} />
                        {teams.find(t => t.TeamId === task.team_id)?.TeamName || "No Team"}
                      </span>
                    </div>
                  </td>
                  <td>
                    <span className={`badge ${task.status === 'Completed' ? 'badge-active' : task.status === 'In Progress' ? 'badge-pending' : ''}`}>
                      {task.status}
                    </span>
                  </td>
                  <td>
                    <span style={{ color: task.priority === 'High' ? 'var(--secondary)' : 'inherit' }}>{task.priority}</span>
                  </td>
                  <td>
                    <div className="flex gap-2">
                      {userRole === 'admin' ? (
                        <>
                          <button className="action-btn" title="Reports History" onClick={() => handleOpenReport(task)}>
                            <History size={18} />
                          </button>
                          <button className="action-btn" onClick={() => {
                            setEditingId(task.TaskId);
                            setFormData({
                              TaskName: task.TaskName,
                              description: task.description || "",
                              status: task.status || "Pending",
                              priority: task.priority || "Normal",
                              project_id: task.project_id || 0,
                              team_id: task.team_id || 0
                            });
                            setShowModal(true);
                          }}>
                            <Edit size={18} />
                          </button>
                          <button className="action-btn text-error" onClick={async () => {
                             if(confirm("Delete task?")) {
                               await taskService.deleteTask(task.TaskId);
                               fetchData();
                             }
                          }}>
                            <Trash2 size={18} />
                          </button>
                        </>
                      ) : (
                        <button className="btn-small" onClick={() => handleOpenReport(task)}>
                          <FileText size={16} />
                          Update
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Task Creation Modal */}
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content glass-card">
            <h2>{editingId ? "Edit Task" : "New Task"}</h2>
            <form onSubmit={handleSubmit} className="mt-4">
              <div className="form-group">
                <label>Task Name</label>
                <input required value={formData.TaskName} onChange={e => setFormData({...formData, TaskName: e.target.value})} />
              </div>
              <div className="form-group">
                <label>Description</label>
                <input value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} />
              </div>
              
              <div className="grid-2 gap-4">
                <div className="form-group">
                  <label>Project</label>
                  <select value={formData.project_id} onChange={e => setFormData({...formData, project_id: parseInt(e.target.value)})}>
                    <option value={0}>No Project</option>
                    {projects.map(p => <option key={p.ProjectId} value={p.ProjectId}>{p.ProjectName}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Team</label>
                  <select value={formData.team_id} onChange={e => setFormData({...formData, team_id: parseInt(e.target.value)})}>
                    <option value={0}>No Team</option>
                    {teams.map(t => <option key={t.TeamId} value={t.TeamId}>{t.TeamName}</option>)}
                  </select>
                </div>
              </div>

              <div className="grid-2 gap-4">
                <div className="form-group">
                  <label>Status</label>
                  <select value={formData.status} onChange={e => setFormData({...formData, status: e.target.value})}>
                    <option value="Pending">Pending</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Priority</label>
                  <select value={formData.priority} onChange={e => setFormData({...formData, priority: e.target.value})}>
                    <option value="Low">Low</option>
                    <option value="Normal">Normal</option>
                    <option value="High">High</option>
                  </select>
                </div>
              </div>

              <div className="flex gap-4 mt-6">
                <button type="button" onClick={handleCloseModal} style={{ background: 'rgba(0,0,0,0.1)', color: 'var(--foreground)' }}>Cancel</button>
                <button type="submit">Save Task</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Daily Report Modal (also shows history) */}
      {showReportModal && (
        <div className="modal-overlay">
          <div className="modal-content glass-card" style={{ maxWidth: '600px' }}>
            <h2>Task Reports & History</h2>
            <p className="subtitle">Activity for: {reportTask?.TaskName}</p>
            
            {userRole === 'employee' && (
              <form onSubmit={handleReportSubmit} className="mt-4 pb-6" style={{ borderBottom: '1px solid var(--card-border)', marginBottom: '1.5rem' }}>
                <div className="form-group">
                  <label>Current Status</label>
                  <select value={reportStatus} onChange={e => setReportStatus(e.target.value)}>
                    <option value="Pending">Pending</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>What did you do today?</label>
                  <textarea 
                    required
                    rows={3}
                    value={reportContent}
                    onChange={e => setReportContent(e.target.value)}
                    style={{ width: '100%', padding: '1rem', borderRadius: '0.75rem', background: 'var(--input-bg)', border: '1px solid var(--card-border)', color: 'inherit' }}
                    placeholder="Describe your progress..."
                  />
                </div>
                <button type="submit" className="btn-small"><Send size={18} /> Submit Update</button>
              </form>
            )}

            <div className="history-section mt-4">
              <h3 style={{ fontSize: '1rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <History size={18} /> Update History
              </h3>
              
              {isLoadingReports ? (
                <div className="flex justify-center py-4">
                  <Loader2 className="animate-spin text-primary" size={24} />
                </div>
              ) : taskReports.length > 0 ? (
                <div className="history-list" style={{ maxHeight: '300px', overflowY: 'auto', paddingRight: '0.5rem' }}>
                  {taskReports.map((report: any) => (
                    <div key={report.ReportId} className="history-item">
                      <div className="flex justify-between items-start">
                        <span className="date">{new Date(report.created_at).toLocaleString()}</span>
                        <span className={`badge ${report.Status === 'Completed' ? 'badge-active' : 'badge-pending'}`} style={{ fontSize: '0.6rem' }}>
                          {report.Status}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>{report.UpdateContent}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-6 text-muted">
                  No updates found for this task.
                </div>
              )}
            </div>

            <div className="mt-6 flex justify-end">
              <button className="btn-small" onClick={() => setShowReportModal(false)} style={{ background: 'rgba(0,0,0,0.1)', color: 'var(--foreground)' }}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
