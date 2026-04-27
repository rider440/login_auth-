import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized error (e.g., redirect to login or clear token)
      localStorage.removeItem('token');
      if (typeof window !== 'undefined') {
        // window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  async register(userData: any) {
    const response = await api.post('/register', userData);
    return response.data;
  },

  async checkPhone(phone: string) {
    const response = await api.post('/auth/check-phone', { phone });
    return response.data;
  },

  async sendOtp(phone: string) {
    const response = await api.post('/send-otp', { phone });
    return response.data;
  },

  async verifyOtp(phone: string, otp: string) {
    const response = await api.post('/verify-otp', { phone, otp });
    return response.data;
  },

  async employeeLogin(phone: string, loginCode: string) {
    const response = await api.post('/auth/employee-login', { 
      phone, 
      login_code: loginCode 
    });
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get('/me');
    return response.data;
  },
};

export const employeeService = {
  async getEmployees() {
    const response = await api.get('/employees/');
    return response.data;
  },
  async getEmployee(id: number) {
    const response = await api.get(`/employees/${id}`);
    return response.data;
  },
  async createEmployee(employeeData: any) {
    const response = await api.post('/employees/', employeeData);
    return response.data;
  },
  async updateEmployee(id: number, employeeData: any) {
    const response = await api.put(`/employees/${id}`, employeeData);
    return response.data;
  },
  async deleteEmployee(id: number) {
    const response = await api.delete(`/employees/${id}`);
    return response.data;
  }
};

export const taskService = {
  async getTasks(params?: { project_id?: number, team_id?: number }) {
    const response = await api.get('/tasks/', { params });
    return response.data;
  },
  async getTask(id: number) {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  },
  async createTask(taskData: any) {
    const response = await api.post('/tasks/', taskData);
    return response.data;
  },
  async updateTask(id: number, taskData: any) {
    const response = await api.put(`/tasks/${id}`, taskData);
    return response.data;
  },
  async deleteTask(id: number) {
    const response = await api.delete(`/tasks/${id}`);
    return response.data;
  },
  async assignTask(assignmentData: { task_id: number, emp_id: number }) {
    const response = await api.post('/tasks/assign/', assignmentData);
    return response.data;
  },
  async getTaskAssignments(taskId: number) {
    const response = await api.get(`/tasks/${taskId}/assignments`);
    return response.data;
  },
  async deleteTaskAssignment(assignmentId: number) {
    const response = await api.delete(`/tasks/assignments/${assignmentId}`);
    return response.data;
  },
  async bulkAssignTask(assignmentData: { task_id: number, emp_ids: number[] }) {
    const response = await api.post('/tasks/bulk-assign/', assignmentData);
    return response.data;
  }
};

export const projectService = {
  async getProjects() {
    const response = await api.get('/projects/');
    return response.data;
  },
  async getProject(id: number) {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },
  async createProject(projectData: any) {
    const response = await api.post('/projects/', projectData);
    return response.data;
  },
  async updateProject(id: number, projectData: any) {
    const response = await api.put(`/projects/${id}`, projectData);
    return response.data;
  },
  async deleteProject(id: number) {
    const response = await api.delete(`/projects/${id}`);
    return response.data;
  }
};

export const teamService = {
  async getTeams(params?: { project_id?: number }) {
    const response = await api.get('/teams/', { params });
    return response.data;
  },
  async getTeam(id: number) {
    const response = await api.get(`/teams/${id}`);
    return response.data;
  },
  async createTeam(teamData: any) {
    const response = await api.post('/teams/', teamData);
    return response.data;
  },
  async updateTeam(id: number, teamData: any) {
    const response = await api.put(`/teams/${id}`, teamData);
    return response.data;
  },
  async deleteTeam(id: number) {
    const response = await api.delete(`/teams/${id}`);
    return response.data;
  }
};

export const reportService = {
  async createReport(reportData: { task_id: number, UpdateContent: string, Status: string }) {
    const response = await api.post('/reports/', reportData);
    return response.data;
  },
  async getReports(params?: { emp_id?: number, task_id?: number }) {
    const response = await api.get('/reports/', { params });
    return response.data;
  }
};

export default api;
