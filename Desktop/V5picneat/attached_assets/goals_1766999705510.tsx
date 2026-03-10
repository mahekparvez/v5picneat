import { useState } from 'react';
import { useLocation } from 'wouter';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';

export default function OnboardingGoals() {
  const [, setLocation] = useLocation();
  const [goal, setGoal] = useState<string | null>(null);

  const goalOptions = [
    { value: 'lose', label: 'Lose Weight', emoji: '📉', desc: 'Shed those extra pounds' },
    { value: 'maintain', label: 'Maintain', emoji: '⚖️', desc: 'Stay at your current weight' },
    { value: 'gain', label: 'Gain Muscle', emoji: '💪', desc: 'Build strength & mass' },
    { value: 'fit', label: 'Get Fit', emoji: '🏃', desc: 'Improve overall health' },
  ];

  const handleContinue = () => {
    if (!goal) return;
    localStorage.setItem('onboarding_goal', goal);
    setLocation('/onboarding/height-weight');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col">
      <div className="flex-1 max-w-md mx-auto w-full pt-12">
        {/* Back button */}
        <button
          onClick={() => setLocation('/onboarding/workouts')}
          className="mb-6 p-2 hover:bg-gray-100 rounded-full transition-all"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>

        {/* Progress bar */}
        <div className="flex gap-2 mb-8">
          <div className="flex-1 h-1 bg-gray-900 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-900 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-900 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-200 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-200 rounded-full"></div>
        </div>

        {/* Title */}
        <motion.h1
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-[35px] font-bold font-display uppercase mb-3 tracking-tighter"
        >
          What Is Your Goal?
        </motion.h1>
        
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-gray-600 mb-8 font-bold tracking-tight"
        >
          Choose what matters most to you
        </motion.p>

        {/* Options */}
        <div className="space-y-3">
          {goalOptions.map((option, idx) => (
            <motion.button
              key={option.value}
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.1 * idx }}
              onClick={() => setGoal(option.value)}
              className={`w-full p-5 rounded-2xl border-2 transition-all text-left ${
                goal === option.value
                  ? 'border-gray-900 bg-gray-100'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-4">
                <span className="text-4xl">{option.emoji}</span>
                <div className="flex-1">
                  <p className="font-bold text-gray-900 uppercase tracking-tight mb-1">{option.label}</p>
                  <p className="text-sm text-gray-600">{option.desc}</p>
                </div>
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Continue button */}
      <motion.button
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
        onClick={handleContinue}
        disabled={!goal}
        className="w-full max-w-md mx-auto bg-gray-900 text-white py-4 rounded-full font-bold text-lg uppercase tracking-tight hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-98"
      >
        Continue
      </motion.button>
    </div>
  );
}