import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = 'http://localhost:5000/api';

const AdminDashboard = () => {
  const { token } = useAuth();
  const [pendingEmployees, setPendingEmployees] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({});
  const [newTask, setNewTask] = useState({ title: '', description: '', assigned_to: '' });
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    await Promise.all([
      fetchPendingEmployees(),
      fetchEmployees(),
      fetchTasks(),
      fetchStats()
    ]);
  };

  const fetchPendingEmployees = async () => {
    try {
      const response = await axios.get(`${API_URL}/admin/pending-employees`);
      setPendingEmployees(response.data);
    } catch (error) {
      console.error('Error fetching pending employees:', error);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await axios.get(`${API_URL}/admin/employees`);
      setEmployees(response.data);
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API_URL}/admin/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/admin/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleApprove = async (userId) => {
    try {
      await axios.put(`${API_URL}/admin/approve/${userId}`);
      alert('Employee approved successfully!');
      fetchPendingEmployees();
      fetchEmployees();
    } catch (error) {
      alert('Error approving employee: ' + error.response?.data?.message);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!newTask.title || !newTask.assigned_to) {
      alert('Please fill all required fields');
      return;
    }
    
    try {
      await axios.post(`${API_URL}/admin/tasks`, newTask);
      alert('Task created successfully!');
      setNewTask({ title: '', description: '', assigned_to: '' });
      fetchTasks();
      fetchStats();
    } catch (error) {
      alert('Error creating task: ' + error.response?.data?.message);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch(status) {
      case 'Completed': return 'bg-success';
      case 'In Progress': return 'bg-warning';
      default: return 'bg-secondary';
    }
  };

  return (
    <div className="container mt-4">
      <h2>Admin Dashboard</h2>
      
      {/* Stats Cards */}
      {activeTab === 'dashboard' && (
        <div className="row mb-4">
          <div className="col-md-4">
            <div className="card text-white bg-primary">
              <div className="card-body">
                <h5 className="card-title">Total Employees</h5>
                <h2>{stats.total_employees || 0}</h2>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card text-white bg-warning">
              <div className="card-body">
                <h5 className="card-title">Pending Approvals</h5>
                <h2>{stats.pending_approvals || 0}</h2>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card text-white bg-info">
              <div className="card-body">
                <h5 className="card-title">Tasks Summary</h5>
                <p>Pending: {stats.tasks_summary?.Pending || 0}</p>
                <p>In Progress: {stats.tasks_summary?.['In Progress'] || 0}</p>
                <p>Completed: {stats.tasks_summary?.Completed || 0}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <ul className="nav nav-tabs mb-3">
        <li className="nav-item">
          <button className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`} 
                  onClick={() => setActiveTab('dashboard')}>
            Dashboard
          </button>
        </li>
        <li className="nav-item">
          <button className={`nav-link ${activeTab === 'approvals' ? 'active' : ''}`} 
                  onClick={() => setActiveTab('approvals')}>
            Pending Approvals ({pendingEmployees.length})
          </button>
        </li>
        <li className="nav-item">
          <button className={`nav-link ${activeTab === 'tasks' ? 'active' : ''}`} 
                  onClick={() => setActiveTab('tasks')}>
            Create Task
          </button>
        </li>
        <li className="nav-item">
          <button className={`nav-link ${activeTab === 'viewtasks' ? 'active' : ''}`} 
                  onClick={() => setActiveTab('viewtasks')}>
            View All Tasks
          </button>
        </li>
        <li className="nav-item">
          <button className={`nav-link ${activeTab === 'employees' ? 'active' : ''}`} 
                  onClick={() => setActiveTab('employees')}>
            Employees List
          </button>
        </li>
      </ul>

      {/* Pending Approvals Tab */}
      {activeTab === 'approvals' && (
        <div>
          <h4>Pending Employee Approvals</h4>
          {pendingEmployees.length === 0 ? (
            <p>No pending approvals</p>
          ) : (
            <div className="table-responsive">
              <table className="table table-bordered">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Registration Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingEmployees.map(emp => (
                    <tr key={emp._id}>
                      <td>{emp.username}</td>
                      <td>{emp.email}</td>
                      <td>{new Date(emp.created_at).toLocaleDateString()}</td>
                      <td>
                        <button className="btn btn-success btn-sm" 
                                onClick={() => handleApprove(emp._id)}>
                          Approve
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Create Task Tab */}
      {activeTab === 'tasks' && (
        <div>
          <h4>Create New Task</h4>
          <form onSubmit={handleCreateTask}>
            <div className="mb-3">
              <label className="form-label">Task Title *</label>
              <input
                type="text"
                className="form-control"
                value={newTask.title}
                onChange={(e) => setNewTask({...newTask, title: e.target.value})}
                required
              />
            </div>
            <div className="mb-3">
              <label className="form-label">Description</label>
              <textarea
                className="form-control"
                rows="3"
                value={newTask.description}
                onChange={(e) => setNewTask({...newTask, description: e.target.value})}
              ></textarea>
            </div>
            <div className="mb-3">
              <label className="form-label">Assign To *</label>
              <select
                className="form-control"
                value={newTask.assigned_to}
                onChange={(e) => setNewTask({...newTask, assigned_to: e.target.value})}
                required
              >
                <option value="">Select Employee</option>
                {employees.filter(emp => emp.is_approved).map(emp => (
                  <option key={emp._id} value={emp._id}>{emp.username}</option>
                ))}
              </select>
            </div>
            <button type="submit" className="btn btn-primary">Create Task</button>
          </form>
        </div>
      )}

      {/* View Tasks Tab */}
      {activeTab === 'viewtasks' && (
        <div>
          <h4>All Tasks</h4>
          <div className="table-responsive">
            <table className="table table-bordered">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Description</th>
                  <th>Assigned To</th>
                  <th>Status</th>
                  <th>Created Date</th>
                </tr>
              </thead>
              <tbody>
                {tasks.map(task => (
                  <tr key={task._id}>
                    <td>{task.title}</td>
                    <td>{task.description || '-'}</td>
                    <td>{task.assigned_to_name || task.assigned_to}</td>
                    <td>
                      <span className={`badge ${getStatusBadgeClass(task.status)}`}>
                        {task.status}
                      </span>
                    </td>
                    <td>{new Date(task.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
                {tasks.length === 0 && (
                  <tr>
                    <td colSpan="5" className="text-center">No tasks found</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Employees List Tab */}
      {activeTab === 'employees' && (
        <div>
          <h4>All Employees</h4>
          <div className="table-responsive">
            <table className="table table-bordered">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Registered Date</th>
                </tr>
              </thead>
              <tbody>
                {employees.map(emp => (
                  <tr key={emp._id}>
                    <td>{emp.username}</td>
                    <td>{emp.email}</td>
                    <td>
                      <span className={`badge ${emp.is_approved ? 'bg-success' : 'bg-warning'}`}>
                        {emp.is_approved ? 'Approved' : 'Pending'}
                      </span>
                    </td>
                    <td>{new Date(emp.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;