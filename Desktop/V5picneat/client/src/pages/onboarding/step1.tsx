// Step 1 of 5 — Name & Sex
import { useState } from "react";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";

export default function OnboardingStep1() {
  const [, setLocation] = useLocation();
  const [name, setName] = useState(localStorage.getItem("onboarding_name") || "");
  const [sex, setSex] = useState<"male" | "female" | null>(
    (localStorage.getItem("onboarding_sex") as "male" | "female") || null
  );

  const isValid = name.trim().length > 0 && sex !== null;

  const handleContinue = () => {
    if (!isValid) return;
    localStorage.setItem("onboarding_name", name.trim());
    localStorage.setItem("onboarding_sex", sex!);
    setLocation("/onboarding/step2");
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col">
      <div className="flex-1 max-w-md mx-auto w-full pt-12">
        <button
          onClick={() => setLocation("/welcome")}
          className="mb-6 p-2 hover:bg-gray-100 rounded-full transition-all"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>

        {/* 5-bar progress */}
        <div className="flex gap-1.5 mb-10">
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-200 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-200 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-200 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-200 rounded-full" />
        </div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[13px] font-bold text-orange-500 uppercase tracking-widest mb-2">
            Step 1 of 5
          </p>
          <h1 className="text-[38px] font-black font-display uppercase tracking-tighter leading-[0.92] mb-2">
            Let's get<br />to know you
          </h1>
          <p className="text-gray-500 font-medium mb-10">
            We'll personalise your calorie plan around you
          </p>
        </motion.div>

        {/* Name */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <label className="block text-[11px] font-black text-gray-500 uppercase tracking-widest mb-2">
            First name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Alex"
            className="w-full px-5 py-4 rounded-2xl border-2 border-gray-200 focus:border-gray-900 outline-none text-[18px] font-bold transition-colors bg-white"
          />
        </motion.div>

        {/* Sex */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
        >
          <label className="block text-[11px] font-black text-gray-500 uppercase tracking-widest mb-3">
            Biological sex
          </label>
          <div className="grid grid-cols-2 gap-4">
            {(["male", "female"] as const).map((s) => (
              <button
                key={s}
                onClick={() => setSex(s)}
                className={`py-10 rounded-3xl border-2 font-black uppercase tracking-tight text-[16px] transition-all flex flex-col items-center gap-3 ${
                  sex === s
                    ? "border-gray-900 bg-gray-900 text-white"
                    : "border-gray-200 bg-white text-gray-700 hover:border-gray-400"
                }`}
              >
                <span className="text-5xl">{s === "male" ? "♂" : "♀"}</span>
                {s === "male" ? "Male" : "Female"}
              </button>
            ))}
          </div>
        </motion.div>
      </div>

      <motion.button
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
        onClick={handleContinue}
        disabled={!isValid}
        className="w-full max-w-md mx-auto bg-gray-900 text-white py-4 rounded-full font-black text-[17px] uppercase tracking-tight hover:bg-gray-800 transition-all disabled:opacity-40 active:scale-[0.98] mt-6"
      >
        Continue →
      </motion.button>
    </div>
  );
}
