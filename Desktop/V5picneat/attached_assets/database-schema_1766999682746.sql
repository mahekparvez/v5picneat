-- ============================================================================
-- PIC N EAT DATABASE SCHEMA
-- Supports: User auth, meal tracking, leaderboard, images, personal data
-- Designed for 1500+ users, easily scales to millions
-- ============================================================================

-- USERS TABLE
-- Stores user authentication and profile data
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Personal details
  gender TEXT CHECK (gender IN ('male', 'female', 'non-binary', 'prefer-not-to-say')),
  date_of_birth DATE,
  height_cm DECIMAL(5,2),
  weight_kg DECIMAL(5,2),
  goal_weight_kg DECIMAL(5,2),
  activity_level TEXT CHECK (activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
  
  -- Goals
  goal_type TEXT CHECK (goal_type IN ('lose_weight', 'maintain', 'gain_muscle', 'get_fit')),
  daily_calorie_goal INTEGER DEFAULT 1800,
  daily_protein_goal INTEGER DEFAULT 50,
  daily_carbs_goal INTEGER DEFAULT 200,
  daily_fats_goal INTEGER DEFAULT 60,
  
  -- Gamification
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  total_miles DECIMAL(10,2) DEFAULT 0,
  current_mission INTEGER DEFAULT 1,
  total_missions_completed INTEGER DEFAULT 0,
  
  -- App settings
  onboarding_completed BOOLEAN DEFAULT FALSE,
  notifications_enabled BOOLEAN DEFAULT TRUE,
  theme TEXT DEFAULT 'light'
);

-- Create index for faster email lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);


-- MEALS TABLE
-- Stores every meal/food item logged by users
CREATE TABLE meals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Food details
  food_name TEXT NOT NULL,
  meal_type TEXT CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
  
  -- Nutrition data
  calories DECIMAL(8,2) NOT NULL,
  protein_g DECIMAL(6,2) DEFAULT 0,
  carbs_g DECIMAL(6,2) DEFAULT 0,
  fats_g DECIMAL(6,2) DEFAULT 0,
  fiber_g DECIMAL(6,2) DEFAULT 0,
  sodium_mg DECIMAL(8,2) DEFAULT 0,
  sugar_g DECIMAL(6,2) DEFAULT 0,
  
  -- Extended nutrition (for premium features)
  calcium_mg DECIMAL(8,2) DEFAULT 0,
  iron_mg DECIMAL(6,2) DEFAULT 0,
  vitamin_a_mcg DECIMAL(8,2) DEFAULT 0,
  vitamin_c_mg DECIMAL(8,2) DEFAULT 0,
  
  -- Image data
  image_url TEXT,
  image_storage_path TEXT,
  
  -- AI classification data
  ai_confidence DECIMAL(5,4),
  ai_model_version TEXT,
  
  -- Purdue-specific (if applicable)
  dining_court TEXT,
  meal_time TEXT,
  station TEXT,
  
  -- Serving info
  serving_size TEXT,
  quantity DECIMAL(6,2) DEFAULT 1,
  
  -- Metadata
  source TEXT DEFAULT 'camera', -- 'camera', 'search', 'manual', 'dining_hall'
  notes TEXT
);

-- Indexes for fast queries
CREATE INDEX idx_meals_user_id ON meals(user_id);
CREATE INDEX idx_meals_created_at ON meals(created_at);
CREATE INDEX idx_meals_user_date ON meals(user_id, created_at);
CREATE INDEX idx_meals_meal_type ON meals(meal_type);


-- DAILY_STATS TABLE
-- Pre-calculated daily totals for faster dashboard loading
CREATE TABLE daily_stats (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  
  -- Daily totals
  total_calories DECIMAL(8,2) DEFAULT 0,
  total_protein_g DECIMAL(6,2) DEFAULT 0,
  total_carbs_g DECIMAL(6,2) DEFAULT 0,
  total_fats_g DECIMAL(6,2) DEFAULT 0,
  total_fiber_g DECIMAL(6,2) DEFAULT 0,
  
  -- Meal counts
  meals_logged INTEGER DEFAULT 0,
  
  -- Goals
  calorie_goal INTEGER,
  goal_met BOOLEAN DEFAULT FALSE,
  
  -- Gamification
  miles_earned DECIMAL(6,2) DEFAULT 0,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Unique constraint: one row per user per day
  UNIQUE(user_id, date)
);

-- Indexes
CREATE INDEX idx_daily_stats_user_id ON daily_stats(user_id);
CREATE INDEX idx_daily_stats_date ON daily_stats(date);
CREATE INDEX idx_daily_stats_user_date ON daily_stats(user_id, date);


