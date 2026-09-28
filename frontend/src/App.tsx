import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { CyberBackground } from './components/CyberBackground';
import { PageTransition } from './components/motion/MotionSystem';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { ScanPage } from './pages/ScanPage';
import { ScanResultPage } from './pages/ScanResultPage';
import { HistoryPage } from './pages/HistoryPage';
import { AuditPage } from './pages/AuditPage';
import { SettingsPage } from './pages/SettingsPage';
import { AiFirewallPage } from './pages/AiFirewallPage';

const ProtectedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-priva-bg flex items-center justify-center">
        <div className="w-8 h-8 rounded-full border-2 border-priva-primary border-t-transparent animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="min-h-screen bg-priva-bg flex flex-col relative z-10">
      <Navbar />
      <div className="flex-1 flex">
        <Sidebar />
        <main className="flex-1 overflow-x-hidden relative">{children}</main>
      </div>
    </div>
  );
};

const AnimatedRoutes: React.FC = () => {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        {/* Public Routes */}
        <Route
          path="/"
          element={
            <PageTransition>
              <div className="min-h-screen bg-priva-bg flex flex-col relative z-10">
                <Navbar />
                <LandingPage />
              </div>
            </PageTransition>
          }
        />
        <Route
          path="/login"
          element={
            <PageTransition>
              <div className="min-h-screen bg-priva-bg flex flex-col relative z-10">
                <Navbar />
                <LoginPage />
              </div>
            </PageTransition>
          }
        />
        <Route
          path="/register"
          element={
            <PageTransition>
              <div className="min-h-screen bg-priva-bg flex flex-col relative z-10">
                <Navbar />
                <RegisterPage />
              </div>
            </PageTransition>
          }
        />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedLayout>
              <PageTransition>
                <DashboardPage />
              </PageTransition>
            </ProtectedLayout>
          }
        />
        <Route
          path="/ai-firewall"
          element={
            <ProtectedLayout>
              <PageTransition>
                <AiFirewallPage />
              </PageTransition>
            </ProtectedLayout>
          }
        />
        <Route
          path="/scan"
          element={
            <ProtectedLayout>
              <PageTransition>
                <ScanPage />
              </PageTransition>
            </ProtectedLayout>
          }
        />
        <Route
          path="/scan/:id"
          element={
            <ProtectedLayout>
              <PageTransition>
                <ScanResultPage />
              </PageTransition>
            </ProtectedLayout>
          }
        />
        <Route
          path="/history"
          element={
            <ProtectedLayout>
              <PageTransition>
                <HistoryPage />
              </PageTransition>
            </ProtectedLayout>
          }
        />
        <Route path="/evaluation" element={<Navigate to="/dashboard" replace />} />
        <Route
          path="/audit"
          element={
            <ProtectedLayout>
              <PageTransition>
                <AuditPage />
              </PageTransition>
            </ProtectedLayout>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedLayout>
              <PageTransition>
                <SettingsPage />
              </PageTransition>
            </ProtectedLayout>
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AnimatePresence>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <div className="relative min-h-screen bg-[#0B0F19]">
        <CyberBackground />
        <BrowserRouter>
          <AnimatedRoutes />
        </BrowserRouter>
      </div>
    </AuthProvider>
  );
};

export default App;
