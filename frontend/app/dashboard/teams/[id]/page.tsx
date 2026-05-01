"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { teamService, taskService, projectService } from "@/services/api";
import { Users, Briefcase, CheckSquare, Loader2, User as UserIcon, Calendar, Clock } from "lucide-react";

export default function TeamProfilePage() {
  const { id } = useParams();
  const [team, setTeam] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [project, setProject] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const teamData = await teamService.getTeam(Number(id));
        setTeam(teamData);

        const [tasksData, projectData] = await Promise.all([
          taskService.getTasks({ team_id: Number(id) }),
          projectService.getProject(teamData.project_id)
        ]);
        
        setTasks(tasksData);
        setProject(projectData);
      } catch (err) {
        setError("Failed to load team profile");
      } finally {
        setIsLoading(false);
      }
    };

    if (id) fetchData();
  }, [id]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 className="animate-spin text-primary" size={48} />
        <p className="mt-4 text-muted">Loading team profile...</p>
      </div>
    );
  }

  if (error || !team) {
    return (
      <div className="glass-card text-center py-10">
        <h2 className="text-error">Error</h2>
        <p className="subtitle">{error || "Team not found"}</p>
        <button className="mt-4" onClick={() => window.location.href = "/dashboard/teams"}>Back to Teams</button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Team Header Card */}
      <div className="glass-card" style={{ padding: '2.5rem' }}>
        <div className="flex justify-between items-start">
          <div className="flex gap-6 items-center">
            <div className="stat-icon" style={{ width: '80px', height: '80px', borderRadius: '1.5rem', background: 'rgba(236, 72, 153, 0.1)', color: 'var(--secondary)' }}>
              <Users size={40} />
            </div>
            <div>
              <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{team.TeamName}</h1>
              <div className="flex items-center gap-4 text-muted">
                <span className="flex items-center gap-2">
                  <Briefcase size={18} /> {project?.ProjectName || "No Project"}
                </span>
                <span className="flex items-center gap-2">
                  <Users size={18} /> {team.members.length} Members
                </span>
                <span className="flex items-center gap-2">
                  <Calendar size={18} /> Created {new Date(team.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Members List */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <div className="glass-card h-full">
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Users size={20} /> Team Members
            </h2>
            <div className="flex flex-col gap-4">
              {team.members.map((member: any) => (
                <div key={member.EmpId} className="flex items-center gap-4 p-3 rounded-xl hover:bg-white/5 transition-colors">
                  <div className="avatar" style={{ width: '48px', height: '48px' }}>
                    {member.FirstName[0]}{member.LastName[0]}
                  </div>
                  <div>
                    <div style={{ fontWeight: 600 }}>{member.FirstName} {member.LastName}</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{member.Email}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Team Tasks */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="glass-card">
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckSquare size={20} /> Team Tasks
            </h2>
            
            {tasks.length === 0 ? (
              <div className="text-center py-10 text-muted">
                No tasks assigned to this team yet.
              </div>
            ) : (
              <div className="flex flex-col gap-4">
                {tasks.map(task => (
                  <div key={task.TaskId} className="history-item" style={{ padding: '1.25rem' }}>
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 style={{ fontSize: '1.1rem', marginBottom: '0.25rem' }}>{task.TaskName}</h4>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>{task.description}</p>
                        <div className="flex gap-4">
                           <span className="flex items-center gap-1" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                             <Clock size={14} /> Due: {task.priority} Priority
                           </span>
                        </div>
                      </div>
                      <span className={`badge ${task.status === 'Completed' ? 'badge-active' : 'badge-pending'}`}>
                        {task.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
