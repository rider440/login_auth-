"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { employeeService, taskService } from "@/services/api";
import { ArrowLeft, Loader2, Mail, Phone, User, CheckSquare, Plus, Trash2, Edit } from "lucide-react";

export default function EmployeeProfilePage() {
  const params = useParams();
  const router = useRouter();
  const employeeId = Number(params.id);

  const [employee, setEmployee] = useState<any>(null);
  const [allTasks, setAllTasks] = useState<any[]>([]);
  const [assignedTasks, setAssignedTasks] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState("");

  const fetchData = async () => {
    try {
      setIsLoading(true);
      // Fetch employee details
      const empData = await employeeService.getEmployee(employeeId);
      setEmployee(empData);

      // Fetch all tasks
      const tasksData = await taskService.getTasks();
      setAllTasks(tasksData);

      // To find tasks assigned to this employee, we must check assignments for each task
      // In a real app, there would be a dedicated backend endpoint for this
      const assigned = [];
      for (const task of tasksData) {
        try {
          const assignments = await taskService.getTaskAssignments(task.TaskId);
          if (assignments.some((a: any) => a.emp_id === employeeId)) {
            assigned.push(task);
          }
        } catch (e) {
          // ignore error for individual task assignments
        }
      }
      setAssignedTasks(assigned);

    } catch (err) {
      setError("Failed to load employee data");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (employeeId) {
      fetchData();
    }
  }, [employeeId]);

  const handleAssignTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTaskId) return;

    try {
      await taskService.assignTask({
        task_id: Number(selectedTaskId),
        emp_id: employeeId
      });
      setShowAssignModal(false);
      setSelectedTaskId("");
      fetchData(); // Refresh data
    } catch (err) {
      alert("Failed to assign task. It might already be assigned.");
    }
  };

  const handleUpdateTaskStatus = async (taskId: number, newStatus: string) => {
    try {
      await taskService.updateTask(taskId, { status: newStatus });
      fetchData(); // Refresh data
    } catch (err) {
      alert("Failed to update status");
    }
  };

  const handleUnassignTask = async (taskId: number) => {
    if (!confirm("Are you sure you want to unassign this task?")) return;
    
    try {
      // Find the assignment ID for this task and employee
      const assignments = await taskService.getTaskAssignments(taskId);
      const assignment = assignments.find((a: any) => a.emp_id === employeeId);
      
      if (assignment) {
        await taskService.deleteTaskAssignment(assignment.TaskAssigneeId);
        fetchData();
      }
    } catch (err) {
      alert("Failed to unassign task");
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="animate-spin text-primary" size={48} />
      </div>
    );
  }

  if (error || !employee) {
    return (
      <div className="error-text text-center py-8">{error || "Employee not found"}</div>
    );
  }

  // Filter out tasks that are already assigned so they don't show in the dropdown
  const unassignedTasks = allTasks.filter(
    t => !assignedTasks.some(at => at.TaskId === t.TaskId)
  );

  return (
    <div >
      <div className="page-header">
        <div>
          <button
            onClick={() => router.push('/dashboard/employees')}
            className="action-btn"
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', padding: 0 }}
          >
            <ArrowLeft size={20} /> Back to Employees
          </button>
          <h1 style={{ marginBottom: '0.25rem' }}>Employee Profile</h1>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 2fr)', gap: '2rem' }}>

        {/* Left Column: Profile Info */}
        <div className="glass-card" style={{ maxWidth: '100%', height: 'fit-content' }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <div style={{
              width: '80px', height: '80px', borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--primary), var(--accent))',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'white', fontSize: '2rem', fontWeight: 'bold', margin: '0 auto 1rem'
            }}>
              {employee.EmpName.charAt(0)}
            </div>
            <h2>{employee.EmpName}</h2>
            <span className={`badge ${employee.is_active ? 'badge-active' : 'badge-inactive'}`} style={{ marginTop: '0.5rem', display: 'inline-block' }}>
              {employee.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div className="profile-item">
              <label>Employee ID</label>
              <div className="profile-value">
                <User size={18} className="icon" />
                <span>#{employee.EmpId}</span>
              </div>
            </div>
            <div className="profile-item">
              <label>Email Address</label>
              <div className="profile-value">
                <Mail size={18} className="icon" />
                <span>{employee.Email || "N/A"}</span>
              </div>
            </div>
            <div className="profile-item">
              <label>Phone Number</label>
              <div className="profile-value">
                <Phone size={18} className="icon" />
                <span>{employee.Phone || "N/A"}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Tasks */}
        <div className="glass-card" style={{ maxWidth: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
            <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckSquare size={24} className="text-primary" />
              Assigned Tasks
            </h2>
            <button onClick={() => setShowAssignModal(true)} className="btn-small" style={{ width: 'auto' }}>
              <Plus size={18} /> Assign Task
            </button>
          </div>

          {assignedTasks.length === 0 ? (
            <div className="text-center py-8 text-muted" style={{ background: 'var(--input-bg)', borderRadius: '0.75rem' }}>
              <p>No tasks assigned to this employee yet.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {assignedTasks.map((task) => (
                <div key={task.TaskId} style={{
                  padding: '1.5rem', background: 'var(--input-bg)',
                  borderRadius: '0.75rem', border: '1px solid var(--card-border)'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <h3 style={{ fontSize: '1.1rem' }}>{task.TaskName}</h3>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <select 
                        value={task.status || "Pending"}
                        onChange={(e) => handleUpdateTaskStatus(task.TaskId, e.target.value)}
                        style={{
                          padding: '0.25rem 0.5rem', borderRadius: '0.5rem', fontSize: '0.8rem',
                          background: 'var(--card)', border: '1px solid var(--card-border)', color: 'var(--foreground)'
                        }}
                      >
                        <option value="Pending">Pending</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Completed">Completed</option>
                      </select>
                      <button 
                        onClick={() => handleUnassignTask(task.TaskId)}
                        style={{ padding: '0.25rem', background: 'transparent', boxShadow: 'none', color: '#ef4444', width: 'auto' }}
                        title="Unassign Task"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  <p className="text-muted" style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>{task.description}</p>
                  
                  <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem' }}>
                    <span style={{ padding: '0.25rem 0.75rem', background: 'rgba(79, 70, 229, 0.1)', color: 'var(--primary)', borderRadius: '999px' }}>
                      Priority: {task.priority || "Normal"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Assign Task Modal */}
      {showAssignModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2 style={{ marginBottom: '1.5rem' }}>Assign Task to {employee.EmpName}</h2>
            <form onSubmit={handleAssignTask}>
              <div className="form-group">
                <label>Select Task</label>
                {unassignedTasks.length === 0 ? (
                  <p className="error-text text-muted">No available tasks to assign. Please create more tasks first.</p>
                ) : (
                  <select
                    required
                    value={selectedTaskId}
                    onChange={(e) => setSelectedTaskId(e.target.value)}
                    style={{
                      width: '100%', padding: '0.875rem 1rem', borderRadius: '0.75rem',
                      border: '1px solid var(--card-border)', background: 'var(--input-bg)',
                      color: 'var(--foreground)', fontSize: '1rem'
                    }}
                  >
                    <option value="" disabled>Select a task...</option>
                    {unassignedTasks.map(t => (
                      <option key={t.TaskId} value={t.TaskId}>{t.TaskName}</option>
                    ))}
                  </select>
                )}
              </div>

              <div className="flex" style={{ gap: '1rem', marginTop: '2rem' }}>
                <button
                  type="button"
                  onClick={() => setShowAssignModal(false)}
                  style={{ background: 'transparent', border: '1px solid var(--card-border)', color: 'var(--foreground)', boxShadow: 'none' }}
                >
                  Cancel
                </button>
                <button type="submit" disabled={!selectedTaskId || unassignedTasks.length === 0}>
                  Assign Task
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
