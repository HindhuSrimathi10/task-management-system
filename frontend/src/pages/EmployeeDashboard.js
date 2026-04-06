import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const API_URL = 'http://localhost:5000/api';

const EmployeeDashboard = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API_URL}/employee/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
      alert('Error loading tasks');
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (taskId, newStatus) => {
    try {
      await axios.put(`${API_URL}/employee/tasks/${taskId}/status`, {
        status: newStatus
      });
      alert('Task status updated!');
      fetchTasks();
    } catch (error) {
      alert('Error updating task: ' + error.response?.data?.message);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch(status) {
      case 'Completed': return 'bg-success';
      case 'In Progress': return 'bg-warning';
      default: return 'bg-secondary';
    }
  };

  if (loading) {
    return <div className="container mt-5 text-center">Loading...</div>;
  }

  return (
    <div className="container mt-4">
      <div className="row">
        <div className="col-12">
          <h2>My Tasks</h2>
          <p className="text-muted">Welcome, {user?.username}</p>
          
          {tasks.length === 0 ? (
            <div className="alert alert-info">
              No tasks assigned yet. Check back later!
            </div>
          ) : (
            <div className="table-responsive">
              <table className="table table-bordered table-hover">
                <thead className="table-dark">
                  <tr>
                    <th>Task Title</th>
                    <th>Description</th>
                    <th>Current Status</th>
                    <th>Assigned Date</th>
                    <th>Update Status</th>
                  </tr>
                </thead>
                <tbody>
                  {tasks.map(task => (
                    <tr key={task._id}>
                      <td><strong>{task.title}</strong></td>
                      <td>{task.description || 'No description'}</td>
                      <td>
                        <span className={`badge ${getStatusBadgeClass(task.status)}`}>
                          {task.status}
                        </span>
                      </td>
                      <td>{new Date(task.created_at).toLocaleDateString()}</td>
                      <td>
                        <select
                          className="form-select form-select-sm"
                          value={task.status}
                          onChange={(e) => updateStatus(task._id, e.target.value)}
                          style={{ width: 'auto', display: 'inline-block' }}
                        >
                          <option value="Pending">Pending</option>
                          <option value="In Progress">In Progress</option>
                          <option value="Completed">Completed</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default EmployeeDashboard;