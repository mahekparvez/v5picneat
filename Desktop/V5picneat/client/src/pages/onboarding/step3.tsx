// Step 3 of 5 — Goal
import { useState } from "react";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";

const GOALS = [
  {
    value: "lose",
    label: "Lose Weight",
    emoji: "📉",
    desc: "Reduce body fat with a calorie deficit",
  },
  {
    value: "maintain",
    label: "Maintain Weight",
    emoji: "⚖️",
    desc: "Stay at your current weight & improve composition",
  },
  {
    value: "gain",
    label: "Gain Muscle",
    emoji: "💪",
    desc: "Build strength and mass with a calorie surplus",
  },
  {
    value: "fit",
    label: "Get Fit",
    emoji: "🏃",
    desc: "Improve overall health & endurance",
  },
];

export default function OnboardingStep3() {
  const [, setLocation] = useLocation();
  const [goal, setGoal] = useState<string | null>(
    localStorage.getItem("onboarding_goal") || null
  );

  const handleContinue = () => {
    if (!goal) return;
    localStorage.setItem("onboarding_goal", goal);
    setLocation("/onboarding/step4");
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col">
      <div className="flex-1 max-w-md mx-auto w-full pt-12">
        <button
          onClick={() => setLocation("/onboarding/step2")}
          className="mb-6 p-2 hover:bg-gray-100 rounded-full transition-all"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>

        <div className="flex gap-1.5 mb-10">
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-200 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-200 rounded-full" />
        </div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[13px] font-bold text-orange-500 uppercase tracking-widest mb-2">
            Step 3 of 5
          </p>
          <h1 className="text-[38px] font-black font-display uppercase tracking-tighter leading-[0.92] mb-2">
            What's your<br />main goal?
          </h1>
          <p className="text-gray-500 font-medium mb-8">
            This shapes your entire calorie & macro plan
          </p>
        </motion.div>

        <div className="space-y-3">
          {GOALS.map((g, idx) => (
            <motion.button
              key={g.value}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.05 * idx }}
              onClick={() => setGoal(g.value)}
              className={cn(
                "w-full p-5 rounded-2xl border-2 flex items-center gap-4 text-left transition-all",
                goal === g.value
                  ? "border-gray-900 bg-gray-900 text-white"
                  : "border-gray-200 bg-white hover:border-gray-300"
              )}
            >
              <span className="text-4xl shrink-0">{g.emoji}</span>
              <div>
                <p className="font-black text-[15px] uppercase tracking-tight">{g.label}</p>
                <p
                  className={cn(
                    "text-[13px] font-medium mt-0.5",
                    goal === g.value ? "text-gray-300" : "text-gray-500"
                  )}
                >
                  {g.desc}
                </p>
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      <motion.button
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        onClick={handleContinue}
        disabled={!goal}
        className="w-full max-w-md mx-auto bg-gray-900 text-white py-4 rounded-full font-black text-[17px] uppercase tracking-tight hover:bg-gray-800 transition-all disabled:opacity-40 active:scale-[0.98] mt-6"
      >
        Continue →
      </motion.button>
    </div>
  );
}
