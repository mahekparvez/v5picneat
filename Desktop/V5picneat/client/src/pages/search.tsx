import { motion } from "framer-motion";
import Layout from "@/components/layout";
import { Search } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

const CATEGORIES = [
  { name: "Protein", color: "bg-blue-100 text-blue-700 border-blue-200" },
  { name: "Carbs", color: "bg-orange-100 text-orange-700 border-orange-200" },
  { name: "Vitamins", color: "bg-purple-100 text-purple-700 border-purple-200" },
  { name: "Minerals", color: "bg-green-100 text-green-700 border-green-200" },
  { name: "Fats", color: "bg-yellow-100 text-yellow-700 border-yellow-200" },
];

const DINING_COURTS = [
  { name: "Wiley Dining Court", distance: "0.2 mi", categories: ["Protein", "Carbs", "Vitamins"] },
  { name: "Earhart Dining Court", distance: "0.5 mi", categories: ["Protein", "Fats", "Minerals"] },
  { name: "Ford Dining Court", distance: "0.8 mi", categories: ["Carbs", "Vitamins", "Minerals"] },
  { name: "Hillenbrand", distance: "1.2 mi", categories: ["Protein", "Carbs", "Fats", "Vitamins", "Minerals"] },
  { name: "Windsor Dining", distance: "1.5 mi", categories: ["Protein", "Minerals"] },
];

export default function SearchPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const filteredCourts = DINING_COURTS.filter(court => 
    selectedCategory ? court.categories.includes(selectedCategory) : false
  );

  return (
    <Layout>
      <div className="px-6 pt-16 pb-6 h-full flex flex-col">
        <div className="mb-6">
          <h1 className="text-[32px] font-bold text-gray-900 leading-tight tracking-tight mb-1">
            Find Nutrient-Rich Foods
          </h1>
          <p className="text-[18px] text-gray-500 font-medium">What are you looking for today?</p>
        </div>

        <div className="flex gap-3 overflow-x-auto no-scrollbar mb-[46px] -mx-6 px-6">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.name}
              onClick={() => setSelectedCategory(selectedCategory === cat.name ? null : cat.name)}
              className={cn(
                "px-6 py-3 rounded-2xl text-[14px] font-bold uppercase border transition-all whitespace-nowrap",
                selectedCategory === cat.name 
                  ? "bg-gray-900 text-white border-gray-900" 
                  : `${cat.color} opacity-80 hover:opacity-100`
              )}
            >
              {cat.name}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto no-scrollbar pb-24">
          {selectedCategory ? (
            <div className="space-y-4">
              {filteredCourts.map((court, i) => (
                <motion.div 
                  key={court.name}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="bg-[#f0f2f5] rounded-3xl p-6 shadow-sm"
                >
                  <h3 className="font-bold font-display uppercase text-[20px] mb-1 tracking-tighter">{court.name}</h3>
                  <p className="text-sm font-bold text-gray-500 mb-4 uppercase tracking-tight">{court.distance}</p>
                  <div className="flex flex-wrap gap-2">
                    {court.categories.map(catName => (
                      <div key={catName} className={cn("px-4 py-1.5 rounded-full text-[11px] font-black uppercase border tracking-tighter", CATEGORIES.find(c => c.name === catName)?.color)}>
                        {catName}
                      </div>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full py-12">
              <Search className="w-16 h-16 text-gray-600 mb-4" />
              <p className="text-[18px] font-bold text-gray-600 text-center px-12">
                Select a nutrient above to find foods
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
