"use client";

import React, { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { projectService, teamService, taskService, authService } from "@/services/api";
import { Loader2, ArrowLeft, Briefcase, Users, CheckSquare, Calendar, Clock, History } from "lucide-react";
import Link from "next/link";

export default function ProjectDetailsPage() {
  const { id } = useParams();
  const router = useRouter();
  const [project, setProject] = useState<any>(null);
  const [teams, setTeams] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [userRole, setUserRole] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const [proj, teamsData, tasksData, user] = await Promise.all([
          projectService.getProject(Number(id)),
          teamService.getTeams({ project_id: Number(id) }),
          taskService.getTasks({ project_id: Number(id) }),
          authService.getCurrentUser()
        ]);
        
        if (user.role !== 'admin') {
          router.push('/dashboard/projects');
          return;
        }

        setProject(proj);
        setTeams(teamsData);
        setTasks(tasksData);
        setUserRole(user.role);
      } catch (err) {
        console.error("Failed to fetch project details", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [id, router]);

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="animate-spin text-primary" size={48} />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="glass-card text-center py-20">
        <h2>Project not found</h2>
        <Link href="/dashboard/projects" className="text-link">Back to Projects</Link>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div className="flex items-center gap-4">
          <Link href="/dashboard/projects" className="action-btn">
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1>{project.ProjectName}</h1>
            <p className="subtitle">Project Details & Resources</p>
          </div>
        </div>
      </div>

      <div className="grid-2 gap-8 mb-8" style={{ gridTemplateColumns: '2fr 1fr' }}>
        <div className="glass-card">
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Briefcase size={20} className="text-primary" /> About Project
          </h2>
          <p style={{ lineHeight: '1.6', color: 'var(--foreground)', opacity: 0.9 }}>
            {project.Description || "No description provided for this project."}
          </p>
          
          <div className="flex gap-6 mt-6 pt-6" style={{ borderTop: '1px solid var(--card-border)' }}>
            <div className="flex flex-col gap-1">
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Created On</span>
              <div className="flex items-center gap-2">
                <Calendar size={16} className="text-primary" />
                <span style={{ fontWeight: 600 }}>{new Date(project.created_at).toLocaleDateString()}</span>
              </div>
            </div>
            <div className="flex flex-col gap-1">
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>Status</span>
              <span className={`badge ${project.Status === 'Completed' ? 'badge-active' : 'badge-pending'}`} style={{ width: 'fit-content' }}>
                {project.Status}
              </span>
            </div>
          </div>
        </div>

        <div className="glass-card">
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Users size={20} className="text-primary" /> Assigned Teams
          </h2>
          {teams.length > 0 ? (
            <div className="flex flex-col gap-3">
              {teams.map(team => (
                <div key={team.TeamId} className="flex items-center justify-between p-3 rounded-lg" style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--card-border)' }}>
                  <div className="flex items-center gap-3">
                    <div className="avatar" style={{ width: '32px', height: '32px', fontSize: '0.8rem' }}>
                      {team.TeamName[0].toUpperCase()}
                    </div>
                    <span style={{ fontWeight: 600 }}>{team.TeamName}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted text-center py-4">No teams assigned yet.</p>
          )}
        </div>
      </div>

      <div className="glass-card">
        <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <CheckSquare size={20} className="text-primary" /> Project Tasks
        </h2>
        {tasks.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Task</th>
                <th>Status</th>
                <th>Priority</th>
                <th>Team</th>
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
                    <span className={`badge ${task.status === 'Completed' ? 'badge-active' : task.status === 'In Progress' ? 'badge-pending' : ''}`}>
                      {task.status}
                    </span>
                  </td>
                  <td>{task.priority}</td>
                  <td>{teams.find(t => t.TeamId === task.team_id)?.TeamName || "No Team"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-center py-10">
             <CheckSquare size={48} className="text-muted mb-4" />
             <p className="subtitle">No tasks found for this project.</p>
          </div>
        )}
      </div>
    </div>
  );
}
