import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import AdminDashboard from './AdminDashboard';
import EmployeeDashboard from './EmployeeDashboard';

const Dashboard = () => {
  const { user } = useAuth();

  if (!user) {
    return <div>Redirecting...</div>;
  }

  return user.role === 'admin' ? <AdminDashboard /> : <EmployeeDashboard />;
};

export default Dashboard;