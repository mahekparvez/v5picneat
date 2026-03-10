import { useState } from 'react';
import { useLocation } from 'wouter';
import { motion } from 'framer-motion';

export default function OnboardingGender() {
  const [, setLocation] = useLocation();
  const [gender, setGender] = useState<string | null>(null);

  const genders = [
    { value: 'male', label: 'Male', emoji: '👨' },
    { value: 'female', label: 'Female', emoji: '👩' },
    { value: 'non-binary', label: 'Non-binary', emoji: '🧑' },
    { value: 'prefer-not-to-say', label: 'Prefer not to say', emoji: '😊' },
  ];

  const handleContinue = () => {
    if (!gender) return;
    localStorage.setItem('onboarding_gender', gender);
    setLocation('/onboarding/workouts');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col">
      <div className="flex-1 max-w-md mx-auto w-full pt-12">
        {/* Progress bar */}
        <div className="flex gap-2 mb-8">
          <div className="flex-1 h-1 bg-gray-900 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-200 rounded-full"></div>
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
          Choose Your Gender
        </motion.h1>
        
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-gray-600 mb-8 font-bold tracking-tight"
        >
          Help us personalize your experience
        </motion.p>

        {/* Options */}
        <div className="space-y-3">
          {genders.map((option, idx) => (
            <motion.button
              key={option.value}
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: 0.1 * idx }}
              onClick={() => setGender(option.value)}
              className={`w-full p-5 rounded-2xl border-2 transition-all text-left flex items-center gap-4 ${
                gender === option.value
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
        disabled={!gender}
        className="w-full max-w-md mx-auto bg-gray-900 text-white py-4 rounded-full font-bold text-lg uppercase tracking-tight hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-98"
      >
        Continue
      </motion.button>
    </div>
  );
}
