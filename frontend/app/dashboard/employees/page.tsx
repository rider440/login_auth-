"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { employeeService } from "@/services/api";
import { Loader2, Plus, Users, Eye, Edit, Trash2 } from "lucide-react";

export default function EmployeesPage() {
  const [employees, setEmployees] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    EmpName: "",
    Email: "",
    Phone: ""
  });

  const fetchEmployees = async () => {
    try {
      setIsLoading(true);
      const data = await employeeService.getEmployees();
      setEmployees(data);
    } catch (err) {
      setError("Failed to load employees");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingId) {
        await employeeService.updateEmployee(editingId, formData);
      } else {
        await employeeService.createEmployee(formData);
      }
      handleCloseModal();
      fetchEmployees();
    } catch (err) {
      alert(`Failed to ${editingId ? 'update' : 'create'} employee`);
    }
  };

  const handleEdit = (emp: any) => {
    setEditingId(emp.EmpId);
    setFormData({
      EmpName: emp.EmpName,
      Email: emp.Email,
      Phone: emp.Phone
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this employee?")) {
      try {
        await employeeService.deleteEmployee(id);
        fetchEmployees();
      } catch (err) {
        alert("Failed to delete employee");
      }
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingId(null);
    setFormData({ EmpName: "", Email: "", Phone: "" });
  };

  return (
    <div >
      <div className="page-header">
        <div>
          <h1 style={{ marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Users size={28} /> Employees
          </h1>
          <p className="subtitle" style={{ marginBottom: 0 }}>Manage your company's employees</p>
        </div>
        <button onClick={() => setShowModal(true)} style={{ width: 'auto', padding: '0.75rem 1.5rem' }}>
          <Plus size={20} />
          Add Employee
        </button>
      </div>

      <div className="glass-card" style={{ maxWidth: '100%', padding: '1.5rem' }}>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="animate-spin text-primary" size={32} />
          </div>
        ) : error ? (
          <div className="error-text text-center py-4">{error}</div>
        ) : employees.length === 0 ? (
          <div className="text-center py-8 text-muted">
            <p>No employees found. Add one to get started!</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((emp) => (
                  <tr key={emp.EmpId}>
                    <td>#{emp.EmpId}</td>
                    <td>{emp.EmpName}</td>
                    <td>{emp.Email || "N/A"}</td>
                    <td>{emp.Phone || "N/A"}</td>
                    <td>
                      <span className={`badge ${emp.is_active ? 'badge-active' : 'badge-inactive'}`}>
                        {emp.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ display: 'flex', gap: '0.5rem' }}>
                      <Link href={`/dashboard/employees/${emp.EmpId}`}>
                        <button className="action-btn btn-small" title="View Profile">
                          <Eye size={18} />
                        </button>
                      </Link>
                      <button 
                        className="action-btn btn-small" 
                        onClick={() => handleEdit(emp)}
                        title="Edit Employee"
                        style={{ color: 'var(--primary)' }}
                      >
                        <Edit size={18} />
                      </button>
                      <button 
                        className="action-btn btn-small" 
                        onClick={() => handleDelete(emp.EmpId)}
                        title="Delete Employee"
                        style={{ color: '#ef4444' }}
                      >
                        <Trash2 size={18} />
                      </button>
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
            <h2 style={{ marginBottom: '1.5rem' }}>{editingId ? 'Edit Employee' : 'Add New Employee'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Full Name</label>
                <input
                  required
                  placeholder="e.g. John Doe"
                  value={formData.EmpName}
                  onChange={(e) => setFormData({ ...formData, EmpName: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.Email}
                  onChange={(e) => setFormData({ ...formData, Email: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Phone Number</label>
                <input
                  value={formData.Phone}
                  onChange={(e) => setFormData({ ...formData, Phone: e.target.value })}
                />
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
                  {editingId ? 'Update Employee' : 'Save Employee'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
