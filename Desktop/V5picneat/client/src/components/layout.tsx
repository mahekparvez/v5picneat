import { ReactNode } from "react";
import BottomNav from "./bottom-nav";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50 pb-24 font-sans max-w-md mx-auto relative overflow-hidden shadow-2xl">
      {children}
      <BottomNav />
    </div>
  );
}
