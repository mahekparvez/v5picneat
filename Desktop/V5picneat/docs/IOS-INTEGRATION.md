# 📱 PicNEat iOS Integration Guide

## ✅ Your Backend is Perfect for iOS!

Your FastAPI backend is a **standard RESTful API** that works seamlessly with iOS URLSession.

---

## 🎯 What You Have:

✅ **Single endpoint**: `/analyze-meal`  
✅ **Simple POST request**: Send image, get JSON  
✅ **Fast response**: 2-4 seconds (perfect for mobile)  
✅ **Clean JSON**: Matches Swift Codable perfectly  
✅ **HTTPS ready**: Railway provides SSL automatically  
✅ **CORS enabled**: Works from any client  

---

## 📲 How to Integrate (3 Steps)

### **Step 1: Add the Swift Code**

Copy `PicNEatAPI.swift` into your Xcode project:
- Drag & drop into your project
- Or paste the code into a new Swift file

### **Step 2: Update the Base URL**

In `PicNEatAPI.swift`, change:
```swift
private let baseURL = "https://picneat-backend-production.up.railway.app"
```

To your actual Railway URL (after deployment).

For local testing:
```swift
private let baseURL = "http://localhost:8000"
```

### **Step 3: Use in Your Views**

```swift
struct CameraView: View {
    @StateObject private var api = PicNEatAPI()
    
    func handlePhoto(_ image: UIImage) {
        Task {
            let result = try await api.analyzeMeal(image: image)
            
            // Update your UI with result
            updateCalorieRing(result.totalCalories)
            showNeilCelebration()
            updateStreak()
        }
    }
}
```

---

## 📊 API Response Structure

Your backend returns this JSON:

```json
{
  "foods": [{
    "name": "pizza, cheese, regular crust",
    "portion_grams": 125.3,
    "calories": 285,
    "protein": 15.0,
    "carbs": 45.1,
    "fats": 12.5,
    "confidence": 0.91,
    "source": "purdue"
  }],
  "total_calories": 285,
  "total_protein": 15.0,
  "total_carbs": 45.1,
  "total_fats": 12.5,
  "analysis_time_ms": 2847
}
```

Which maps perfectly to Swift:

```swift
struct MealAnalysisResponse: Codable {
    let foods: [DetectedFood]
    let totalCalories: Int
    let totalProtein: Double
    // ... etc
}
```

---

## 🎨 UI Flow (From Your PRD)

```
1. User taps PIC tab
   ↓
2. Camera opens (helmet HUD)
   ↓
3. Takes photo
   ↓
4. Call: api.analyzeMeal(image)
   [Shows: Neil "working" animation]
   ↓
5. Get response (2-4 seconds)
   ↓
6. Display results:
   - Food name + confidence %
   - Calories + macros
   - [Retake] or [Log Meal] buttons
   ↓
7. User taps [Log Meal]
   ↓
8. Save to Supabase
9. Show Neil celebration (+FUEL)
10. Update calorie ring
11. Update streak
```

---

## 🔌 Complete Example

```swift
// 1. In your camera view
@State private var capturedImage: UIImage?

// 2. After taking photo
capturedImage = image

// 3. Analyze the image
Task {
    do {
        let result = try await api.analyzeMeal(image: image)
        
        // 4. Update UI
        await MainActor.run {
            // Show results screen
            self.showResults(result)
            
            // Neil animation
            self.showNeilWorking = false
            self.showNeilEating = true
        }
    } catch {
        // Show error
        self.showError(error)
    }
}

// 5. User taps "Log Meal"
func logMeal(_ result: MealAnalysisResponse) {
    // Save to Supabase
    supabase.from("meal_logs").insert([
        "user_id": currentUser.id,
        "detected_foods": result.foods,
        "total_calories": result.totalCalories,
        "photo_url": uploadedImageURL
    ])
    
    // Update fuel
    currentUser.fuelTotal += 25
    
    // Show celebration
    showNeilCelebration()
}
```

---

## ✅ What Works Out of the Box:

1. ✅ **Image Upload** - Multipart form data (standard)
2. ✅ **JSON Parsing** - Swift Codable (automatic)
3. ✅ **Error Handling** - HTTP status codes
4. ✅ **Async/Await** - Modern Swift concurrency
5. ✅ **Type Safety** - Full compile-time checks

---

## 🧪 Testing

### **Test Health Check:**
```swift
let api = PicNEatAPI()
let healthy = try await api.checkHealth()
print("Backend online: \(healthy)")
```

### **Test Food Detection:**
```swift
let testImage = UIImage(named: "pizza")!
let result = try await api.analyzeMeal(image: testImage)
print("Detected: \(result.foods[0].name)")
print("Calories: \(result.totalCalories)")
```

---

## 📱 Info.plist Requirements

Add camera permission:

```xml
<key>NSCameraUsageDescription</key>
<string>PicNEat needs camera access to identify your food</string>
```

---

## 🔥 Performance Tips

1. **Image Compression**
   ```swift
   image.jpegData(compressionQuality: 0.8) // 80% quality
   ```
   - Faster upload
   - Same accuracy
   - Less bandwidth

2. **Loading States**
   ```swift
   @Published var isAnalyzing = false
   ```
   - Show Neil "working" animation
   - Disable buttons during analysis
   - Better UX

3. **Error Handling**
   ```swift
   enum APIError: LocalizedError {
       case invalidImage
       case serverError(Int)
   }
   ```
   - User-friendly messages
   - Retry options
   - Offline handling

---

## 🎯 What Your iOS App Needs to Do:

**Required:**
- ✅ Take photo
- ✅ POST to `/analyze-meal`
- ✅ Parse JSON response
- ✅ Display results

**Optional (but cool):**
- 🎨 Neil animations during analysis
- 💾 Cache results locally
- 🔄 Retry on network error
- 📊 Show confidence % badge
- 🏫 Highlight Purdue menu matches

---

## 🚀 Deployment Checklist

**Before submitting to App Store:**

1. ✅ Change baseURL to Railway production URL
2. ✅ Add error handling for all API calls
3. ✅ Test with slow network (airplane mode on/off)
4. ✅ Add loading indicators
5. ✅ Cache images locally (optional)
6. ✅ Add camera permissions to Info.plist

---

## 💡 Pro Tips

1. **Use @StateObject for API**
   ```swift
   @StateObject private var api = PicNEatAPI()
   ```
   - Prevents recreation
   - Maintains state

2. **Handle Background**
   ```swift
   .onAppear {
       Task {
           try? await api.checkHealth()
       }
   }
   ```
   - Check connection on launch
   - Better UX

3. **Show Source Badge**
   ```swift
   if food.source == "purdue" {
       Image("hillenbrand-logo")
       Text("From \(food.diningHall)")
   }
   ```
   - Users love seeing campus data!

---

## 🎉 You're Ready!

Your backend is **100% compatible** with iOS URLSession. No special setup needed!

**Next steps:**
1. Deploy backend to Railway
2. Get your production URL
3. Update `baseURL` in Swift code
4. Test with real photos
5. Ship to TestFlight! 🚀

---

## 📞 Need More?

The Swift code includes:
- ✅ Complete API client
- ✅ Error handling
- ✅ SwiftUI examples
- ✅ Camera integration
- ✅ Result display views

Just copy-paste and customize! 🎨
