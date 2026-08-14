import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import "./index.css";

// Components
import { Navbar } from "./components/layout/Navbar";

// Pages
import Login from './pages/auth/Login';
import Signup from './pages/auth/Signup';
import Dashboard from './pages/dashboard/Dashboard';
import Profile from './pages/profile/Profile';
import ProfileView from './pages/profile/ProfileView';
import SetupInterview from './pages/interview/SetupInterview';
import InterviewSession from './pages/interview/InterviewSession';
import Report from './pages/interview/Report';

import InterviewDetails from './pages/interview/InterviewDetails';

// Layout wrapper for authenticated pages
const AppLayout = ({ children }) => (
  <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
    <Navbar />
    <main style={{ flex: 1, backgroundColor: "var(--bg-secondary)" }}>
      {children}
    </main>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Auth routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Main App Routes (Wrapped with Layout) */}
          <Route path="/dashboard" element={<AppLayout><Dashboard /></AppLayout>} />
          <Route path="/profile" element={<AppLayout><ProfileView /></AppLayout>} />
          <Route path="/profile/new" element={<AppLayout><Profile /></AppLayout>} />
          <Route path="/profile/update" element={<AppLayout><Profile /></AppLayout>} />
          <Route path="/interview/start" element={<AppLayout><SetupInterview /></AppLayout>} />
          <Route path="/interview/:session_id" element={<AppLayout><InterviewSession /></AppLayout>} />
          <Route path="/report/:session_id" element={<AppLayout><Report /></AppLayout>} />
          <Route path="/interview/details/:interview_id" element={<AppLayout><InterviewDetails /></AppLayout>} />
          
          {/* Default redirect */}
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
