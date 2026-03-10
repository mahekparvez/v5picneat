import { useState } from 'react';
import { useLocation } from 'wouter';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';

export default function OnboardingWorkouts() {
  const [, setLocation] = useLocation();
  const [workouts, setWorkouts] = useState<number | null>(null);

  const workoutOptions = [
    { value: 0, label: 'None', emoji: '😴' },
    { value: 1, label: '1-2 times', emoji: '🏃' },
    { value: 3, label: '3-4 times', emoji: '💪' },
    { value: 5, label: '5+ times', emoji: '🔥' },
  ];

  const handleContinue = () => {
    if (workouts === null) return;
    localStorage.setItem('onboarding_workouts', workouts.toString());
    setLocation('/onboarding/goals');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col">
      <div className="flex-1 max-w-md mx-auto w-full pt-12">
        {/* Back button */}
        <button
          onClick={() => setLocation('/onboarding/gender')}
          className="mb-6 p-2 hover:bg-gray-100 rounded-full transition-all"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>

        {/* Progress bar */}
        <div className="flex gap-2 mb-8">
          <div className="flex-1 h-1 bg-gray-900 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-900 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-200 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-200 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-200 rounded-full"></div>
        </div>

        {/* Title */}
        <motion.h1
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-[35px] font-bold font-display uppercase mb-3 tracking-tighter"
        >
          How Many Workouts
        </motion.h1>
        
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-gray-600 mb-8 font-bold tracking-tight"
        >
          Do you do per week?
        </motion.p>

        {/* Options */}
        <div className="space-y-3">
          {workoutOptions.map((option, idx) => (
            <motion.button
              key={option.value}
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.1 * idx }}
              onClick={() => setWorkouts(option.value)}
              className={`w-full p-5 rounded-2xl border-2 transition-all text-left flex items-center gap-4 ${
                workouts === option.value
                  ? 'border-gray-900 bg-gray-100'
                  : 'border-gray-200 bg-white hover:border-gray-300'
              }`}
            >
              <span className="text-4xl">{option.emoji}</span>
              <span className="font-bold text-gray-900 uppercase tracking-tight">{option.label}</span>
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
        disabled={workouts === null}
        className="w-full max-w-md mx-auto bg-gray-900 text-white py-4 rounded-full font-bold text-lg uppercase tracking-tight hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-98"
      >
        Continue
      </motion.button>
    </div>
  );
}