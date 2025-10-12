'use client'

import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"

// Mock data for demonstration
const mockProgressData = {
  today: {
    resolved: 12,
    teamEfficiency: 87,
    streakDays: 3,
    streakType: "Zero Stagnant Pallets",
    todayAchievement: {
      title: "Speed Demon",
      description: "Fastest processing time achieved!",
      icon: "⚡",
      unlocked: true
    }
  },
  recentlyResolved: [
    { id: "PLT-4829", action: "Moved to 12.05A", time: "10:30 AM", operator: "Maria S." },
    { id: "PLT-4723", action: "Moved to 15.08B", time: "10:35 AM", operator: "Maria S." },
    { id: "PLT-4651", action: "Moved to 18.12C", time: "11:15 AM", operator: "John D." },
    { id: "LOC-RECV-05", action: "Capacity restored", time: "1:20 PM", operator: "Sarah L." },
    { id: "PLT-4502", action: "Moved to 22.08A", time: "2:45 PM", operator: "Mike R." }
  ],
  stillNeedAttention: {
    critical: 26,
    medium: 49
  },
  weeklyProgress: {
    totalResolved: 78,
    weeklyGoal: 100,
    improvementRate: 15,
    bestDay: "Wednesday (18 resolved)"
  },
  achievements: [
    { title: "Golden Shift", description: "No anomalies during complete shift", icon: "🏆", unlocked: false },
    { title: "Perfect Score", description: "100% data quality for the day", icon: "🎯", unlocked: true },
    { title: "Problem Solver", description: "Resolved 50+ items this week", icon: "🔧", unlocked: true },
    { title: "Consistency King", description: "5 days streak of improvements", icon: "👑", unlocked: false }
  ]
}

interface ProgressTrackerProps {
  className?: string
  onBackToHub?: () => void
  onContinueWorking?: () => void
}

