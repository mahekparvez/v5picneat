import { Link } from 'wouter';
import { motion } from 'framer-motion';
import astronautRocket from "@assets/Eat_Page_1767000174644.png";

export default function WelcomePage() {
  return (
    <div className="min-h-screen bg-gray-50 p-6 flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute top-[-20%] right-[-20%] w-[500px] h-[500px] bg-orange-200/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-[-20%] left-[-20%] w-[500px] h-[500px] bg-blue-200/20 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-md w-full text-center relative z-10">
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="mb-12"
        >
          <div className="w-64 h-64 mx-auto relative mb-8">
            <img src={astronautRocket} alt="Astronaut riding rocket" className="w-full h-full object-contain drop-shadow-xl" />
          </div>
          
          <h1 className="text-[48px] font-black font-display uppercase leading-[0.9] mb-4 tracking-tighter text-black">
            Pic N Eat
          </h1>
          <p className="text-xl text-gray-500 font-bold tracking-tight px-8">
            Your AI-powered nutrition companion for Purdue dining
          </p>
        </motion.div>

        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
          className="space-y-4"
        >
          <Link href="/onboarding/gender">
            <button
              data-testid="button-get-started"
              className="w-full bg-gray-900 text-white py-4 rounded-full font-bold text-lg uppercase tracking-tight hover:bg-gray-800 transition-all shadow-lg active:scale-98"
            >
              Get Started
            </button>
          </Link>
          
          <Link href="/">
            <button
              data-testid="button-login"
              className="w-full bg-white text-gray-900 py-4 rounded-full font-bold text-lg uppercase tracking-tight hover:bg-gray-50 transition-all border-2 border-gray-200 active:scale-98"
            >
              I already have an account
            </button>
          </Link>
        </motion.div>
      </div>
    </div>
  );
}
