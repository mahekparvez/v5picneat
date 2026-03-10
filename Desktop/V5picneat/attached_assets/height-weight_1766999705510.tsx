import { useState } from 'react';
import { useLocation } from 'wouter';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';

export default function OnboardingHeightWeight() {
  const [, setLocation] = useLocation();
  const [unit, setUnit] = useState<'imperial' | 'metric'>('imperial');
  const [feet, setFeet] = useState('');
  const [inches, setInches] = useState('');
  const [cm, setCm] = useState('');
  const [weight, setWeight] = useState('');

  const handleContinue = () => {
    const heightValue = unit === 'imperial' ? `${feet}ft ${inches}in` : `${cm}cm`;
    const weightValue = unit === 'imperial' ? `${weight}lbs` : `${weight}kg`;
    
    localStorage.setItem('onboarding_height', heightValue);
    localStorage.setItem('onboarding_weight', weightValue);
    setLocation('/onboarding/calculate');
  };

  const isValid = unit === 'imperial' 
    ? feet && inches && weight
    : cm && weight;

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col">
      <div className="flex-1 max-w-md mx-auto w-full pt-12">
        {/* Back button */}
        <button
          onClick={() => setLocation('/onboarding/goals')}
          className="mb-6 p-2 hover:bg-gray-100 rounded-full transition-all"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>

        {/* Progress bar */}
        <div className="flex gap-2 mb-8">
          <div className="flex-1 h-1 bg-gray-900 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-900 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-900 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-900 rounded-full"></div>
          <div className="flex-1 h-1 bg-gray-200 rounded-full"></div>
        </div>

        {/* Title */}
        <motion.h1
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-[35px] font-bold font-display uppercase mb-3 tracking-tighter"
        >
          Height & Weight
        </motion.h1>
        
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="text-gray-600 mb-8 font-bold tracking-tight"
        >
          Tell us about your current stats
        </motion.p>

        {/* Unit toggle */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setUnit('imperial')}
            className={`flex-1 py-3 rounded-full font-bold uppercase tracking-tight transition-all ${
              unit === 'imperial'
                ? 'bg-gray-900 text-white'
                : 'bg-gray-200 text-gray-600'
            }`}
          >
            Imperial
          </button>
          <button
            onClick={() => setUnit('metric')}
            className={`flex-1 py-3 rounded-full font-bold uppercase tracking-tight transition-all ${
              unit === 'metric'
                ? 'bg-gray-900 text-white'
                : 'bg-gray-200 text-gray-600'
            }`}
          >
            Metric
          </button>
        </div>

        {/* Height input */}
        <div className="mb-6">
          <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-tight">
            Height
          </label>
          {unit === 'imperial' ? (
            <div className="flex gap-3">
              <input
                type="number"
                value={feet}
                onChange={(e) => setFeet(e.target.value)}
                placeholder="5"
                className="flex-1 px-4 py-4 rounded-2xl border-2 border-gray-900 focus:outline-none transition-all font-medium text-center"
              />
              <span className="flex items-center font-bold">ft</span>
              <input
                type="number"
                value={inches}
                onChange={(e) => setInches(e.target.value)}
                placeholder="10"
                className="flex-1 px-4 py-4 rounded-2xl border-2 border-gray-900 focus:outline-none transition-all font-medium text-center"
              />
              <span className="flex items-center font-bold">in</span>
            </div>
          ) : (
            <div className="flex gap-3">
              <input
                type="number"
                value={cm}
                onChange={(e) => setCm(e.target.value)}
                placeholder="175"
                className="flex-1 px-4 py-4 rounded-2xl border-2 border-gray-900 focus:outline-none transition-all font-medium text-center"
              />
              <span className="flex items-center font-bold">cm</span>
            </div>
          )}
        </div>

        {/* Weight input */}
        <div className="mb-6">
          <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-tight">
            Weight
          </label>
          <div className="flex gap-3">
            <input
              type="number"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              placeholder={unit === 'imperial' ? '165' : '75'}
              className="flex-1 px-4 py-4 rounded-2xl border-2 border-gray-900 focus:outline-none transition-all font-medium text-center"
            />
            <span className="flex items-center font-bold">{unit === 'imperial' ? 'lbs' : 'kg'}</span>
          </div>
        </div>
      </div>

      {/* Continue button */}
      <motion.button
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4 }}
        onClick={handleContinue}
        disabled={!isValid}
        className="w-full max-w-md mx-auto bg-gray-900 text-white py-4 rounded-full font-bold text-lg uppercase tracking-tight hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-98"
      >
        Continue
      </motion.button>
    </div>
  );
}