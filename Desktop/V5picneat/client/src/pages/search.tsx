import { motion } from "framer-motion";
import Layout from "@/components/layout";
import { Search, MapPin, Loader2, ChevronDown, ChevronUp } from "lucide-react";
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
  { name: "Protein",   color: "bg-blue-100   text-blue-700   border-blue-200",   icon: "🍗" },
  { name: "Carbs",     color: "bg-orange-100 text-orange-700 border-orange-200", icon: "🌾" },
  { name: "Vitamins",  color: "bg-purple-100 text-purple-700 border-purple-200", icon: "🥦" },
  { name: "Minerals",  color: "bg-green-100  text-green-700  border-green-200",  icon: "🥛" },
  { name: "Fats",      color: "bg-yellow-100 text-yellow-700 border-yellow-200", icon: "🔥" },
];

// ── Haversine distance (miles) ─────────────────────────────────────────────────
function distanceMi(lat1: number, lng1: number, lat2: number, lng2: number) {
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
  const [locationAsked, setLocationAsked] = useState(false);
  const [expandedHall, setExpandedHall] = useState<string | null>(null);
  const [menuDate, setMenuDate] = useState("");

  // Ask for location once on mount
  useEffect(() => {
    if (!locationAsked && navigator.geolocation) {
      setLocationAsked(true);
      navigator.geolocation.getCurrentPosition(
        (pos) => setUserPos({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
        () => {} // silently ignore denial
      );
    }
  }, [locationAsked]);

  // Fetch menu whenever category or userPos changes
  const fetchMenu = useCallback(async (category: string | null) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (category) params.set("category", category);
      const resp = await fetch(`${API_BASE}/dining-menu?${params}`);
      if (!resp.ok) throw new Error(`Server error ${resp.status}`);
      const data: MenuResponse = await resp.json();
      setMenuDate(data.date);

      // Attach distance if we have user location
      const enriched = data.halls.map((h) => ({
        ...h,
        distanceMi: userPos
          ? distanceMi(userPos.lat, userPos.lng, h.lat, h.lng)
          : undefined,
      }));

      // Sort by distance if available, else alphabetically
      enriched.sort((a, b) =>
        a.distanceMi !== undefined && b.distanceMi !== undefined
          ? a.distanceMi - b.distanceMi
          : a.hall.localeCompare(b.hall)
      );
      setHalls(enriched);
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
    }
  }, [selectedCategory, fetchMenu]);

  const catConfig = (name: string) =>
    CATEGORIES.find((c) => c.name === name) ?? CATEGORIES[0];

  return (
    <Layout>
      <div className="px-6 pt-16 pb-6 h-full flex flex-col">
        {/* Header */}
        <div className="mb-5">
          <h1 className="text-[32px] font-bold text-gray-900 leading-tight tracking-tight mb-1">
            Find Nutrient-Rich Foods
          </h1>
          <div className="flex items-center gap-2 flex-wrap">
            <p className="text-[17px] text-gray-500 font-medium">What are you looking for today?</p>
            {userPos ? (
              <span className="flex items-center gap-1 text-[13px] text-green-600 font-semibold">
                <MapPin size={13} /> Near you
              </span>
            ) : (
              <button
                onClick={() => {
                  if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                      (pos) => setUserPos({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
                      () => setError("Location denied — distances won't be shown.")
                    );
                  }
                }}
                className="flex items-center gap-1 text-[13px] text-orange-500 font-semibold underline underline-offset-2"
              >
                <MapPin size={13} /> Enable location
              </button>
            )}
          </div>
          {menuDate && (
            <p className="text-[12px] text-gray-400 font-medium mt-1 uppercase tracking-tight">
              Menu for {menuDate}
            </p>
          )}
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
          {/* Idle state */}
          {!selectedCategory && !loading && (
            <div className="flex flex-col items-center justify-center h-full py-12">
              <Search className="w-16 h-16 text-gray-300 mb-4" />
              <p className="text-[18px] font-bold text-gray-500 text-center px-12">
                Pick a nutrient above to see what's on at each dining hall today
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

          {/* Hall cards */}
          {!loading && !error && halls.length > 0 && (
            <div className="space-y-4">
              {halls.map((hall, i) => {
                const isOpen = expandedHall === hall.hall;
                const filteredItems = hall.items.filter((item) =>
                  selectedCategory ? item.categories.includes(selectedCategory) : true
                );
                const visibleItems = isOpen ? filteredItems : filteredItems.slice(0, 5);

                return (
                  <motion.div
                    key={hall.hall}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="bg-[#f0f2f5] rounded-3xl p-5 shadow-sm"
                  >
                    {/* Hall header */}
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-bold font-display uppercase text-[19px] tracking-tighter leading-tight">
                          {hall.hall}
                        </h3>
                        {hall.distanceMi !== undefined && (
                          <p className="text-[12px] font-bold text-gray-400 uppercase tracking-tight flex items-center gap-1 mt-0.5">
                            <MapPin size={11} />
                            {hall.distanceMi < 0.1
                              ? "You're here!"
                              : `${hall.distanceMi.toFixed(1)} mi away`}
                          </p>
                        )}
                      </div>
                      {/* Nutrition category badges */}
                      <div className="flex flex-wrap gap-1 justify-end max-w-[140px]">
                        {hall.categories.map((cat) => (
                          <span
                            key={cat}
                            className={cn(
                              "px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase border tracking-tighter",
                              catConfig(cat).color,
                              selectedCategory === cat ? "ring-2 ring-gray-700" : ""
                            )}
                          >
                            {cat}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Food items */}
                    <div className="space-y-1.5">
                      {visibleItems.map((item) => (
                        <div
                          key={item.name + item.station}
                          className="bg-white rounded-2xl px-4 py-3 flex justify-between items-center"
                        >
                          <div className="flex-1 min-w-0">
                            <p className="font-bold text-gray-900 text-[13px] uppercase tracking-tight truncate">
                              {item.name}
                            </p>
                            {(item.station || item.meal) && (
                              <p className="text-[11px] text-gray-400 uppercase tracking-tight">
                                {[item.station, item.meal].filter(Boolean).join(" · ")}
                              </p>
                            )}
                          </div>
                          <div className="flex gap-2 text-[12px] font-bold shrink-0 ml-3">
                            <span className="text-orange-500">{Math.round(item.calories)} cal</span>
                            {item.protein > 0 && (
                              <span className="text-blue-500">P {item.protein}g</span>
                            )}
                          </div>
                        </div>
                      ))}

                      {/* Show more / less */}
                      {filteredItems.length > 5 && (
                        <button
                          onClick={() => setExpandedHall(isOpen ? null : hall.hall)}
                          className="w-full flex items-center justify-center gap-1 py-2 text-[12px] font-bold text-gray-500 uppercase tracking-tight"
                        >
                          {isOpen ? (
                            <>Show less <ChevronUp size={14} /></>
                          ) : (
                            <>Show all {filteredItems.length} items <ChevronDown size={14} /></>
                          )}
                        </button>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}

          {/* No results */}
          {!loading && !error && selectedCategory && halls.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 gap-3">
              <p className="text-[18px] font-bold text-gray-400 text-center">
                No {selectedCategory} options found today
              </p>
              <p className="text-sm text-gray-400 text-center px-8">
                The backend may be offline or the dining menu hasn't been posted yet.
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