-- STREAKS TABLE
-- Tracks daily check-ins and streaks
CREATE TABLE streaks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  logged_meal BOOLEAN DEFAULT FALSE,
  goal_achieved BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(user_id, date)
);

CREATE INDEX idx_streaks_user_id ON streaks(user_id);
CREATE INDEX idx_streaks_date ON streaks(date);


-- BADGES TABLE
-- Available badges/achievements
CREATE TABLE badges (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT UNIQUE NOT NULL,
  description TEXT,
  icon TEXT,
  criteria_type TEXT NOT NULL, -- 'miles', 'streak', 'meals_logged', 'goal_days'
  criteria_value INTEGER NOT NULL,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default badges
INSERT INTO badges (name, description, icon, criteria_type, criteria_value) VALUES
  ('Moon', 'Reach 100 miles', '🌙', 'miles', 100),
  ('Mercury', 'Reach 200 miles', '☿️', 'miles', 200),
  ('Venus', 'Reach 300 miles', '♀️', 'miles', 300),
  ('Jupiter', 'Reach 400 miles', '♃', 'miles', 400),
  ('Uranus', 'Reach 500 miles', '♅', 'miles', 500),
  ('7 Day Streak', '7 days in a row', '🔥', 'streak', 7),
  ('30 Day Streak', '30 days in a row', '💪', 'streak', 30),
  ('100 Day Streak', '100 days in a row', '🏆', 'streak', 100);


-- USER_BADGES TABLE
-- Track which badges users have earned
CREATE TABLE user_badges (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  badge_id UUID NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
  earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(user_id, badge_id)
);

CREATE INDEX idx_user_badges_user_id ON user_badges(user_id);


-- FOOD_DATABASE TABLE
-- Store common foods and their nutrition for auto-complete
CREATE TABLE food_database (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT NOT NULL,
  brand TEXT,
  
  -- Nutrition per serving
  calories DECIMAL(8,2) NOT NULL,
  protein_g DECIMAL(6,2) DEFAULT 0,
  carbs_g DECIMAL(6,2) DEFAULT 0,
  fats_g DECIMAL(6,2) DEFAULT 0,
  fiber_g DECIMAL(6,2) DEFAULT 0,
  sodium_mg DECIMAL(8,2) DEFAULT 0,
  
  serving_size TEXT,
  serving_unit TEXT,
  
  -- Purdue dining hall specific
  is_dining_hall_item BOOLEAN DEFAULT FALSE,
  dining_court TEXT,
  
  -- Search optimization
  search_vector tsvector,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Full-text search index
CREATE INDEX idx_food_database_search ON food_database USING GIN(search_vector);
CREATE INDEX idx_food_database_name ON food_database(name);


-- SHARED_MEALS TABLE
-- Social feature: users can share meals
CREATE TABLE shared_meals (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  meal_id UUID NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
  
  caption TEXT,
  likes_count INTEGER DEFAULT 0,
  
  is_public BOOLEAN DEFAULT TRUE,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_shared_meals_user_id ON shared_meals(user_id);
CREATE INDEX idx_shared_meals_created_at ON shared_meals(created_at DESC);


-- LIKES TABLE
-- Track who liked what
CREATE TABLE likes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  shared_meal_id UUID NOT NULL REFERENCES shared_meals(id) ON DELETE CASCADE,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  UNIQUE(user_id, shared_meal_id)
);

CREATE INDEX idx_likes_shared_meal_id ON likes(shared_meal_id);


-- FRIENDS TABLE
-- User connections for leaderboard competition
CREATE TABLE friends (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  friend_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  status TEXT CHECK (status IN ('pending', 'accepted', 'blocked')) DEFAULT 'pending',
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Prevent duplicate friendships
  UNIQUE(user_id, friend_id),
  -- Prevent self-friending
  CHECK (user_id != friend_id)
);

CREATE INDEX idx_friends_user_id ON friends(user_id);
CREATE INDEX idx_friends_status ON friends(status);


-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Leaderboard view (top users by streak)
CREATE OR REPLACE VIEW leaderboard AS
SELECT 
  u.id,
  u.name,
  u.current_streak,
  u.total_miles,
  u.total_missions_completed,
  RANK() OVER (ORDER BY u.current_streak DESC, u.total_miles DESC) as rank
FROM users u
WHERE u.onboarding_completed = TRUE
ORDER BY rank
LIMIT 100;


-- User daily summary view
CREATE OR REPLACE VIEW user_daily_summary AS
SELECT 
  u.id as user_id,
  u.name,
  ds.date,
  ds.total_calories,
  ds.total_protein_g,
  ds.total_carbs_g,
  ds.total_fats_g,
  ds.meals_logged,
  ds.goal_met,
  u.daily_calorie_goal,
  (ds.total_calories / NULLIF(u.daily_calorie_goal, 0) * 100) as goal_percentage
FROM users u
LEFT JOIN daily_stats ds ON u.id = ds.user_id;


-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update user streak
CREATE OR REPLACE FUNCTION update_user_streak()
RETURNS TRIGGER AS $$
BEGIN
  -- Check if user logged yesterday
  IF EXISTS (
    SELECT 1 FROM streaks 
    WHERE user_id = NEW.user_id 
    AND date = CURRENT_DATE - INTERVAL '1 day'
    AND logged_meal = TRUE
  ) THEN
    -- Continue streak
    UPDATE users 
    SET current_streak = current_streak + 1,
        longest_streak = GREATEST(longest_streak, current_streak + 1),
        updated_at = NOW()
    WHERE id = NEW.user_id;
  ELSE
    -- Reset streak to 1
    UPDATE users 
    SET current_streak = 1,
        updated_at = NOW()
    WHERE id = NEW.user_id;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update streak when meal is logged
CREATE TRIGGER trigger_update_streak
AFTER INSERT ON streaks
FOR EACH ROW
WHEN (NEW.logged_meal = TRUE)
EXECUTE FUNCTION update_user_streak();


-- Function to update daily stats when meal is added
CREATE OR REPLACE FUNCTION update_daily_stats()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO daily_stats (
    user_id, 
    date, 
    total_calories, 
    total_protein_g, 
    total_carbs_g, 
    total_fats_g,
    total_fiber_g,
    meals_logged
  )
  VALUES (
    NEW.user_id,
    DATE(NEW.created_at),
    NEW.calories,
    NEW.protein_g,
    NEW.carbs_g,
    NEW.fats_g,
    NEW.fiber_g,
    1
  )
  ON CONFLICT (user_id, date) 
  DO UPDATE SET
    total_calories = daily_stats.total_calories + NEW.calories,
    total_protein_g = daily_stats.total_protein_g + NEW.protein_g,
    total_carbs_g = daily_stats.total_carbs_g + NEW.carbs_g,
    total_fats_g = daily_stats.total_fats_g + NEW.fats_g,
    total_fiber_g = daily_stats.total_fiber_g + NEW.fiber_g,
    meals_logged = daily_stats.meals_logged + 1,
    updated_at = NOW();
  
  -- Update streak
  INSERT INTO streaks (user_id, date, logged_meal)
  VALUES (NEW.user_id, DATE(NEW.created_at), TRUE)
  ON CONFLICT (user_id, date)
  DO UPDATE SET logged_meal = TRUE;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update daily stats
CREATE TRIGGER trigger_update_daily_stats
AFTER INSERT ON meals
FOR EACH ROW
EXECUTE FUNCTION update_daily_stats();


-- Function to calculate miles from calories
CREATE OR REPLACE FUNCTION calculate_miles(calories DECIMAL)
RETURNS DECIMAL AS $$
BEGIN
  -- Rough estimate: 100 calories = 1 mile
  RETURN ROUND((calories / 100.0)::numeric, 2);
END;
$$ LANGUAGE plpgsql;


-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- Users can only see/edit their own data
-- ============================================================================

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE streaks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;
ALTER TABLE shared_meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE friends ENABLE ROW LEVEL SECURITY;

-- Policies for users table
CREATE POLICY "Users can view their own data"
  ON users FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own data"
  ON users FOR UPDATE
  USING (auth.uid() = id);

-- Policies for meals table
CREATE POLICY "Users can view their own meals"
  ON meals FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own meals"
  ON meals FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own meals"
  ON meals FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own meals"
  ON meals FOR DELETE
  USING (auth.uid() = user_id);

-- Policies for daily_stats
CREATE POLICY "Users can view their own stats"
  ON daily_stats FOR SELECT
  USING (auth.uid() = user_id);

-- Policies for shared_meals (public can view)
CREATE POLICY "Anyone can view public shared meals"
  ON shared_meals FOR SELECT
  USING (is_public = TRUE);

CREATE POLICY "Users can create shared meals"
  ON shared_meals FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Leaderboard is public
CREATE POLICY "Everyone can view leaderboard"
  ON users FOR SELECT
  USING (onboarding_completed = TRUE);


-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Composite indexes for common queries
CREATE INDEX idx_meals_user_date_type ON meals(user_id, DATE(created_at), meal_type);
CREATE INDEX idx_daily_stats_date_goal ON daily_stats(date, goal_met);