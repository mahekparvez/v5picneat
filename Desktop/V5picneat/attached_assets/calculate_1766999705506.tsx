import { useEffect } from 'react';
import { useLocation } from 'wouter';

export default function OnboardingCalculate() {
  const [, setLocation] = useLocation();

  useEffect(() => {
    calculateAndSave();
  }, []);

  const calculateAndSave = () => {
    // Get stored data
    const gender = localStorage.getItem('onboarding_gender') || 'male';
    const workouts = parseInt(localStorage.getItem('onboarding_workouts') || '0');
    const heightStr = localStorage.getItem('onboarding_height') || '5ft 10in';
    const weightStr = localStorage.getItem('onboarding_weight') || '165lbs';
    const goal = localStorage.getItem('onboarding_goal') || 'maintain';

    // Parse height (convert to cm)
    let heightCm = 175;
    if (heightStr.includes('ft')) {
      const [ftStr, inStr] = heightStr.split(' ');
      const feet = parseInt(ftStr) || 5;
      const inches = parseInt(inStr) || 10;
      heightCm = (feet * 12 + inches) * 2.54;
    } else {
      heightCm = parseInt(heightStr) || 175;
    }

    // Parse weight (convert to kg)
    let weightKg = 75;
    if (weightStr.includes('lbs')) {
      const lbs = parseInt(weightStr) || 165;
      weightKg = lbs * 0.453592;
    } else {
      weightKg = parseInt(weightStr) || 75;
    }

    // Assume age 25 for now
    const age = 25;

    // Calculate BMR using Mifflin-St Jeor Equation
    let calculatedBMR = 0;
    if (gender === 'male') {
      calculatedBMR = (10 * weightKg) + (6.25 * heightCm) - (5 * age) + 5;
    } else {
      calculatedBMR = (10 * weightKg) + (6.25 * heightCm) - (5 * age) - 161;
    }

    // Determine activity multiplier based on workouts
    let multiplier = 1.2;
    if (workouts === 0) {
      multiplier = 1.2;
    } else if (workouts === 1) {
      multiplier = 1.375;
    } else if (workouts === 3) {
      multiplier = 1.55;
    } else if (workouts === 5) {
      multiplier = 1.725;
    }

    // Calculate TDEE
    const calculatedTDEE = calculatedBMR * multiplier;

    // Calculate target calories based on goal
    let target = calculatedTDEE;
    if (goal === 'lose') {
      target = calculatedTDEE - 500;
    } else if (goal === 'gain') {
      target = calculatedTDEE + 300;
    }

    // Save calculated values
    const finalBMR = Math.round(calculatedBMR);
    const finalTDEE = Math.round(calculatedTDEE);
    const finalTarget = Math.round(target);

    localStorage.setItem('user_bmr', finalBMR.toString());
    localStorage.setItem('user_tdee', finalTDEE.toString());
    localStorage.setItem('user_target_calories', finalTarget.toString());
    localStorage.setItem('nutrition_goal', finalTarget.toString());

    // Navigate to complete page
    setTimeout(() => {
      setLocation('/onboarding/complete');
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-gray-900 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-xl font-bold font-display uppercase tracking-tight">Calculating...</p>
      </div>
    </div>
  );
}