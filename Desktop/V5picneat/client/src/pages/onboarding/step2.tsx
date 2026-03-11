// Step 2 of 5 — Age, Height & Weight
import { useState } from "react";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";

export default function OnboardingStep2() {
  const [, setLocation] = useLocation();
  const [unit, setUnit] = useState<"imperial" | "metric">("imperial");
  const [age, setAge] = useState(localStorage.getItem("onboarding_age") || "");
  const [feet, setFeet] = useState("");
  const [inches, setInches] = useState("");
  const [cm, setCm] = useState("");
  const [weight, setWeight] = useState("");

  const heightOk = unit === "imperial" ? feet && inches : cm;
  const isValid = !!(age && parseInt(age) >= 10 && parseInt(age) <= 99 && heightOk && weight);

  const handleContinue = () => {
    if (!isValid) return;
    const heightValue = unit === "imperial" ? `${feet}ft ${inches}in` : `${cm}cm`;
    const weightValue = unit === "imperial" ? `${weight}lbs` : `${weight}kg`;
    localStorage.setItem("onboarding_age", age);
    localStorage.setItem("onboarding_height", heightValue);
    localStorage.setItem("onboarding_weight", weightValue);
    setLocation("/onboarding/step3");
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col">
      <div className="flex-1 max-w-md mx-auto w-full pt-12">
        <button
          onClick={() => setLocation("/onboarding/step1")}
          className="mb-6 p-2 hover:bg-gray-100 rounded-full transition-all"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>

        <div className="flex gap-1.5 mb-10">
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-900 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-200 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-200 rounded-full" />
          <div className="flex-1 h-1.5 bg-gray-200 rounded-full" />
        </div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <p className="text-[13px] font-bold text-orange-500 uppercase tracking-widest mb-2">
            Step 2 of 5
          </p>
          <h1 className="text-[38px] font-black font-display uppercase tracking-tighter leading-[0.92] mb-2">
            Your stats
          </h1>
          <p className="text-gray-500 font-medium mb-8">
            Used to calculate your BMR &amp; calorie needs
          </p>
        </motion.div>

        {/* Unit toggle */}
        <div className="flex gap-2 mb-6">
          {(["imperial", "metric"] as const).map((u) => (
            <button
              key={u}
              onClick={() => setUnit(u)}
              className={`flex-1 py-2.5 rounded-full font-black uppercase tracking-tight text-[13px] transition-all ${
                unit === u ? "bg-gray-900 text-white" : "bg-gray-200 text-gray-600"
              }`}
            >
              {u}
            </button>
          ))}
        </div>

        {/* Age */}
        <div className="mb-6">
          <label className="block text-[11px] font-black text-gray-500 uppercase tracking-widest mb-2">
            Age
          </label>
          <div className="flex items-center gap-3">
            <input
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="20"
              min="10"
              max="99"
              className="w-28 px-4 py-4 rounded-2xl border-2 border-gray-200 focus:border-gray-900 outline-none text-[22px] font-black text-center bg-white transition-colors"
            />
            <span className="text-gray-500 font-bold text-[16px]">years old</span>
          </div>
        </div>

        {/* Height */}
        <div className="mb-6">
          <label className="block text-[11px] font-black text-gray-500 uppercase tracking-widest mb-2">
            Height
          </label>
          {unit === "imperial" ? (
            <div className="flex gap-2 items-center">
              <input
                type="number"
                value={feet}
                onChange={(e) => setFeet(e.target.value)}
                placeholder="5"
                className="w-20 px-3 py-4 rounded-2xl border-2 border-gray-200 focus:border-gray-900 outline-none text-[20px] font-black text-center bg-white"
              />
              <span className="font-bold text-gray-500 text-[16px]">ft</span>
              <input
                type="number"
                value={inches}
                onChange={(e) => setInches(e.target.value)}
                placeholder="10"
                className="w-20 px-3 py-4 rounded-2xl border-2 border-gray-200 focus:border-gray-900 outline-none text-[20px] font-black text-center bg-white"
              />
              <span className="font-bold text-gray-500 text-[16px]">in</span>
            </div>
          ) : (
            <div className="flex gap-2 items-center">
              <input
                type="number"
                value={cm}
                onChange={(e) => setCm(e.target.value)}
                placeholder="175"
                className="w-28 px-4 py-4 rounded-2xl border-2 border-gray-200 focus:border-gray-900 outline-none text-[20px] font-black text-center bg-white"
              />
              <span className="font-bold text-gray-500 text-[16px]">cm</span>
            </div>
          )}
        </div>

        {/* Weight */}
        <div className="mb-8">
          <label className="block text-[11px] font-black text-gray-500 uppercase tracking-widest mb-2">
            Current weight
          </label>
          <div className="flex gap-2 items-center">
            <input
              type="number"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              placeholder={unit === "imperial" ? "165" : "75"}
              className="w-28 px-4 py-4 rounded-2xl border-2 border-gray-200 focus:border-gray-900 outline-none text-[20px] font-black text-center bg-white"
            />
            <span className="font-bold text-gray-500 text-[16px]">
              {unit === "imperial" ? "lbs" : "kg"}
            </span>
          </div>
        </div>
      </div>

      <motion.button
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        onClick={handleContinue}
        disabled={!isValid}
        className="w-full max-w-md mx-auto bg-gray-900 text-white py-4 rounded-full font-black text-[17px] uppercase tracking-tight hover:bg-gray-800 transition-all disabled:opacity-40 active:scale-[0.98] mt-4"
      >
        Continue →
      </motion.button>
    </div>
  );
}
