import { useState } from "react";
import { useLocation, Link } from "wouter";
import { motion } from "framer-motion";
import { ArrowLeft, Eye, EyeOff } from "lucide-react";

const isPurdueEmail = (email: string) =>
  email.trim().toLowerCase().endsWith("@purdue.edu");

export default function LoginPage() {
  const [, setLocation] = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [emailError, setEmailError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isPurdueEmail(email)) {
      setEmailError("Must be a @purdue.edu email address");
      return;
    }
    setEmailError("");
    setLoading(true);
    localStorage.setItem("user_email", email.trim().toLowerCase());
    // Simulate network delay then go to email verification
    setTimeout(() => {
      setLoading(false);
      setLocation("/verify-email");
    }, 700);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col">
      <div className="max-w-md mx-auto w-full pt-12 flex-1">
        <button
          onClick={() => setLocation("/welcome")}
          className="mb-8 p-2 hover:bg-gray-100 rounded-full transition-all"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[13px] font-bold text-orange-500 uppercase tracking-widest mb-2">
            Purdue Only
          </p>
          <h1 className="text-[38px] font-black font-display uppercase tracking-tighter leading-[0.92] mb-2">
            Welcome<br />back
          </h1>
          <p className="text-gray-500 font-medium mb-10">
            Sign in with your @purdue.edu email
          </p>
        </motion.div>

        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          onSubmit={handleSubmit}
          className="space-y-4"
        >
          {/* Email */}
          <div>
            <label className="block text-[11px] font-black text-gray-500 uppercase tracking-widest mb-2">
              Purdue Email
            </label>
            <input
              type="email"
              value={email}
              autoComplete="email"
              onChange={(e) => {
                setEmail(e.target.value);
                setEmailError("");
              }}
              placeholder="boiler@purdue.edu"
              className={`w-full px-5 py-4 rounded-2xl border-2 outline-none text-[16px] font-medium transition-colors bg-white ${
                emailError
                  ? "border-red-400 focus:border-red-500"
                  : "border-gray-200 focus:border-gray-900"
              }`}
            />
            {emailError && (
              <p className="text-red-500 text-[12px] font-bold mt-1.5">⚠ {emailError}</p>
            )}
            {email && !isPurdueEmail(email) && !emailError && (
              <p className="text-orange-500 text-[12px] font-bold mt-1.5">
                Must end in @purdue.edu
              </p>
            )}
          </div>

          {/* Password */}
          <div>
            <label className="block text-[11px] font-black text-gray-500 uppercase tracking-widest mb-2">
              Password
            </label>
            <div className="relative">
              <input
                type={showPw ? "text" : "password"}
                value={password}
                autoComplete="current-password"
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-5 py-4 pr-12 rounded-2xl border-2 border-gray-200 focus:border-gray-900 outline-none text-[16px] transition-colors bg-white"
              />
              <button
                type="button"
                onClick={() => setShowPw((v) => !v)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-700"
              >
                {showPw ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <motion.button
            type="submit"
            disabled={loading || !email || !password}
            whileTap={{ scale: 0.98 }}
            className="w-full bg-gray-900 text-white py-4 rounded-full font-black text-[17px] uppercase tracking-tight hover:bg-gray-800 transition-all disabled:opacity-40 mt-2"
          >
            {loading ? "Signing in…" : "Sign In"}
          </motion.button>
        </motion.form>

        {/* Divider */}
        <div className="flex items-center gap-4 my-8">
          <div className="flex-1 h-px bg-gray-200" />
          <span className="text-[12px] font-bold text-gray-400 uppercase">or</span>
          <div className="flex-1 h-px bg-gray-200" />
        </div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-center text-gray-500 font-medium"
        >
          New to Pic N Eat?{" "}
          <Link href="/onboarding/step1">
            <span className="font-black text-gray-900 underline underline-offset-2 cursor-pointer">
              Get started
            </span>
          </Link>
        </motion.p>
      </div>
    </div>
  );
}
