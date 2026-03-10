import { motion, AnimatePresence } from "framer-motion";
import Layout from "@/components/layout";
import { MapPin, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { useState, useEffect, useCallback } from "react";
import { cn } from "@/lib/utils";

const API_BASE = import.meta.env.VITE_PICNEAT_API || "http://localhost:8000";

// ── Types ──────────────────────────────────────────────────────────────────────
interface MenuItem {
  name: string;
  meal: string;
  station: string;
  serving: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  categories: string[];
}

interface DiningHall {
  hall: string;
  lat: number;
  lng: number;
  categories: string[];
  items: MenuItem[];
  distanceMi?: number;
}

interface MenuResponse {
  date: string;
  total: number;
  halls: DiningHall[];
}

// ── Category config ────────────────────────────────────────────────────────────
const CATEGORIES = [
  { name: "Protein",    color: "bg-blue-100   text-blue-700   border-blue-200",   icon: "🍗" },
  { name: "Carbs",      color: "bg-orange-100 text-orange-700 border-orange-200", icon: "🌾" },
  { name: "Fats",       color: "bg-yellow-100 text-yellow-700 border-yellow-200", icon: "🔥" },
  { name: "Minerals",   color: "bg-green-100  text-green-700  border-green-200",  icon: "🥛" },
  { name: "Vitamin A",  color: "bg-red-100    text-red-700    border-red-200",    icon: "🥕" },
  { name: "Vitamin C",  color: "bg-orange-100 text-orange-600 border-orange-200", icon: "🍊" },
  { name: "Vitamin D",  color: "bg-yellow-100 text-yellow-600 border-yellow-200", icon: "☀️" },
  { name: "Vitamin B",  color: "bg-purple-100 text-purple-700 border-purple-200", icon: "🌾" },
  { name: "Vitamin B12",color: "bg-pink-100   text-pink-700   border-pink-200",   icon: "🥩" },
];

// ── Meal period helper ─────────────────────────────────────────────────────────
type MealPeriod = "Breakfast" | "Lunch" | "Dinner" | "All";

function getCurrentMealPeriod(): MealPeriod {
  const h = new Date().getHours();
  if (h >= 7 && h < 11)  return "Breakfast";
  if (h >= 11 && h < 15) return "Lunch";
  if (h >= 15 && h < 21) return "Dinner";
  return "All";
}

function mealLabel(period: MealPeriod): string {
  if (period === "All") return "Today's menu";
  return `${period} menu`;
}

function itemMatchesPeriod(item: MenuItem, period: MealPeriod): boolean {
  if (period === "All") return true;
  return item.meal.toLowerCase().includes(period.toLowerCase());
}

// ── Nutrient value label for selected category ─────────────────────────────────
function nutrientLabel(item: MenuItem, category: string | null): string {
  switch (category) {
    case "Protein": return `${item.protein}g / serving`;
    case "Carbs":   return `${item.carbs}g / serving`;
    case "Fats":    return `${item.fats}g / serving`;
    default:        return item.serving ? `${item.serving} / serving` : "— / serving";
  }
}

// ── Haversine distance (miles) ─────────────────────────────────────────────────
function haversine(lat1: number, lng1: number, lat2: number, lng2: number) {
  const R = 3958.8;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLng = ((lng2 - lng1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// ── Component ──────────────────────────────────────────────────────────────────
export default function SearchPage() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [halls, setHalls] = useState<DiningHall[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userPos, setUserPos] = useState<{ lat: number; lng: number } | null>(null);
  const [expandedHall, setExpandedHall] = useState<string | null>(null);
  const [menuDate, setMenuDate] = useState("");
  const [mealPeriod] = useState<MealPeriod>(getCurrentMealPeriod);

  // Ask for location once on mount
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => setUserPos({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => {}
      );
    }
  }, []);

  const fetchMenu = useCallback(async (category: string | null) => {
    setLoading(true);
    setError(null);
    setExpandedHall(null);
    try {
      const params = new URLSearchParams();
      if (category) params.set("category", category);
      const resp = await fetch(`${API_BASE}/dining-menu?${params}`);
      if (!resp.ok) throw new Error(`Server error ${resp.status}`);
      const data: MenuResponse = await resp.json();
      setMenuDate(data.date);

      const enriched = data.halls.map((h) => ({
        ...h,
        distanceMi: userPos
          ? haversine(userPos.lat, userPos.lng, h.lat, h.lng)
          : undefined,
      }));

      enriched.sort((a, b) =>
        a.distanceMi !== undefined && b.distanceMi !== undefined
          ? a.distanceMi - b.distanceMi
          : a.hall.localeCompare(b.hall)
      );

      setHalls(enriched);
      // Auto-expand the first hall
      if (enriched.length > 0) setExpandedHall(enriched[0].hall);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load menu");
    } finally {
      setLoading(false);
    }
  }, [userPos]);

  useEffect(() => {
    if (selectedCategory !== null) {
      void fetchMenu(selectedCategory);
    } else {
      setHalls([]);
      setMenuDate("");
    }
  }, [selectedCategory, fetchMenu]);

  return (
    <Layout>
      <div className="px-6 pt-16 pb-6 h-full flex flex-col">

        {/* Header — all text starts at the same left edge */}
        <div className="mb-5">
          <h1 className="text-[32px] font-bold text-gray-900 leading-tight tracking-tight mb-0.5">
            Find Nutrient-Rich Foods
          </h1>
          <div className="flex items-center gap-1.5 overflow-hidden whitespace-nowrap">
            <span className="text-[14px] text-gray-500 font-medium truncate">
              {mealLabel(mealPeriod)}{menuDate ? ` · ${menuDate}` : ""}
            </span>
            <span className="text-gray-300 shrink-0">·</span>
            {userPos ? (
              <span className="flex items-center gap-0.5 text-[13px] text-green-600 font-semibold shrink-0">
                <MapPin size={12} /> Near you
              </span>
            ) : (
              <button
                onClick={() =>
                  navigator.geolocation?.getCurrentPosition(
                    (p) => setUserPos({ lat: p.coords.latitude, lng: p.coords.longitude }),
                    () => {}
                  )
                }
                className="flex items-center gap-0.5 text-[13px] text-orange-500 font-semibold underline underline-offset-2 shrink-0"
              >
                <MapPin size={12} /> Enable location
              </button>
            )}
          </div>
        </div>

        {/* Category chips */}
        <div className="flex gap-3 overflow-x-auto no-scrollbar mb-6 -mx-6 px-6">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.name}
              onClick={() =>
                setSelectedCategory(selectedCategory === cat.name ? null : cat.name)
              }
              className={cn(
                "px-5 py-2.5 rounded-2xl text-[13px] font-bold uppercase border transition-all whitespace-nowrap flex items-center gap-1.5",
                selectedCategory === cat.name
                  ? "bg-gray-900 text-white border-gray-900"
                  : `${cat.color} opacity-80 hover:opacity-100`
              )}
            >
              <span>{cat.icon}</span> {cat.name}
            </button>
          ))}
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto no-scrollbar pb-24">

          {/* Idle */}
          {!selectedCategory && !loading && (
            <div className="flex flex-col items-center justify-center h-full py-12 gap-4">
              <p className="text-[18px] font-bold text-gray-400 text-center">
                Pick a nutrient above to see what's on at each dining hall
              </p>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-20 gap-3">
              <Loader2 className="w-10 h-10 text-orange-500 animate-spin" />
              <p className="text-gray-500 font-semibold">Loading today's menu…</p>
            </div>
          )}

          {/* Error */}
          {error && !loading && (
            <div className="bg-red-50 border border-red-200 rounded-2xl p-5 text-center">
              <p className="font-bold text-red-600 mb-1">Couldn't load menu</p>
              <p className="text-sm text-red-500 mb-3">{error}</p>
              <button
                onClick={() => void fetchMenu(selectedCategory)}
                className="px-5 py-2 bg-red-500 text-white font-bold rounded-full text-sm"
              >
                Retry
              </button>
            </div>
          )}

          {/* Hall accordion list */}
          {!loading && !error && halls.length > 0 && (
            <div className="space-y-1">
              {halls.map((hall, i) => {
                const isOpen = expandedHall === hall.hall;

                // Filter by selected category AND current meal period
                const filteredItems = hall.items.filter(
                  (item) =>
                    (!selectedCategory || item.categories.includes(selectedCategory)) &&
                    itemMatchesPeriod(item, mealPeriod)
                );

                if (filteredItems.length === 0) return null;

                return (
                  <motion.div
                    key={hall.hall}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.04 }}
                  >
                    {/* ── Dining court name row — tappable, aligned flush left ── */}
                    <button
                      onClick={() => setExpandedHall(isOpen ? null : hall.hall)}
                      className="w-full flex items-center justify-between py-3 group"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-[22px] font-black font-display uppercase tracking-tighter text-gray-900 group-hover:text-orange-500 transition-colors">
                          {hall.hall}
                        </span>
                        {hall.distanceMi !== undefined && (
                          <span className="text-[12px] font-bold text-gray-400 uppercase tracking-tight flex items-center gap-0.5">
                            <MapPin size={11} />
                            {hall.distanceMi < 0.1 ? "Here" : `${hall.distanceMi.toFixed(1)} mi`}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-[12px] font-bold text-gray-400 uppercase">
                          {filteredItems.length} {filteredItems.length === 1 ? "item" : "items"}
                        </span>
                        {isOpen
                          ? <ChevronUp size={18} className="text-gray-400" />
                          : <ChevronDown size={18} className="text-gray-400" />
                        }
                      </div>
                    </button>

                    {/* Divider */}
                    <div className="h-px bg-gray-200 mb-1" />

                    {/* ── Dropdown food list ── */}
                    <AnimatePresence initial={false}>
                      {isOpen && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.2, ease: "easeInOut" }}
                          className="overflow-hidden"
                        >
                          <div className="pb-4 space-y-0">
                            {filteredItems.map((item, idx) => (
                              <div
                                key={item.name + idx}
                                className="flex items-baseline justify-between py-2.5 border-b border-gray-100 last:border-0"
                              >
                                {/* Food name — aligned with hall name */}
                                <div className="flex-1 min-w-0 pr-4">
                                  <p className="text-[15px] font-semibold text-gray-900 truncate">
                                    {item.name}
                                  </p>
                                  {item.station && (
                                    <p className="text-[12px] text-gray-400 uppercase tracking-tight">
                                      {item.station}
                                    </p>
                                  )}
                                </div>
                                {/* Nutrient amount for selected category */}
                                <span className="text-[13px] font-bold text-gray-500 shrink-0 whitespace-nowrap">
                                  {nutrientLabel(item, selectedCategory)}
                                </span>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                );
              })}
            </div>
          )}

          {/* No results */}
          {!loading && !error && selectedCategory && halls.length > 0 &&
            halls.every((h) =>
              h.items.filter(
                (item) =>
                  item.categories.includes(selectedCategory!) &&
                  itemMatchesPeriod(item, mealPeriod)
              ).length === 0
            ) && (
            <p className="text-center text-[17px] font-bold text-gray-400 py-16 px-8">
              No {selectedCategory} options for {mealPeriod === "All" ? "today" : mealPeriod.toLowerCase()} yet
            </p>
          )}
        </div>
      </div>
    </Layout>
  );
}
