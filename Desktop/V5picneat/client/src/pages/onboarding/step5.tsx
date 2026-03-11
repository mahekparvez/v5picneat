// Step 5 of 5 — Activity Level → auto-calculates then shows plan
import { useState } from "react";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";

const ACTIVITIES = [
  { value: "1.2",   label: "Sedentary",      desc: "Desk job, little to no exercise", emoji: "🛋️" },
  { value: "1.375", label: "Lightly Active",  desc: "Light exercise 1–2 days/week",    emoji: "🚶" },
  { value: "1.55",  label: "Moderately Active", desc: "Exercise 3–5 days/week",        emoji: "🏃" },
  { value: "1.725", label: "Very Active",     desc: "Hard training 6–7 days/week",     emoji: "⚡" },
];

function calcAndSave() {
  const sex        = localStorage.getItem("onboarding_sex")      || "male";
  const age        = parseInt(localStorage.getItem("onboarding_age")    || "20");
  const actMul     = parseFloat(localStorage.getItem("onboarding_activity") || "1.375");
  const goal       = localStorage.getItem("onboarding_goal")     || "maintain";
  const paceStr    = localStorage.getItem("onboarding_pace")     || "500";
  const pace       = parseInt(paceStr);
  const heightStr  = localStorage.getItem("onboarding_height")   || "5ft 10in";
  const weightStr  = localStorage.getItem("onboarding_weight")   || "165lbs";

  // Parse height → cm
  let heightCm = 175;
  if (heightStr.includes("ft")) {
    const [ftPart, inPart] = heightStr.split(" ");
    heightCm = (parseInt(ftPart) * 12 + parseInt(inPart)) * 2.54;
  } else {
    heightCm = parseInt(heightStr) || 175;
  }

  // Parse weight → kg
  let weightKg = 75;
  if (weightStr.includes("lbs")) {
    weightKg = parseInt(weightStr) * 0.453592;
  } else {
    weightKg = parseInt(weightStr) || 75;
  }

  // Mifflin-St Jeor BMR
  const bmr = sex === "male"
    ? 10 * weightKg + 6.25 * heightCm - 5 * age + 5
    : 10 * weightKg + 6.25 * heightCm - 5 * age - 161;

  const tdee = bmr * actMul;

  // Apply goal deficit/surplus
  let target = tdee;
  if (goal === "lose") target = tdee - pace;
  else if (goal === "gain") target = tdee + pace;
  else if (goal === "fit") target = tdee - 250; // modest deficit for fit

  const t = Math.max(Math.round(target), 1200); // never below 1200

  // Macro split: 30% protein, 40% carbs, 30% fats
  const protein = Math.round(t * 0.30 / 4);
  const carbs   = Math.round(t * 0.40 / 4);
  const fats    = Math.round(t * 0.30 / 9);

  localStorage.setItem("user_bmr",             Math.round(bmr).toString());
  localStorage.setItem("user_tdee",            Math.round(tdee).toString());
  localStorage.setItem("user_target_calories", t.toString());
  localStorage.setItem("user_protein_target",  protein.toString());
  localStorage.setItem("user_carbs_target",    carbs.toString());
  localStorage.setItem("user_fats_target",     fats.toString());
}

export default function OnboardingStep5() {
  const [, setLocation] = useLocation();
  const [activity, setActivity] = useState<string | null>(
    localStorage.getItem("onboarding_activity") || null
  );

  const handleContinue = () => {
    if (!activity) return;
    localStorage.setItem("onboarding_activity", activity);
    calcAndSave();
    setLocation("/onboarding/plan");
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col">
      <div className="flex-1 max-w-md mx-auto w-full pt-12">
        <button
          onClick={() => setLocation("/onboarding/step4")}
          className="mb-6 p-2 hover:bg-gray-100 rounded-full transition-all"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>

        <div className="flex gap-1.5 mb-10">
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
        </div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[13px] font-bold text-orange-500 uppercase tracking-widest mb-2">
            Step 5 of 5
          </p>
          <h1 className="text-[38px] font-black font-display uppercase tracking-tighter leading-[0.92] mb-2">
            How active<br />are you?
          </h1>
          <p className="text-gray-500 font-medium mb-8">
            Activity level fine-tunes your total daily calorie burn
          </p>
        </motion.div>

        <div className="space-y-3">
          {ACTIVITIES.map((a, idx) => (
            <motion.button
              key={a.value}
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.06 * idx }}
              onClick={() => setActivity(a.value)}
              className={cn(
                "w-full p-5 rounded-2xl border-2 flex items-center gap-4 text-left transition-all",
                activity === a.value
                  ? "border-gray-900 bg-gray-900 text-white"
                  : "border-gray-200 bg-white hover:border-gray-300"
              )}
            >
              <span className="text-4xl shrink-0">{a.emoji}</span>
              <div className="flex-1">
                <p className="font-black text-[15px] uppercase tracking-tight">{a.label}</p>
                <p
                  className={cn(
                    "text-[13px] font-medium mt-0.5",
                    activity === a.value ? "text-gray-300" : "text-gray-500"
                  )}
                >
                  {a.desc}
                </p>
              </div>
              <div
                className={cn(
                  "w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0",
                  activity === a.value ? "border-white bg-white" : "border-gray-300"
                )}
              >
                {activity === a.value && (
                  <div className="w-2.5 h-2.5 rounded-full bg-gray-900" />
                )}
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      <motion.button
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.35 }}
        onClick={handleContinue}
        disabled={!activity}
        className="w-full max-w-md mx-auto bg-orange-500 text-white py-4 rounded-full font-black text-[17px] uppercase tracking-tight hover:bg-orange-600 transition-all disabled:opacity-40 active:scale-[0.98] mt-6 shadow-lg shadow-orange-200"
      >
        Build My Plan 🚀
      </motion.button>
    </div>
  );
}
