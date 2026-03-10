import { useEffect } from 'react';

export default function LoginPage() {
  useEffect(() => {
    // Redirect to Replit auth
    window.location.href = '/api/login';
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-gray-900 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-xl font-bold font-display uppercase tracking-tight">Redirecting to login...</p>
      </div>
    </div>
  );
}
