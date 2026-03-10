import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, timestamp, doublePrecision } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Export auth models (required for Replit Auth)
export * from "./models/auth";

// User profile table (extends auth user with nutrition-specific data)
export const userProfiles = pgTable("user_profiles", {
  userId: varchar("user_id").primaryKey().references(() => users.id, { onDelete: "cascade" }),
  name: text("name"),
  gender: varchar("gender", { length: 20 }),
  heightCm: doublePrecision("height_cm"),
  weightKg: doublePrecision("weight_kg"),
  workoutsPerWeek: integer("workouts_per_week").default(0),
  goal: varchar("goal", { length: 20 }), // lose, maintain, gain, fit
  bmr: integer("bmr"),
  tdee: integer("tdee"),
  targetCalories: integer("target_calories"),
  currentStreak: integer("current_streak").default(0),
  totalMiles: doublePrecision("total_miles").default(0),
  onboardingCompleted: integer("onboarding_completed").default(0), // boolean as int
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Meals table
export const meals = pgTable("meals", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").notNull().references(() => users.id, { onDelete: "cascade" }),
  foodName: text("food_name").notNull(),
  calories: integer("calories").notNull(),
  proteinG: doublePrecision("protein_g").notNull(),
  carbsG: doublePrecision("carbs_g").notNull(),
  fatsG: doublePrecision("fats_g").notNull(),
  fiberG: doublePrecision("fiber_g").default(0),
  imageUrl: text("image_url"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Import users from auth models for reference
import { users } from "./models/auth";

// Zod schemas
export const insertUserProfileSchema = createInsertSchema(userProfiles).omit({
  createdAt: true,
  updatedAt: true,
});

export const insertMealSchema = createInsertSchema(meals).omit({
  id: true,
  createdAt: true,
});

// Types
export type UserProfile = typeof userProfiles.$inferSelect;
export type InsertUserProfile = z.infer<typeof insertUserProfileSchema>;
export type Meal = typeof meals.$inferSelect;
export type InsertMeal = z.infer<typeof insertMealSchema>;
