import { Link, useLocation } from "wouter";
import { Camera, Circle, Triangle, Search } from "lucide-react";
import { cn } from "@/lib/utils";

export default function BottomNav() {
  const [location] = useLocation();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-md border-t border-gray-100 pb-safe pt-2 px-6 z-50">
      <div className="flex items-center justify-between max-w-md mx-auto h-20">
        <Link href="/camera">
          <div className={cn("flex flex-col items-center gap-[4px] cursor-pointer transition-colors", location === "/camera" ? "text-blue-500" : "text-gray-400")}>
            <div className={cn("p-2 rounded-xl bg-gray-100 transition-all", location === "/camera" && "bg-blue-100")}>
               <div className="w-[26px] h-[26px] bg-blue-500 rotate-45 rounded-sm" /> 
            </div>
            <span className="text-[13px] font-bold uppercase tracking-tighter">Pic</span>
          </div>
        </Link>

        <Link href="/">
          <div className={cn("flex flex-col items-center gap-[4px] cursor-pointer transition-colors", location === "/" ? "text-gray-900" : "text-gray-400")}>
            <div className={cn("p-2 rounded-full bg-gray-100 transition-all", location === "/" && "bg-gray-200")}>
              <div className="w-[26px] h-[26px] bg-gray-900 rounded-full" />
            </div>
            <span className="text-[13px] font-bold uppercase tracking-tighter">Eat</span>
          </div>
        </Link>

        <Link href="/leaderboard">
          <div className={cn("flex flex-col items-center gap-[4px] cursor-pointer transition-colors", location === "/leaderboard" ? "text-gray-900" : "text-gray-400")}>
             <div className={cn("p-2 rounded-xl bg-gray-100 transition-all", location === "/leaderboard" && "bg-gray-200")}>
               <div className="w-0 h-0 border-l-[13px] border-l-transparent border-r-[13px] border-r-transparent border-b-[22px] border-b-gray-900" />
            </div>
            <span className="text-[13px] font-bold uppercase tracking-tighter">Lead</span>
          </div>
        </Link>

         <Link href="/search">
          <div className={cn("flex flex-col items-center gap-[4px] cursor-pointer transition-colors", location === "/search" ? "text-gray-900" : "text-gray-400")}>
            <div className={cn("p-2 rounded-full bg-gray-100 transition-all flex items-center justify-center", location === "/search" && "bg-gray-200")}>
              <Search className="w-[26px] h-[26px] text-gray-900" />
            </div>
            <span className="text-[13px] font-bold uppercase tracking-tighter">Find</span>
          </div>
        </Link>
      </div>
    </nav>
  );
}
