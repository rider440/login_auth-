"use client";

import React, { useEffect, useState } from "react";
import { projectService, authService } from "@/services/api";
import { Plus, Briefcase, Calendar, CheckCircle2, Clock, MoreVertical } from "lucide-react";
import Link from "next/link";

interface Project {
  ProjectId: number;
  ProjectName: string;
  Description: string;
  Status: string;
  created_at: string;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [userRole, setUserRole] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [newProject, setNewProject] = useState({ ProjectName: "", Description: "" });

  const fetchData = async () => {
    try {
      const [projData, userData] = await Promise.all([
        projectService.getProjects(),
        authService.getCurrentUser()
      ]);
      setProjects(projData);
      setUserRole(userData.role);
    } catch (err) {
      console.error("Failed to fetch projects", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await projectService.createProject(newProject);
      setShowAddModal(false);
      setNewProject({ ProjectName: "", Description: "" });
      fetchData();
    } catch (err) {
      alert("Failed to create project");
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Projects</h1>
          <p className="subtitle">Manage and track all your active projects</p>
        </div>
        <button className="btn-small" onClick={() => setShowAddModal(true)}>
          <Plus size={20} />
          Add Project
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-10">Loading projects...</div>
      ) : (
        <div className="project-grid">
          {projects.map((project) => (
            <Link
              key={project.ProjectId}
              href={`/dashboard/projects/${project.ProjectId}`}
              className="project-card"
              style={{ textDecoration: 'none', color: 'inherit' }}
            >
              <div className="flex justify-between items-start mb-4">
                <div className="stat-icon" style={{ background: 'rgba(79, 70, 229, 0.1)', color: 'var(--primary)' }}>
                  <Briefcase size={24} />
                </div>
                <span className={`badge ${project.Status === 'Completed' ? 'badge-active' : 'badge-pending'}`}>
                  {project.Status}
                </span>
              </div>

              <h3>{project.ProjectName}</h3>
              <p className="description">{project.Description || "No description provided."}</p>

              <div className="project-meta">
                <div className="flex items-center gap-2 text-muted" style={{ fontSize: '0.8rem' }}>
                  <Calendar size={14} />
                  <span>{new Date(project.created_at).toLocaleDateString()}</span>
                </div>
                <div className="flex gap-2">
                  <CheckCircle2 size={18} className="text-muted" />
                  <Clock size={18} className="text-muted" />
                </div>
              </div>
            </Link>
          ))}

          {projects.length === 0 && (
            <div className="glass-card text-center py-10" style={{ gridColumn: '1/-1' }}>
              <Briefcase size={48} className="text-muted mb-4" />
              <h3>No projects found</h3>
              <p className="subtitle">Start by creating your first project</p>
            </div>
          )}
        </div>
      )}

      {/* Add Project Modal */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal-content glass-card">
            <h2>Create New Project</h2>
            <form onSubmit={handleCreate} className="mt-4">
              <div className="form-group">
                <label>Project Name</label>
                <input
                  type="text"
                  required
                  value={newProject.ProjectName}
                  onChange={(e) => setNewProject({ ...newProject, ProjectName: e.target.value })}
                  placeholder="e.g. Website Redesign"
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <input
                  type="text"
                  value={newProject.Description}
                  onChange={(e) => setNewProject({ ...newProject, Description: e.target.value })}
                  placeholder="Brief project overview"
                />
              </div>
              <div className="flex gap-4">
                <button type="button" onClick={() => setShowAddModal(false)} style={{ background: 'rgba(0,0,0,0.1)', color: 'var(--foreground)' }}>
                  Cancel
                </button>
                <button type="submit">Create Project</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
