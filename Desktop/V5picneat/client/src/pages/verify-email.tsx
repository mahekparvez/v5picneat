import { useRef, useState } from "react";
import { useLocation } from "wouter";
import { motion, AnimatePresence } from "framer-motion";
import { Mail } from "lucide-react";

export default function VerifyEmailPage() {
  const [, setLocation] = useLocation();
  const [digits, setDigits] = useState(["", "", "", "", "", ""]);
  const [verified, setVerified] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);
  const email = localStorage.getItem("user_email") || "your@purdue.edu";

  const handleChange = (i: number, val: string) => {
    if (!/^\d*$/.test(val)) return;
    const next = [...digits];
    next[i] = val.slice(-1);
    setDigits(next);
    if (val && i < 5) inputRefs.current[i + 1]?.focus();
  };

  const handleKeyDown = (i: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !digits[i] && i > 0) {
      inputRefs.current[i - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (pasted.length > 0) {
      const next = [...digits];
      pasted.split("").forEach((ch, idx) => { if (idx < 6) next[idx] = ch; });
      setDigits(next);
      inputRefs.current[Math.min(pasted.length, 5)]?.focus();
    }
    e.preventDefault();
  };

  const isComplete = digits.every((d) => d !== "");

  const handleVerify = () => {
    if (!isComplete) return;
    setVerified(true);
    setTimeout(() => {
      const done = localStorage.getItem("onboarding_completed") === "true";
      setLocation(done ? "/" : "/onboarding/step1");
    }, 1400);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col items-center justify-center">
      <div className="max-w-md w-full">
        <AnimatePresence mode="wait">
          {!verified ? (
            <motion.div
              key="form"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
            >
              {/* Icon */}
              <div className="w-16 h-16 bg-orange-100 rounded-2xl flex items-center justify-center mb-6 mx-auto">
                <Mail className="w-8 h-8 text-orange-500" />
              </div>

              <h1 className="text-[32px] font-black font-display uppercase tracking-tighter mb-2 text-center">
                Check your<br />Purdue email
              </h1>
              <p className="text-gray-500 text-center font-medium mb-1">
                We sent a 6-digit code to
              </p>
              <p className="text-center font-black text-gray-900 mb-8 text-[15px]">{email}</p>

              {/* OTP inputs */}
              <div className="flex gap-2 justify-center mb-8" onPaste={handlePaste}>
                {digits.map((digit, i) => (
                  <input
                    key={i}
                    ref={(el) => { inputRefs.current[i] = el; }}
                    id={`otp-${i}`}
                    type="text"
                    inputMode="numeric"
                    value={digit}
                    onChange={(e) => handleChange(i, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(i, e)}
                    maxLength={1}
                    className={`w-12 h-14 rounded-2xl border-2 outline-none text-[22px] font-black text-center bg-white transition-colors ${
                      digit ? "border-gray-900" : "border-gray-200 focus:border-gray-500"
                    }`}
                  />
                ))}
              </div>

              <button
                onClick={handleVerify}
                disabled={!isComplete}
                className="w-full bg-gray-900 text-white py-4 rounded-full font-black text-[17px] uppercase tracking-tight hover:bg-gray-800 transition-all disabled:opacity-40"
              >
                Verify Email
              </button>

              <button
                onClick={() => setLocation("/login")}
                className="w-full mt-3 py-3 text-gray-500 font-bold text-[14px] uppercase tracking-tight hover:text-gray-800 transition-colors"
              >
                ← Use a different email
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="success"
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="text-center"
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 300, damping: 20 }}
                className="text-7xl mb-6"
              >
                ✅
              </motion.div>
              <h1 className="text-[32px] font-black font-display uppercase tracking-tighter mb-2">
                Verified!
              </h1>
              <p className="text-gray-500 font-medium">Setting up your profile…</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
