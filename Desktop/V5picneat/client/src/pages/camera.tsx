import { useState, useRef, useEffect } from "react";
import Layout from "@/components/layout";
import { X, Zap, Check, X as CloseIcon, Loader2, Camera, Upload } from "lucide-react";
import { cn } from "@/lib/utils";
import { useLocation } from "wouter";

const API_BASE = import.meta.env.VITE_PICNEAT_API || "http://localhost:8000";

interface PredictionResult {
  food_name: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  confidence: number;
  foods?: { name: string; portion_grams: number; calories: number; protein: number; carbs: number; fats: number; confidence: number; source: string }[];
}

interface MealAnalysisResponse {
  foods: { name: string; portion_grams: number; calories: number; protein: number; carbs: number; fats: number; confidence: number; source: string }[];
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fats: number;
  analysis_time_ms: number;
}

export default function CameraPage() {
  const [, setLocation] = useLocation();
  const [hasPhoto, setHasPhoto] = useState(false);
  const [photoData, setPhotoData] = useState<string | null>(null);
  const [flashActive, setFlashActive] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [cameraReady, setCameraReady] = useState(false);

  useEffect(() => {
    let stream: MediaStream | null = null;
    async function setupCamera() {
      setCameraError(null);
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment' },
          audio: false,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setCameraReady(true);
        }
      } catch (err) {
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false,
          });
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
            setCameraReady(true);
          }
        } catch (err2) {
          const msg = err instanceof Error ? err.message : String(err);
          setCameraError(
            msg.includes('Permission') || msg.includes('NotAllowed')
              ? 'Camera permission denied. Use "Upload photo" below.'
              : 'Camera not available. Use "Upload photo" to analyze a picture.'
          );
          setCameraReady(false);
        }
      }
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setCameraError('Camera not supported in this browser. Use "Upload photo" instead.');
    } else {
      setupCamera();
    }
    return () => {
      if (stream) stream.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const takePicture = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext('2d');
      if (context) {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.9);
        setPhotoData(dataUrl);
        setHasPhoto(true);
        setPrediction(null);
        void runAnalysis(dataUrl);
      }
    }
  };

  const runAnalysis = async (dataUrl: string) => {
    setAnalyzing(true);
    setAnalysisError(null);
    try {
      const blob = await (await fetch(dataUrl)).blob();
      const form = new FormData();
      form.append('file', blob, 'food.jpg');
      const response = await fetch(`${API_BASE}/analyze-meal`, {
        method: 'POST',
        body: form,
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        const detail = (data && typeof data.detail === 'string') ? data.detail : data.detail?.join?.(' ') || `Server error ${response.status}`;
        throw new Error(detail);
      }
      const first = (data as MealAnalysisResponse).foods?.[0];
      setPrediction({
        food_name: (data as MealAnalysisResponse).foods?.length > 1 ? 'Meal' : (first?.name ?? 'Food'),
        calories: (data as MealAnalysisResponse).total_calories,
        protein: Math.round((data as MealAnalysisResponse).total_protein * 10) / 10,
        carbs: Math.round((data as MealAnalysisResponse).total_carbs * 10) / 10,
        fats: Math.round((data as MealAnalysisResponse).total_fats * 10) / 10,
        confidence: first ? Math.round(first.confidence * 100) : 0,
        foods: (data as MealAnalysisResponse).foods,
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error('Analysis error:', err);
      setAnalysisError(message);
      setPrediction({
        food_name: 'Could not analyze',
        calories: 0,
        protein: 0,
        carbs: 0,
        fats: 0,
        confidence: 0,
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const logMeal = () => {
    if (!prediction) return;
    
    const newMeal = {
      id: Date.now(),
      image: photoData,
      name: prediction.food_name,
      calories: prediction.calories,
      protein: prediction.protein,
      carbs: prediction.carbs,
      fats: prediction.fats,
      timestamp: new Date().toISOString()
    };

    const saved = localStorage.getItem('logged_meals');
    const meals = saved ? JSON.parse(saved) : [];
    localStorage.setItem('logged_meals', JSON.stringify([...meals, newMeal]));
    
    setLocation("/");
  };

  const toggleFlash = () => {
    setFlashActive(!flashActive);
  };

  const retake = () => {
    setHasPhoto(false);
    setPhotoData(null);
    setPrediction(null);
    setAnalysisError(null);
  };

  const handleFilePick = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !file.type.startsWith('image/')) return;
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setPhotoData(dataUrl);
      setHasPhoto(true);
      setPrediction(null);
      void runAnalysis(dataUrl);
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  return (
    <Layout>
      <div className="min-h-screen bg-black relative overflow-hidden">
        {flashActive && !hasPhoto && (
          <div className="absolute inset-0 bg-white/20 z-10 pointer-events-none animate-pulse" />
        )}

        <div className="absolute inset-0 flex items-center justify-center">
          {hasPhoto ? (
            <img src={photoData!} className="w-full h-full object-cover" alt="Captured" />
          ) : (
            <>
              <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover" />
              {cameraError && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 p-6 text-center z-10">
                  <Camera className="w-12 h-12 text-amber-400 mb-3 opacity-80" />
                  <p className="text-white font-medium mb-1">Camera unavailable</p>
                  <p className="text-white/80 text-sm mb-6 max-w-xs">{cameraError}</p>
                  <p className="text-white/60 text-xs mb-4">Upload a food photo to analyze it:</p>
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center gap-2 px-6 py-3 bg-orange-500 text-white font-bold rounded-full shadow-lg"
                  >
                    <Upload size={20} />
                    Upload photo
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        {/* Analyzing overlay */}
        {analyzing && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="bg-white/95 rounded-2xl px-8 py-6 flex flex-col items-center gap-3 shadow-xl">
              <Loader2 className="w-10 h-10 text-orange-500 animate-spin" />
              <p className="font-bold text-gray-800">Neil is analyzing...</p>
              <p className="text-sm text-gray-500">Calories & macros in a sec</p>
            </div>
          </div>
        )}

        {/* Error from backend */}
        {analysisError && (
          <div className="absolute top-24 left-4 right-4 z-30 bg-red-500/95 text-white rounded-2xl p-4 shadow-xl">
            <p className="font-bold mb-1">Analysis failed</p>
            <p className="text-sm opacity-95">{analysisError}</p>
            <p className="text-xs mt-2 opacity-80">Check backend .env (e.g. GROQ_API_KEY) and try again.</p>
          </div>
        )}

        {/* Prediction Result Overlay */}
        {prediction && (
          <div className="absolute top-24 left-4 right-4 z-30">
            <div className="bg-white/95 backdrop-blur rounded-3xl p-6 shadow-2xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-bold font-display uppercase tracking-tight">{prediction.food_name}</h3>
                <span className="text-sm font-bold text-green-600 bg-green-100 px-3 py-1 rounded-full">
                  {prediction.confidence}% match
                </span>
              </div>
              <div className="grid grid-cols-4 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-orange-500">{prediction.calories}</p>
                  <p className="text-xs font-bold text-gray-500 uppercase">Cals</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-blue-500">{prediction.protein}g</p>
                  <p className="text-xs font-bold text-gray-500 uppercase">Protein</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-yellow-500">{prediction.carbs}g</p>
                  <p className="text-xs font-bold text-gray-500 uppercase">Carbs</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-red-500">{prediction.fats}g</p>
                  <p className="text-xs font-bold text-gray-500 uppercase">Fats</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="absolute top-12 left-0 right-0 flex justify-between px-8 z-30">
          <button onClick={toggleFlash} className={cn("p-3 backdrop-blur rounded-full transition-colors", flashActive ? "bg-yellow-400 text-black" : "bg-black/40 text-white")}>
            <Zap size={24} fill={flashActive ? "currentColor" : "none"} />
          </button>
          {hasPhoto && (
            <button onClick={retake} className="p-3 bg-black/40 backdrop-blur rounded-full text-white">
              <CloseIcon size={24} />
            </button>
          )}
        </div>

        <div className="absolute bottom-32 left-0 right-0 flex justify-center items-center gap-8 z-30">
          {!hasPhoto ? (
            <div className="flex flex-col items-center gap-4">
              {cameraReady && (
                <button 
                  onClick={takePicture} 
                  data-testid="button-capture"
                  className="w-20 h-20 rounded-full border-[6px] border-orange-400 flex items-center justify-center p-1 bg-white shadow-lg active:scale-95 transition-transform"
                >
                  <div className="w-full h-full rounded-full border-[3px] border-orange-400 bg-transparent" />
                </button>
              )}
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="flex items-center gap-2 px-5 py-2.5 bg-white/90 text-gray-800 font-semibold rounded-full shadow-lg text-sm"
              >
                <Upload size={18} />
                Upload photo
              </button>
            </div>
          ) : (
            <div className="flex gap-6 items-center">
              <button 
                onClick={retake} 
                data-testid="button-retake"
                className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center text-white shadow-lg active:scale-90 transition-transform"
              >
                <CloseIcon size={32} strokeWidth={3} />
              </button>
              
              {!prediction ? (
                <button 
                  onClick={() => photoData && runAnalysis(photoData)} 
                  disabled={analyzing}
                  data-testid="button-analyze"
                  className="px-8 py-3 bg-blue-500 text-white font-bold rounded-full shadow-lg uppercase tracking-widest text-sm disabled:opacity-50 flex items-center gap-2"
                >
                  {analyzing ? (
                    <>
                      <Loader2 size={18} className="animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    "Analyze again"
                  )}
                </button>
              ) : (
                <button 
                  onClick={logMeal} 
                  data-testid="button-log"
                  className="px-8 py-3 bg-green-500 text-white font-bold rounded-full shadow-lg uppercase tracking-widest text-sm"
                >
                  Log Meal
                </button>
              )}

              {prediction && (
                <button 
                  onClick={logMeal} 
                  data-testid="button-confirm"
                  className="w-16 h-16 rounded-full bg-green-500 flex items-center justify-center text-white shadow-lg active:scale-90 transition-transform"
                >
                  <Check size={32} strokeWidth={3} />
                </button>
              )}
            </div>
          )}
        </div>
        <canvas ref={canvasRef} className="hidden" />
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={handleFilePick}
        />
      </div>
    </Layout>
  );
}
