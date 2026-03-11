import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import NotFound from "@/pages/not-found";
import Home from "@/pages/home";
import Leaderboard from "@/pages/leaderboard";
import SearchPage from "@/pages/search";
import CameraPage from "@/pages/camera";
import WelcomePage from "@/pages/welcome";
import LoginPage from "@/pages/login";
import VerifyEmailPage from "@/pages/verify-email";
// New 5-step onboarding
import OnboardingStep1 from "@/pages/onboarding/step1";
import OnboardingStep2 from "@/pages/onboarding/step2";
import OnboardingStep3 from "@/pages/onboarding/step3";
import OnboardingStep4 from "@/pages/onboarding/step4";
import OnboardingStep5 from "@/pages/onboarding/step5";
import OnboardingPlan from "@/pages/onboarding/plan";
// Legacy onboarding (kept for backward compat)
import OnboardingGender from "@/pages/onboarding/gender";
import OnboardingWorkouts from "@/pages/onboarding/workouts";
import OnboardingGoals from "@/pages/onboarding/goals";
import OnboardingHeightWeight from "@/pages/onboarding/height-weight";
import OnboardingCalculate from "@/pages/onboarding/calculate";
import OnboardingComplete from "@/pages/onboarding/complete";

function Router() {
  return (
    <Switch>
      {/* Auth */}
      <Route path="/welcome" component={WelcomePage} />
      <Route path="/login" component={LoginPage} />
      <Route path="/verify-email" component={VerifyEmailPage} />

      {/* New 5-step onboarding */}
      <Route path="/onboarding/step1" component={OnboardingStep1} />
      <Route path="/onboarding/step2" component={OnboardingStep2} />
      <Route path="/onboarding/step3" component={OnboardingStep3} />
      <Route path="/onboarding/step4" component={OnboardingStep4} />
      <Route path="/onboarding/step5" component={OnboardingStep5} />
      <Route path="/onboarding/plan"  component={OnboardingPlan} />

      {/* Legacy onboarding routes */}
      <Route path="/onboarding/gender"       component={OnboardingGender} />
      <Route path="/onboarding/workouts"     component={OnboardingWorkouts} />
      <Route path="/onboarding/goals"        component={OnboardingGoals} />
      <Route path="/onboarding/height-weight" component={OnboardingHeightWeight} />
      <Route path="/onboarding/calculate"    component={OnboardingCalculate} />
      <Route path="/onboarding/complete"     component={OnboardingComplete} />

      {/* Main App */}
      <Route path="/" component={Home} />
      <Route path="/leaderboard" component={Leaderboard} />
      <Route path="/camera" component={CameraPage} />
      <Route path="/search" component={SearchPage} />

      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster />
      <Router />
    </QueryClientProvider>
  );
}

export default App;
