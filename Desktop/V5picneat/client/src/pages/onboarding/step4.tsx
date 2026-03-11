// Step 4 of 5 — Timeline & Pace
import { useState } from "react";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";

const TIMELINES = [
  { value: "2w",  label: "2 Weeks",   emoji: "⚡", desc: "Sprint mode" },
  { value: "1m",  label: "1 Month",   emoji: "📅", desc: "Short burst" },
  { value: "3m",  label: "3 Months",  emoji: "🎯", desc: "Recommended" },
  { value: "6m",  label: "6 Months",  emoji: "📈", desc: "Sustainable" },
  { value: "1y",  label: "1 Year",    emoji: "🏆", desc: "Long-term" },
];

// Cal adjust per day based on pace
const PACES = [
  { value: "250",  label: "Gradual",     desc: "–250 cal/day · Easy & sustainable", emoji: "🐢" },
  { value: "500",  label: "Steady",      desc: "–500 cal/day · ~1 lb/week",          emoji: "🚶" },
  { value: "750",  label: "Aggressive",  desc: "–750 cal/day · Fast results",         emoji: "🔥" },
];

// Surplus paces for gain
const GAIN_PACES = [
  { value: "150",  label: "Lean Bulk",   desc: "+150 cal/day · Minimal fat gain",   emoji: "🌱" },
  { value: "300",  label: "Classic Bulk", desc: "+300 cal/day · Steady gains",       emoji: "💪" },
  { value: "500",  label: "Aggressive",  desc: "+500 cal/day · Maximum growth",     emoji: "🚀" },
];

export default function OnboardingStep4() {
  const [, setLocation] = useLocation();
  const goal = localStorage.getItem("onboarding_goal") || "maintain";
  const [timeline, setTimeline] = useState<string | null>(
    localStorage.getItem("onboarding_timeline") || null
  );
  const [pace, setPace] = useState<string | null>(
    localStorage.getItem("onboarding_pace") || null
  );

  const needsPace = goal === "lose" || goal === "gain";
  const isValid = timeline !== null && (!needsPace || pace !== null);
  const paceOptions = goal === "gain" ? GAIN_PACES : PACES;

  const goalLabel =
    goal === "lose" ? "weight loss" : goal === "gain" ? "muscle gain" : "your goal";

  const handleContinue = () => {
    if (!isValid) return;
    localStorage.setItem("onboarding_timeline", timeline!);
    if (pace) localStorage.setItem("onboarding_pace", pace);
    setLocation("/onboarding/step5");
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col overflow-y-auto">
      <div className="flex-1 max-w-md mx-auto w-full pt-12">
        <button
          onClick={() => setLocation("/onboarding/step3")}
          className="mb-6 p-2 hover:bg-gray-100 rounded-full transition-all"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>

        <div className="flex gap-1.5 mb-10">
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-200 rounded-full" />
        </div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[13px] font-bold text-orange-500 uppercase tracking-widest mb-2">
            Step 4 of 5
          </p>
          <h1 className="text-[38px] font-black font-display uppercase tracking-tighter leading-[0.92] mb-2">
            Timeline &amp;<br />pace
          </h1>
          <p className="text-gray-500 font-medium mb-8">
            When do you want to reach {goalLabel}?
          </p>
        </motion.div>

        {/* Timeline */}
        <div className="mb-8">
          <label className="block text-[11px] font-black text-gray-500 uppercase tracking-widest mb-3">
            Goal timeline
          </label>
          <div className="grid grid-cols-3 gap-2">
            {TIMELINES.map((t, idx) => (
              <motion.button
                key={t.value}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.04 * idx }}
                onClick={() => setTimeline(t.value)}
                className={cn(
                  "p-4 rounded-2xl border-2 flex flex-col items-center gap-1 transition-all",
                  timeline === t.value
                    ? "border-gray-900 bg-gray-900 text-white"
                    : "border-gray-200 bg-white hover:border-gray-400"
                )}
              >
                <span className="text-2xl">{t.emoji}</span>
                <span className="font-black text-[13px] uppercase tracking-tight">
                  {t.label}
                </span>
                <span
                  className={cn(
                    "text-[10px] font-medium",
                    timeline === t.value ? "text-gray-300" : "text-gray-400"
                  )}
                >
                  {t.desc}
                </span>
              </motion.button>
            ))}
          </div>
        </div>

        {/* Pace — only for lose/gain */}
        {needsPace && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-8"
          >
            <label className="block text-[11px] font-black text-gray-500 uppercase tracking-widest mb-3">
              Speed / pace
            </label>
            <div className="space-y-2">
              {paceOptions.map((p) => (
                <button
                  key={p.value}
                  onClick={() => setPace(p.value)}
                  className={cn(
                    "w-full p-4 rounded-2xl border-2 flex items-center gap-4 text-left transition-all",
                    pace === p.value
                      ? "border-gray-900 bg-gray-900 text-white"
                      : "border-gray-200 bg-white hover:border-gray-300"
                  )}
                >
                  <span className="text-3xl shrink-0">{p.emoji}</span>
                  <div className="flex-1">
                    <p className="font-black text-[14px] uppercase tracking-tight">{p.label}</p>
                    <p
                      className={cn(
                        "text-[12px] font-medium",
                        pace === p.value ? "text-gray-300" : "text-gray-500"
                      )}
                    >
                      {p.desc}
                    </p>
                  </div>
                  <div
                    className={cn(
                      "w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0",
                      pace === p.value ? "border-white bg-white" : "border-gray-300"
                    )}
                  >
                    {pace === p.value && (
                      <div className="w-2.5 h-2.5 rounded-full bg-gray-900" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </div>

      <motion.button
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        onClick={handleContinue}
        disabled={!isValid}
        className="w-full max-w-md mx-auto bg-gray-900 text-white py-4 rounded-full font-black text-[17px] uppercase tracking-tight hover:bg-gray-800 transition-all disabled:opacity-40 active:scale-[0.98] mt-4"
      >
        Continue →
      </motion.button>
    </div>
  );
}
