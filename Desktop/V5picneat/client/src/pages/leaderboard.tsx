import { motion } from "framer-motion";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis, ReferenceLine } from "recharts";
import Layout from "@/components/layout";
import astronautCape from "@assets/Astronaut-cartoon-illustration-vector_1766637602817.png";
import planetsRow from "@assets/image_1766761255761.png";
import superAstronaut from "@assets/image_1766761677744.png";

const data = [
  { name: '0', calories: 1500 },
  { name: '5', calories: 1500 },
  { name: '10', calories: 2800 },
  { name: '15', calories: 1800 },
  { name: '20', calories: 2400 },
  { name: '25', calories: 1200 },
  { name: '30', calories: 1980 },
];

const CustomCursor = (props: any) => {
  const { cx, cy } = props;
  if (!cx || !cy) return null;
  return (
    <g>
      <image 
        href={astronautCape} 
        x={cx - 25} 
        y={cy - 50} 
        width="50" 
        height="50" 
        className="drop-shadow-lg"
      />
    </g>
  );
};

export default function Leaderboard() {
  return (
    <Layout>
      <div className="px-6 pt-12 pb-6 relative overflow-hidden">
        {/* Hero Illustration Background */}
        <div className="absolute -right-16 top-0 w-64 h-64 pointer-events-none opacity-40 blur-[1px] -z-10">
          <img src={superAstronaut} alt="Hero Astronaut" className="w-full h-full object-contain mix-blend-multiply" />
        </div>

        {/* Mission & Chart Section */}
        <div className="mb-4 relative">
          <div className="flex items-center justify-between">
            <h1 className="text-[31px] font-bold font-display uppercase mb-1 tracking-tighter">Mission Number: 1</h1>
            <div className="flex items-center gap-1 relative -top-[1px]">
              <span className="text-[31px] font-bold font-display uppercase leading-none">2</span>
              <span className="text-2xl leading-none">⭐</span>
            </div>
          </div>
           <p className="text-[18px] font-bold mb-4 uppercase tracking-tight">Miles: 60</p>
           
           <div className="h-64 w-full bg-orange-50/50 rounded-2xl mb-4 relative overflow-hidden border border-orange-100">
             <ResponsiveContainer width="100%" height="100%">
               <AreaChart data={data} margin={{ top: 60, right: 15, left: 15, bottom: 25 }}>
                 <defs>
                   <linearGradient id="colorCals" x1="0" y1="0" x2="0" y2="1">
                     <stop offset="5%" stopColor="#e67e22" stopOpacity={0.15}/>
                     <stop offset="95%" stopColor="#e67e22" stopOpacity={0}/>
                   </linearGradient>
                 </defs>
                 <XAxis 
                   dataKey="name" 
                   axisLine={false} 
                   tickLine={false} 
                   label={{ value: 'Days', position: 'insideBottom', offset: -15, fontSize: 14, fontWeight: '900' }}
                   tick={{fontSize: 11, fill: '#9ca3af', fontWeight: '900'}} 
                 />
                 <YAxis 
                   axisLine={false} 
                   tickLine={false} 
                   tick={(props) => {
                     const { x, y, payload } = props;
                     if (payload.value === 0) return <></>;
                     return (
                       <text x={x} y={y} dy={4} textAnchor="end" fontSize={11} fill="#9ca3af" fontWeight="900">
                         {payload.value}
                       </text>
                     );
                   }}
                   domain={[0, 3000]} 
                   ticks={[0, 1000, 2000, 3000]}
                   label={{ value: 'Calories', angle: -90, position: 'insideLeft', fontSize: 14, fontWeight: '900', offset: 0 }}
                 />
                 <Tooltip 
                   cursor={<CustomCursor />} 
                   content={<div className="bg-white/90 backdrop-blur px-2 py-1 rounded shadow-sm text-[10px] font-bold border border-orange-100">{`Cals: ${data[0].calories}`}</div>}
                   position={{ y: 0 }}
                 />
                 <ReferenceLine y={1800} stroke="#ff4d4d" strokeDasharray="3 3" />
                 <Area type="monotone" dataKey="calories" stroke="#e67e22" strokeWidth={3} fillOpacity={1} fill="url(#colorCals)" />
               </AreaChart>
             </ResponsiveContainer>
           </div>
        </div>

        {/* Mission Stats */}
        <div className="mb-8">
          <h3 className="font-display font-bold text-lg mb-3 uppercase tracking-tighter">Mission</h3>
          <div className="bg-lime-100/80 rounded-2xl p-4 flex items-center gap-4 border-2 border-lime-300/50 shadow-sm">
             <div className="w-16 h-16 flex items-center justify-center shrink-0">
               <span className="text-4xl">⭐</span>
             </div>
             <div className="font-bold text-sm text-gray-900 uppercase tracking-tight">
               1 Mission | 100mi | 7 Days Streak
             </div>
          </div>
        </div>

        {/* Badges */}
        <div className="mb-8">
          <h3 className="font-display font-bold text-lg mb-4 uppercase tracking-tighter">Badges</h3>
          <div className="flex justify-between items-center gap-2">
            {[
              { name: 'Moon', miles: '100 mi', pos: '0%' },
              { name: 'Mercury', miles: '200 mi', pos: '25%' },
              { name: 'Venus', miles: '300 mi', pos: '50%' },
              { name: 'Jupiter', miles: '400 mi', pos: '75%' },
              { name: 'Uranus', miles: '500 mi', pos: '100%' }
            ].map((planet) => (
              <div key={planet.name} className="flex flex-col items-center gap-1 shrink-0 flex-1">
                 <div className="text-sm font-black text-gray-400 uppercase tracking-tighter text-center">{planet.name}</div>
                 <div className="w-16 h-16 rounded-full shadow-lg border-2 border-white bg-white flex items-center justify-center overflow-hidden">
                    <div className="w-16 h-16 shrink-0 rounded-full scale-[1.3]" style={{ backgroundImage: `url(${planetsRow})`, backgroundSize: '500% 100%', backgroundPosition: planet.pos }} />
                 </div>
                 <div className="text-sm font-black text-gray-900 mt-1 uppercase tracking-tighter text-center">{planet.miles}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Leaderboard */}
        <div className="pb-24">
           <h3 className="font-display font-bold text-lg mb-4 uppercase tracking-tighter">Leaderboard</h3>
           <div className="space-y-1">
             {[
               { name: "NAME", days: 16, pos: '25%' },
               { name: "NAME", days: 6, pos: '0%' },
               { name: "NAME", days: 3, pos: '0%' },
               { name: "NAME", days: 2, pos: '50%' },
               { name: "NAME", days: 1, pos: '75%' }
             ].map((user, i) => (
               <div key={i} className="flex items-center justify-between bg-gray-200/60 p-3 rounded-xl">
                 <div className="flex items-center gap-4">
                   <div className="w-12 h-12 rounded-full border-2 border-white shadow-md bg-white flex items-center justify-center overflow-hidden">
                      <div className="w-12 h-12 shrink-0 rounded-full scale-[1.3]" style={{ backgroundImage: `url(${planetsRow})`, backgroundSize: '500% 100%', backgroundPosition: user.pos }} />
                   </div>
                   <span className="font-black font-display uppercase tracking-widest text-gray-900 text-sm">{user.name}</span>
                 </div>
                 <span className="font-black text-sm text-gray-900 uppercase tracking-tight">{user.days} Days</span>
               </div>
             ))}
           </div>
        </div>

      </div>
    </Layout>
  );
}
