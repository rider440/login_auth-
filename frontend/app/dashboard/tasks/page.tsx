"use client";

import React, { useEffect, useState } from "react";
import { taskService, employeeService, authService } from "@/services/api";
import { Loader2, Plus, CheckSquare, Edit, Trash2, Users } from "lucide-react";

export default function TasksPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [assignTaskId, setAssignTaskId] = useState<number | null>(null);
  const [employees, setEmployees] = useState<any[]>([]);
  const [selectedEmpIds, setSelectedEmpIds] = useState<number[]>([]);
  const [isAssigning, setIsAssigning] = useState(false);

  const [formData, setFormData] = useState({
    TaskName: "",
    description: "",
    status: "Pending",
    priority: "Normal",
  });
  const [userRole, setUserRole] = useState<string | null>(null);

  const fetchUser = async () => {
    try {
      const data = await authService.getCurrentUser();
      setUserRole(data.role);
    } catch (err) { }
  };

  const fetchTasks = async () => {
    try {
      setIsLoading(true);
      const data = await taskService.getTasks();
      setTasks(data);
    } catch (err) {
      setError("Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  };

  const fetchEmployees = async () => {
    try {
      const data = await employeeService.getEmployees();
      setEmployees(data);
    } catch (err) {
      console.error("Failed to load employees");
    }
  };

  useEffect(() => {
    fetchTasks();
    fetchEmployees();
    fetchUser();
  }, []);

  const handleUpdateStatus = async (taskId: number, newStatus: string) => {
    try {
      await taskService.updateTask(taskId, { status: newStatus });
      fetchTasks();
    } catch (err) {
      alert("Failed to update status");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await taskService.updateTask(editingId, formData);
      } else {
        await taskService.createTask(formData);
      }
      handleCloseModal();
      fetchTasks();
    } catch (err) {
      alert(`Failed to ${editingId ? 'update' : 'create'} task`);
    }
  };

  const handleEdit = (task: any) => {
    setEditingId(task.TaskId);
    setFormData({
      TaskName: task.TaskName,
      description: task.description || "",
      status: task.status || "Pending",
      priority: task.priority || "Normal",
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this task?")) {
      try {
        await taskService.deleteTask(id);
        fetchTasks();
      } catch (err) {
        alert("Failed to delete task");
      }
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
    setFormData({ TaskName: "", description: "", status: "Pending", priority: "Normal" });
  };

  const handleOpenAssignModal = async (task: any) => {
    setAssignTaskId(task.TaskId);
    try {
      const assignments = await taskService.getTaskAssignments(task.TaskId);
      setSelectedEmpIds(assignments.map((a: any) => a.emp_id));
      setShowAssignModal(true);
    } catch (err) {
      alert("Failed to load assignments");
    }
  };

  const handleAssignSubmit = async () => {
    if (!assignTaskId) return;
    try {
      setIsAssigning(true);
      await taskService.bulkAssignTask({
        task_id: assignTaskId,
        emp_ids: selectedEmpIds
      });
      setShowAssignModal(false);
      setAssignTaskId(null);
      setSelectedEmpIds([]);
    } catch (err) {
      alert("Failed to assign employees");
    } finally {
      setIsAssigning(false);
    }
  };

  const toggleEmployeeSelection = (empId: number) => {
    setSelectedEmpIds(prev =>
      prev.includes(empId)
        ? prev.filter(id => id !== empId)
        : [...prev, empId]
    );
  };

  return (
    <div >
      <div className="page-header">
        <div>
          <h1 style={{ marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckSquare size={28} /> Tasks
          </h1>
          <p className="subtitle" style={{ marginBottom: 0 }}>Manage your company's tasks</p>
        </div>
        {userRole === 'admin' && (
          <button onClick={() => setShowModal(true)} style={{ width: 'auto', padding: '0.75rem 1.5rem' }}>
            <Plus size={20} />
            Create Task
          </button>
        )}
      </div>

      <div className="glass-card" style={{ maxWidth: '100%', padding: '1.5rem' }}>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="animate-spin text-primary" size={32} />
          </div>
        ) : error ? (
          <div className="error-text text-center py-4">{error}</div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-8 text-muted">
            <p>No tasks found. Create one to get started!</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Task Name</th>
                  <th>Description</th>
                  <th>Status</th>
                  <th>Priority</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map((task) => (
                  <tr key={task.TaskId}>
                    <td>#{task.TaskId}</td>
                    <td style={{ fontWeight: 500 }}>{task.TaskName}</td>
                    <td style={{ maxWidth: '250px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {task.description}
                    </td>
                    <td>
                      <span className={`badge ${task.status === 'Completed' ? 'badge-active' :
                        task.status === 'In Progress' ? 'badge-active' : 'badge-inactive'
                        }`}>
                        {task.status || "Pending"}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${task.priority === 'High' ? 'badge-inactive' : 'badge-active'
                        }`}>
                        {task.priority || "Normal"}
                      </span>
                    </td>
                    <td style={{ display: 'flex', gap: '0.5rem' }}>
                      {userRole === 'admin' ? (
                        <>
                          <button
                            className="action-btn btn-small"
                            onClick={() => handleOpenAssignModal(task)}
                            title="Assign Employees"
                            style={{ color: 'var(--primary)' }}
                          >
                            <Users size={18} />
                          </button>
                          <button
                            className="action-btn btn-small"
                            onClick={() => handleEdit(task)}
                            title="Edit Task"
                            style={{ color: 'var(--primary)' }}
                          >
                            <Edit size={18} />
                          </button>
                          <button
                            className="action-btn btn-small"
                            onClick={() => handleDelete(task.TaskId)}
                            title="Delete Task"
                            style={{ color: '#ef4444' }}
                          >
                            <Trash2 size={18} />
                          </button>
                        </>
                      ) : (
                        <select 
                          value={task.status}
                          onChange={(e) => handleUpdateStatus(task.TaskId, e.target.value)}
                          style={{ 
                            padding: '0.25rem 0.5rem', 
                            borderRadius: '0.5rem',
                            border: '1px solid var(--card-border)',
                            fontSize: '0.875rem',
                            background: 'var(--input-bg)',
                            color: 'var(--foreground)'
                          }}
                        >
                          <option value="Pending">Pending</option>
                          <option value="In Progress">In Progress</option>
                          <option value="Completed">Completed</option>
                        </select>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2 style={{ marginBottom: '1.5rem' }}>{editingId ? 'Edit Task' : 'Create New Task'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Task Name</label>
                <input
                  required
                  value={formData.TaskName}
                  onChange={(e) => setFormData({ ...formData, TaskName: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  required
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  style={{
                    width: '100%', padding: '0.875rem 1rem', borderRadius: '0.75rem',
                    border: '1px solid var(--card-border)', background: 'var(--input-bg)',
                    color: 'var(--foreground)', fontSize: '1rem', fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    style={{
                      width: '100%', padding: '0.875rem 1rem', borderRadius: '0.75rem',
                      border: '1px solid var(--card-border)', background: 'var(--input-bg)',
                      color: 'var(--foreground)', fontSize: '1rem'
                    }}
                  >
                    <option value="Pending">Pending</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Priority</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                    style={{
                      width: '100%', padding: '0.875rem 1rem', borderRadius: '0.75rem',
                      border: '1px solid var(--card-border)', background: 'var(--input-bg)',
                      color: 'var(--foreground)', fontSize: '1rem'
                    }}
                  >
                    <option value="Low">Low</option>
                    <option value="Normal">Normal</option>
                    <option value="High">High</option>
                  </select>
                </div>
              </div>

              <div className="flex" style={{ gap: '1rem', marginTop: '2rem' }}>
                <button
                  type="button"
                  onClick={handleCloseModal}
                  style={{ background: 'transparent', border: '1px solid var(--card-border)', color: 'var(--foreground)', boxShadow: 'none' }}
                >
                  Cancel
                </button>
                <button type="submit">
                  {editingId ? 'Update Task' : 'Save Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showAssignModal && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ maxWidth: '500px' }}>
            <h2 style={{ marginBottom: '1rem' }}>Assign Employees</h2>
            <p className="subtitle" style={{ marginBottom: '1.5rem' }}>Select employees to assign to this task</p>

            <div style={{ maxHeight: '300px', overflowY: 'auto', marginBottom: '1.5rem', border: '1px solid var(--card-border)', borderRadius: '0.75rem' }}>
              {employees.length === 0 ? (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--muted)' }}>
                  No employees found
                </div>
              ) : (
                employees.map(emp => (
                  <div
                    key={emp.EmpId}
                    onClick={() => toggleEmployeeSelection(emp.EmpId)}
                    style={{
                      padding: '0.75rem 1rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem',
                      cursor: 'pointer',
                      borderBottom: '1px solid var(--card-border)',
                      background: selectedEmpIds.includes(emp.EmpId) ? 'rgba(var(--primary-rgb), 0.1)' : 'transparent'
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedEmpIds.includes(emp.EmpId)}
                      onChange={() => { }} // Handled by div click
                      style={{ width: '1.2rem', height: '1.2rem', cursor: 'pointer' }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 500 }}>{emp.FirstName} {emp.LastName}</div>
                      <div style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>{emp.Email}</div>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="flex" style={{ gap: '1rem' }}>
              <button
                type="button"
                onClick={() => { setShowAssignModal(false); setAssignTaskId(null); }}
                style={{ background: 'transparent', border: '1px solid var(--card-border)', color: 'var(--foreground)', boxShadow: 'none' }}
              >
                Cancel
              </button>
              <button
                onClick={handleAssignSubmit}
                disabled={isAssigning}
                style={{ flex: 1 }}
              >
                {isAssigning ? <Loader2 className="animate-spin" size={20} /> : 'Save Assignments'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
