import React, { lazy, Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/PrivateRoute';

// Lazy load pages for better performance
const Home = lazy(() => import('./pages/Home'));
const Chat = lazy(() => import('./pages/Chat'));

// Loading fallback component
const LoadingScreen = () => (
  <div className="flex items-center justify-center h-screen bg-[#0b1220]">
    <div className="text-slate-400">Loading...</div>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <Suspense fallback={<LoadingScreen />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Home initialAuthMode="login" />} />
            <Route path="/register" element={<Home initialAuthMode="register" />} />
            <Route
              path="/chat"
              element={
                <PrivateRoute>
                  <Chat />
                </PrivateRoute>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </Router>
    </AuthProvider>
  );
}

export default App;
