// Plan Reveal — shown after step 5
import { useEffect, useState } from "react";
import { useLocation } from "wouter";
import { motion } from "framer-motion";

interface Plan {
  name: string;
  target: number;
  bmr: number;
  tdee: number;
  protein: number;
  carbs: number;
  fats: number;
  goalLabel: string;
  timelineLabel: string;
}

const TIMELINE_MAP: Record<string, string> = {
  "2w": "2 weeks",
  "1m": "1 month",
  "3m": "3 months",
  "6m": "6 months",
  "1y":  "1 year",
};

const GOAL_MAP: Record<string, string> = {
  lose:     "Fat Loss",
  gain:     "Muscle Gain",
  maintain: "Maintenance",
  fit:      "Get Fit",
};

export default function OnboardingPlan() {
  const [, setLocation] = useLocation();
  const [plan, setPlan] = useState<Plan | null>(null);
  const [revealed, setRevealed] = useState(false);

  useEffect(() => {
    const p: Plan = {
      name:          localStorage.getItem("onboarding_name")       || "there",
      target:        parseInt(localStorage.getItem("user_target_calories") || "2000"),
      bmr:           parseInt(localStorage.getItem("user_bmr")             || "1600"),
      tdee:          parseInt(localStorage.getItem("user_tdee")            || "2000"),
      protein:       parseInt(localStorage.getItem("user_protein_target")  || "150"),
      carbs:         parseInt(localStorage.getItem("user_carbs_target")    || "200"),
      fats:          parseInt(localStorage.getItem("user_fats_target")     || "67"),
      goalLabel:     GOAL_MAP[localStorage.getItem("onboarding_goal") || "maintain"] ?? "Maintenance",
      timelineLabel: TIMELINE_MAP[localStorage.getItem("onboarding_timeline") || "3m"] ?? "3 months",
    };
    setPlan(p);
    setTimeout(() => setRevealed(true), 300);
  }, []);

  const handleStart = () => {
    localStorage.setItem("onboarding_completed", "true");
    setLocation("/");
  };

  if (!plan) return null;

  const first = plan.name.split(" ")[0];

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col">
      <div className="flex-1 max-w-md mx-auto w-full pt-12">
        {/* All 5 bars filled */}
        <div className="flex gap-1.5 mb-10">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          ))}
        </div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[13px] font-bold text-orange-500 uppercase tracking-widest mb-2">
            Your Plan
          </p>
          <h1 className="text-[38px] font-black font-display uppercase tracking-tighter leading-[0.92] mb-1">
            {first},<br />here's your<br />daily target
          </h1>
          <p className="text-gray-500 font-medium mb-8">
            {plan.goalLabel} plan · Goal in {plan.timelineLabel}
          </p>
        </motion.div>

        {/* Big calorie number — Cal AI style */}
        <motion.div
          initial={{ scale: 0.7, opacity: 0 }}
          animate={revealed ? { scale: 1, opacity: 1 } : {}}
          transition={{ type: "spring", stiffness: 280, damping: 22 }}
          className="mb-6 text-center"
        >
          <div className="inline-flex flex-col items-center bg-gray-900 text-white rounded-3xl px-12 py-8 shadow-2xl shadow-gray-900/20 w-full">
            <p className="text-[13px] font-black uppercase tracking-widest text-gray-400 mb-1">
              {plan.goalLabel}
            </p>
            <p className="text-[78px] font-black leading-none tracking-tighter">
              {plan.target.toLocaleString()}
            </p>
            <p className="text-[16px] font-bold text-orange-400 mt-1">calories / day</p>
          </div>
        </motion.div>

        {/* Macro breakdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={revealed ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.25 }}
          className="grid grid-cols-3 gap-3 mb-5"
        >
          {[
            { label: "Protein", value: plan.protein, color: "bg-blue-50 border-blue-200 text-blue-700" },
            { label: "Carbs",   value: plan.carbs,   color: "bg-orange-50 border-orange-200 text-orange-700" },
            { label: "Fats",    value: plan.fats,    color: "bg-yellow-50 border-yellow-200 text-yellow-700" },
          ].map((m) => (
            <div key={m.label} className={`rounded-2xl border-2 p-4 text-center ${m.color}`}>
              <p className="text-[30px] font-black leading-none">{m.value}</p>
              <p className="text-[10px] font-black uppercase tracking-widest mt-1">{m.label}</p>
              <p className="text-[10px] font-medium opacity-60">g / day</p>
            </div>
          ))}
        </motion.div>

        {/* BMR / TDEE / Target row */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={revealed ? { opacity: 1 } : {}}
          transition={{ delay: 0.45 }}
          className="flex bg-white rounded-2xl p-4 border border-gray-100 mb-6"
        >
          {[
            { label: "BMR",         val: plan.bmr,    accent: false },
            { label: "Maintenance", val: plan.tdee,   accent: false },
            { label: "Your Target", val: plan.target, accent: true  },
          ].map((row, i) => (
            <div key={row.label} className="flex-1 text-center">
              {i > 0 && <div className="absolute w-px h-8 bg-gray-100 -translate-x-1/2 mt-1" />}
              <p className={`text-[20px] font-black ${row.accent ? "text-orange-500" : ""}`}>
                {row.val.toLocaleString()}
              </p>
              <p className="text-[9px] font-black text-gray-400 uppercase tracking-widest leading-tight">
                {row.label}
              </p>
            </div>
          ))}
        </motion.div>
      </div>

      <motion.button
        initial={{ opacity: 0, y: 16 }}
        animate={revealed ? { opacity: 1, y: 0 } : {}}
        transition={{ delay: 0.6 }}
        onClick={handleStart}
        className="w-full max-w-md mx-auto bg-gray-900 text-white py-4 rounded-full font-black text-[17px] uppercase tracking-tight hover:bg-gray-800 transition-all active:scale-[0.98] shadow-xl shadow-gray-900/20"
      >
        🚀 Let's Go, {first}!
      </motion.button>
    </div>
  );
}
