"use client";

import React, { useEffect, useState } from "react";
import { teamService, projectService, employeeService } from "@/services/api";
import { Plus, Users, Briefcase, User as UserIcon, Trash2, Edit } from "lucide-react";

interface Team {
  TeamId: number;
  TeamName: string;
  project_id: number;
  members: any[];
}

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingTeamId, setEditingTeamId] = useState<number | null>(null);
  
  const [formData, setFormData] = useState({ 
    TeamName: "", 
    project_id: 0,
    member_ids: [] as number[]
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [teamsData, projectsData, employeesData] = await Promise.all([
        teamService.getTeams(),
        projectService.getProjects(),
        employeeService.getEmployees()
      ]);
      setTeams(teamsData);
      setProjects(projectsData);
      setEmployees(employeesData);
    } catch (err) {
      console.error("Failed to fetch teams data", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.project_id === 0) return alert("Please select a project");
    
    try {
      if (editingTeamId) {
        await teamService.updateTeam(editingTeamId, formData);
      } else {
        await teamService.createTeam(formData);
      }
      handleCloseModal();
      fetchData();
    } catch (err) {
      alert(`Failed to ${editingTeamId ? 'update' : 'create'} team`);
    }
  };

  const handleEdit = (team: Team) => {
    setEditingTeamId(team.TeamId);
    setFormData({
      TeamName: team.TeamName,
      project_id: team.project_id,
      member_ids: team.members.map(m => m.EmpId)
    });
    setShowAddModal(true);
  };

  const handleCloseModal = () => {
    setShowAddModal(false);
    setEditingTeamId(null);
    setFormData({ TeamName: "", project_id: 0, member_ids: [] });
  };

  const toggleMember = (empId: number) => {
    setFormData(prev => ({
      ...prev,
      member_ids: prev.member_ids.includes(empId)
        ? prev.member_ids.filter(id => id !== empId)
        : [...prev.member_ids, empId]
    }));
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure?")) return;
    try {
      await teamService.deleteTeam(id);
      fetchData();
    } catch (err) {
      alert("Failed to delete team");
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Teams</h1>
          <p className="subtitle">Organize employees into project-specific teams</p>
        </div>
        <button className="btn-small" onClick={() => setShowAddModal(true)}>
          <Plus size={20} />
          Create Team
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-10">Loading teams...</div>
      ) : (
        <div className="project-grid">
          {teams.map((team) => (
            <div key={team.TeamId} className="project-card">
              <div className="flex justify-between items-start mb-4">
                <div className="stat-icon" style={{ background: 'rgba(236, 72, 153, 0.1)', color: 'var(--secondary)' }}>
                  <Users size={24} />
                </div>
                <div className="flex gap-1">
                  <button className="action-btn" title="Edit Team" onClick={() => handleEdit(team)}>
                    <Edit size={16} />
                  </button>
                  <button className="action-btn text-error" title="Delete Team" onClick={() => handleDelete(team.TeamId)}>
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              
              <h3>{team.TeamName}</h3>
              <div className="flex items-center gap-2 text-muted mb-4" style={{ fontSize: '0.875rem' }}>
                <Briefcase size={16} />
                <span>{projects.find(p => p.ProjectId === team.project_id)?.ProjectName || "Unknown Project"}</span>
              </div>
              
              <div className="mb-6">
                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Members ({team.members.length})</label>
                <div className="flex -space-x-2 mt-2">
                  {team.members.slice(0, 5).map((member, i) => (
                    <div 
                      key={member.EmpId} 
                      className="avatar" 
                      style={{ 
                        width: '32px', 
                        height: '32px', 
                        border: '2px solid var(--background)',
                        fontSize: '0.7rem'
                      }}
                      title={`${member.FirstName} ${member.LastName}`}
                    >
                      {member.FirstName[0]}{member.LastName[0]}
                    </div>
                  ))}
                  {team.members.length > 5 && (
                    <div className="avatar" style={{ width: '32px', height: '32px', border: '2px solid var(--background)', background: 'var(--text-muted)', fontSize: '0.7rem' }}>
                      +{team.members.length - 5}
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-auto">
                <button 
                  className="btn-small w-full" 
                  style={{ background: 'rgba(255,255,255,0.05)', color: 'var(--foreground)' }}
                  onClick={() => window.location.href = `/dashboard/teams/${team.TeamId}`}
                >
                  View Team Profile
                </button>
              </div>
            </div>
          ))}

          {teams.length === 0 && (
            <div className="glass-card text-center py-10" style={{ gridColumn: '1/-1' }}>
              <Users size={48} className="text-muted mb-4" />
              <h3>No teams organized yet</h3>
              <p className="subtitle">Group your employees by project</p>
            </div>
          )}
        </div>
      )}

      {/* Team Modal */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-content glass-card" style={{ maxWidth: '600px' }}>
            <h2>{editingTeamId ? "Edit Team" : "Create Team"}</h2>
            <form onSubmit={handleSubmit} className="mt-4">
              <div className="form-group">
                <label>Team Name</label>
                <input 
                  type="text" 
                  required 
                  value={formData.TeamName}
                  onChange={(e) => setFormData({...formData, TeamName: e.target.value})}
                  placeholder="e.g. Frontend Squad"
                />
              </div>

              <div className="form-group">
                <label>Select Project</label>
                <select 
                   className="w-full p-3 rounded-xl border border-card-border bg-input-bg"
                   value={formData.project_id}
                   onChange={(e) => setFormData({...formData, project_id: parseInt(e.target.value)})}
                   style={{ width: '100%', padding: '0.875rem', borderRadius: '0.75rem', background: 'var(--input-bg)', border: '1px solid var(--card-border)' }}
                >
                  <option value={0}>Choose a project...</option>
                  {projects.map(p => (
                    <option key={p.ProjectId} value={p.ProjectId}>{p.ProjectName}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Select Members</label>
                <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid var(--card-border)', borderRadius: '0.75rem', padding: '0.5rem' }}>
                  {employees.map(emp => (
                    <div 
                      key={emp.EmpId} 
                      onClick={() => toggleMember(emp.EmpId)}
                      className={`flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors`}
                      style={{ 
                        background: formData.member_ids.includes(emp.EmpId) ? 'var(--primary)' : 'transparent',
                        color: formData.member_ids.includes(emp.EmpId) ? 'white' : 'inherit',
                        marginBottom: '4px'
                      }}
                    >
                      <UserIcon size={16} />
                      <span>{emp.FirstName} {emp.LastName}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-4 mt-6">
                <button type="button" onClick={handleCloseModal} style={{ background: 'rgba(0,0,0,0.1)', color: 'var(--foreground)' }}>
                  Cancel
                </button>
                <button type="submit">{editingTeamId ? "Update Team" : "Create Team"}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