export function ProgressTracker({ className, onBackToHub, onContinueWorking }: ProgressTrackerProps) {
  return (
    <div className={cn("max-w-6xl mx-auto p-6 space-y-6", className)}>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
            ✅ Progress Tracker - Monday
          </h1>
          <p className="text-muted-foreground mt-1">
            Track your achievements and continue building momentum
          </p>
        </div>
        <Button variant="outline" onClick={onBackToHub}>
          ← Back to Hub
        </Button>
      </div>

      {/* Today's Achievements */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

        {/* Items Resolved */}
        <Card className="border-green-200 dark:border-green-800">
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-green-600 dark:text-green-400 mb-1">
              {mockProgressData.today.resolved}
            </div>
            <div className="text-sm text-muted-foreground">Items Resolved</div>
            <div className="text-xs text-green-600 dark:text-green-400 mt-1">
              Great progress! 🎉
            </div>
          </CardContent>
        </Card>

        {/* Team Efficiency */}
        <Card className="border-blue-200 dark:border-blue-800">
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-1">
              {mockProgressData.today.teamEfficiency}%
            </div>
            <div className="text-sm text-muted-foreground">Team Efficiency</div>
            <div className="text-xs text-blue-600 dark:text-blue-400 mt-1">
              Above 80% target ↗️
            </div>
          </CardContent>
        </Card>

        {/* Current Streak */}
        <Card className="border-orange-200 dark:border-orange-800">
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-orange-600 dark:text-orange-400 mb-1 flex items-center justify-center gap-1">
              {mockProgressData.today.streakDays}
              <span className="text-xl">🔥</span>
            </div>
            <div className="text-sm text-muted-foreground">Day Streak</div>
            <div className="text-xs text-orange-600 dark:text-orange-400 mt-1">
              {mockProgressData.today.streakType}
            </div>
          </CardContent>
        </Card>

        {/* Today's Achievement */}
        <Card className="border-purple-200 dark:border-purple-800">
          <CardContent className="p-4 text-center">
            <div className="text-3xl mb-1">
              {mockProgressData.today.todayAchievement.icon}
            </div>
            <div className="text-sm font-semibold text-purple-600 dark:text-purple-400">
              {mockProgressData.today.todayAchievement.title}
            </div>
            <div className="text-xs text-muted-foreground mt-1">
              {mockProgressData.today.todayAchievement.description}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recently Resolved & Still Need Attention */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Recently Resolved */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              ✅ Recently Resolved
              <Badge variant="secondary" className="bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300">
                {mockProgressData.recentlyResolved.length} items
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {mockProgressData.recentlyResolved.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <div className="flex-1">
                    <div className="font-semibold text-sm">{item.id}</div>
                    <div className="text-xs text-muted-foreground">{item.action}</div>
                  </div>
                  <div className="text-right text-xs text-muted-foreground">
                    <div>{item.time}</div>
                    <div>by {item.operator}</div>
                  </div>
                </div>
              ))}
            </div>
            <Separator className="my-4" />
            <Button variant="outline" size="sm" className="w-full">
              View All Resolved Items
            </Button>
          </CardContent>
        </Card>

        {/* Still Need Attention */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              🎯 Still Need Attention
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div>
                    <div className="font-semibold">{mockProgressData.stillNeedAttention.critical} Critical Items</div>
                    <div className="text-sm text-muted-foreground">High priority issues</div>
                  </div>
                </div>
                <Button size="sm" variant="destructive">
                  Tackle Now
                </Button>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <div>
                    <div className="font-semibold">{mockProgressData.stillNeedAttention.medium} Medium Items</div>
                    <div className="text-sm text-muted-foreground">Standard priority</div>
                  </div>
                </div>
                <Button size="sm" variant="outline">
                  Review List
                </Button>
              </div>

              <Separator />

              <div className="text-center">
                <div className="text-lg font-semibold text-muted-foreground mb-2">
                  Keep the momentum going! 💪
                </div>
                <Button onClick={onContinueWorking} className="w-full">
                  Continue Working →
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Weekly Progress & Achievements */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Weekly Progress */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              📊 Weekly Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">

              {/* Progress towards goal */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Weekly Goal Progress</span>
                  <span className="text-sm text-muted-foreground">
                    {mockProgressData.weeklyProgress.totalResolved} / {mockProgressData.weeklyProgress.weeklyGoal}
                  </span>
                </div>
                <Progress
                  value={(mockProgressData.weeklyProgress.totalResolved / mockProgressData.weeklyProgress.weeklyGoal) * 100}
                  className="h-3"
                />
                <div className="text-xs text-muted-foreground mt-1">
                  {mockProgressData.weeklyProgress.weeklyGoal - mockProgressData.weeklyProgress.totalResolved} more to reach weekly target
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-muted/50 rounded-lg">
                  <div className="text-lg font-bold text-green-600 dark:text-green-400">
                    +{mockProgressData.weeklyProgress.improvementRate}%
                  </div>
                  <div className="text-xs text-muted-foreground">Improvement Rate</div>
                </div>
                <div className="text-center p-3 bg-muted/50 rounded-lg">
                  <div className="text-sm font-semibold">Best Day</div>
                  <div className="text-xs text-muted-foreground">
                    {mockProgressData.weeklyProgress.bestDay}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Achievement Collection */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              🏆 Achievement Collection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {mockProgressData.achievements.map((achievement, index) => (
                <div
                  key={index}
                  className={cn(
                    "p-3 rounded-lg border text-center transition-all",
                    achievement.unlocked
                      ? "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800"
                      : "bg-muted/30 border-muted opacity-60"
                  )}
                >
                  <div className="text-2xl mb-1">{achievement.icon}</div>
                  <div className="text-sm font-semibold">{achievement.title}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {achievement.description}
                  </div>
                  {achievement.unlocked && (
                    <Badge variant="secondary" className="mt-2 text-xs bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300">
                      Unlocked! ✨
                    </Badge>
                  )}
                </div>
              ))}
            </div>
            <Separator className="my-4" />
            <div className="text-center text-sm text-muted-foreground">
              <span className="font-medium">2 of 4</span> achievements unlocked this week!
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Motivational Footer */}
      <Card className="bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20">
        <CardContent className="py-6 text-center">
          <div className="text-lg font-semibold text-foreground mb-2">
            🌟 Outstanding Work Today!
          </div>
          <div className="text-sm text-muted-foreground mb-4">
            You've resolved {mockProgressData.today.resolved} items and maintained {mockProgressData.today.teamEfficiency}% efficiency.
            Your {mockProgressData.today.streakDays}-day streak is impressive!
          </div>
          <div className="flex gap-3 justify-center">
            <Button variant="outline" size="sm">
              Share Achievement
            </Button>
            <Button size="sm" onClick={onContinueWorking}>
              Keep Going! 💪
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}