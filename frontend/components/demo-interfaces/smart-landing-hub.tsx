'use client'

import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

// Enhanced warehouse mock data - premium intelligence
const mockData = {
  criticalItems: 38,
  mediumItems: 49,
  resolvedToday: 12,
  mostUrgent: "58 forgotten pallets need attention in RECV-01",
  financialImpact: "$45,000",
  timeframe: "125h over threshold",
  topPattern: "RECV-01 causes 40% of forgotten pallet issues",
  currentStreak: "3 days without stagnant pallets",
  palletIds: ["PLT-4829", "PLT-4723", "PLT-3901"],
  zones: ["RECV-01", "RECV-02", "AISLE-12"],
  // Enhanced data for visualizations
  capacityData: {
    current: 58,
    threshold: 125,
    percentage: 46
  },
  // Track Progress data
  trackProgress: {
    resolvedToday: 12,
    streakDays: 3,
    streakType: "Zero Stagnant Pallets",
    motivationalText: "Keep it going! Team performance trending up",
    last7Days: [2, 1, 0, 0, 0, 1, 0], // 0 = perfect, 1 = minor, 2+ = problems
    trend: {
      direction: "up",
      change: "+12%",
      period: "vs last week"
    }
  },
  processingStatus: {
    lastUpdated: "Just now",
    processingTime: "2.3s",
    confidence: 94
  }
}

interface SmartLandingHubProps {
  className?: string
  onNavigate?: (destination: 'action' | 'analytics' | 'progress' | 'upload') => void
}

export function SmartLandingHub({ className, onNavigate }: SmartLandingHubProps) {
  return (
    <div className={cn("max-w-5xl mx-auto p-6 space-y-8", className)}>
      {/* Main Header - Brand Voice Integration */}
      <div className="text-center space-y-3">
        <h1 className="text-slate-800 dark:text-slate-100" style={{ fontFamily: 'Roboto, sans-serif', fontWeight: 'bold', fontSize: '32px' }}>
          What needs your attention today?
        </h1>
        <div className="space-y-1">
          <p className="text-slate-600 dark:text-slate-300 text-lg" style={{ fontFamily: 'Roboto, sans-serif' }}>
            Built by warehouse professionals who understand the real struggles
          </p>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Here's what our analysis found in your warehouse
          </p>
        </div>
      </div>

      {/* Main Action Cards Grid - F-Pattern Layout Optimization */}
      {/* Take Action positioned top-left for F-pattern reading flow */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* Take Action Card - Safety Orange Brand Integration - PRIMARY FOCUS */}
        <Card
          className="cursor-pointer hover:shadow-xl transition-all duration-300 border-2 border-orange-100 hover:border-orange-200 dark:border-orange-900/50 dark:hover:border-orange-800/50 hover:scale-[1.03] shadow-lg hover:shadow-2xl ring-1 ring-orange-100 dark:ring-orange-900/30 bg-gradient-to-br from-orange-50/30 to-orange-100/20 dark:from-orange-950/20 dark:to-orange-900/30"
          style={{ borderRadius: '6px' }}
          onClick={() => onNavigate?.('action')}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center border border-orange-200 dark:border-orange-800 transition-all duration-200 hover:bg-orange-200 dark:hover:bg-orange-800/50" style={{ borderRadius: '6px' }}>
                {/* Warehouse Safety Alert Icon - Flame/Urgency Symbol */}
                <svg className="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z" />
                </svg>
              </div>
              <div>
                <CardTitle className="text-slate-800 dark:text-slate-100" style={{ fontFamily: 'Roboto, sans-serif', fontWeight: 'bold', fontSize: '20px', letterSpacing: '-0.025em' }}>
                  Fix Problems NOW
                </CardTitle>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className="bg-orange-500 text-white hover:bg-orange-600 transition-all duration-200 hover:scale-105 hover:shadow-md">
                    {mockData.criticalItems} urgent
                  </Badge>
                  <span className="text-sm text-slate-600 dark:text-slate-400" style={{ fontFamily: 'Roboto, sans-serif' }}>
                    worth {mockData.financialImpact}
                  </span>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400 mb-1" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  Highest risk right now:
                </p>
                <p className="font-medium text-orange-700 dark:text-orange-300" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  {mockData.mostUrgent}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  {mockData.timeframe} • Impact: {mockData.financialImpact}
                </p>
                {/* Capacity Progress Bar */}
                <div className="mt-2">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-slate-600 dark:text-slate-400" style={{ fontFamily: 'Roboto, sans-serif' }}>
                      Capacity Threshold
                    </span>
                    <span className="text-xs font-medium text-orange-700 dark:text-orange-300">
                      {mockData.capacityData.current}/{mockData.capacityData.threshold}
                    </span>
                  </div>
                  <div className="w-full bg-orange-100 dark:bg-orange-900/30 rounded-full h-2">
                    <div
                      className="bg-orange-500 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${mockData.capacityData.percentage}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              <Button
                className="w-full mt-3 bg-orange-500 hover:bg-orange-600 text-white font-medium"
                style={{ fontFamily: 'Roboto, sans-serif', borderRadius: '6px' }}
                onClick={(e) => {
                  e.stopPropagation()
                  onNavigate?.('action')
                }}
              >
                See What Needs Fixed
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* View Analytics Card - Steel Gray Professional Authority */}
        <Card
          className="cursor-pointer hover:shadow-xl transition-all duration-300 border-2 hover:border-slate-300 dark:hover:border-slate-600 hover:scale-[1.03] shadow-md hover:shadow-lg bg-gradient-to-br from-slate-50/40 to-slate-100/30 dark:from-slate-800/40 dark:to-slate-700/30"
          style={{ borderRadius: '6px' }}
          onClick={() => onNavigate?.('analytics')}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center border border-slate-200 dark:border-slate-700">
                {/* Zone Grid Icon - Warehouse Native */}
                <svg className="w-6 h-6 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 5h16M4 12h16M4 19h16M10 5v14M4 5v14a2 2 0 002 2h12a2 2 0 002-2V5" />
                  <text x="7" y="9" fontSize="6" fill="currentColor" fontWeight="bold">A</text>
                  <text x="13" y="9" fontSize="6" fill="currentColor" fontWeight="bold">2</text>
                </svg>
              </div>
              <div>
                <CardTitle className="text-slate-800 dark:text-slate-100" style={{ fontFamily: 'Roboto, sans-serif', fontWeight: 'bold', fontSize: '20px', letterSpacing: '-0.025em' }}>
                  Understand Patterns
                </CardTitle>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  See where problems concentrate
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400 mb-1" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  Key pattern identified:
                </p>
                <p className="font-medium text-slate-700 dark:text-slate-300" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  {mockData.topPattern}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Analysis of {mockData.zones.join(', ')}
                </p>
                {/* Zone Heatmap Preview */}
                <div className="mt-2">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-slate-600 dark:text-slate-400" style={{ fontFamily: 'Roboto, sans-serif' }}>
                      Problem Hotspots
                    </span>
                    <span className="text-xs font-medium text-slate-700 dark:text-slate-300">
                      40% concentrated
                    </span>
                  </div>
                  <div className="grid grid-cols-6 gap-1 h-6">
                    {[3, 1, 0, 2, 3, 1, 0, 1, 3, 2, 1, 0].map((intensity, index) => (
                      <div
                        key={index}
                        className={`rounded-sm transition-all duration-500 ${
                          intensity === 0
                            ? 'bg-slate-200 dark:bg-slate-700'
                            : intensity === 1
                            ? 'bg-yellow-300 dark:bg-yellow-600'
                            : intensity === 2
                            ? 'bg-orange-400 dark:bg-orange-500'
                            : 'bg-red-500 dark:bg-red-600'
                        }`}
                        title={`Zone ${Math.floor(index / 2) + 1}: ${
                          intensity === 0 ? 'Normal' : intensity === 1 ? 'Minor' : intensity === 2 ? 'Moderate' : 'High'
                        } issues`}
                      ></div>
                    ))}
                  </div>
                </div>
              </div>
              <Button
                variant="outline"
                className="w-full mt-3 border-slate-300 hover:bg-slate-50 dark:border-slate-600 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium"
                style={{ fontFamily: 'Roboto, sans-serif', borderRadius: '6px' }}
                onClick={(e) => {
                  e.stopPropagation()
                  onNavigate?.('analytics')
                }}
              >
                Dive Into Analytics
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Track Progress Card - Safety Orange Success (Brand Aligned) */}
        <Card
          className="cursor-pointer hover:shadow-xl transition-all duration-300 border-2 border-orange-100 hover:border-orange-200 dark:border-orange-900/50 dark:hover:border-orange-800/50 hover:scale-[1.03] shadow-md hover:shadow-lg bg-gradient-to-br from-orange-50/30 to-orange-100/20 dark:from-orange-950/20 dark:to-orange-900/30"
          style={{ borderRadius: '6px' }}
          onClick={() => onNavigate?.('progress')}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center border border-orange-200 dark:border-orange-800" style={{ borderRadius: '6px' }}>
                {/* Pallet Stack Icon - Warehouse Native */}
                <svg className="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 10h18M3 14h18M3 18h18M5 6h14a2 2 0 012 2v12a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8 6V4m8 2V4" />
                </svg>
              </div>
              <div>
                <CardTitle className="text-slate-800 dark:text-slate-100" style={{ fontFamily: 'Roboto, sans-serif', fontWeight: 'bold', fontSize: '20px', letterSpacing: '-0.025em' }}>
                  Track Your Wins
                </CardTitle>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className="bg-orange-500 text-white hover:bg-orange-600 transition-all duration-200 hover:scale-105 hover:shadow-md">
                    {mockData.trackProgress.resolvedToday} solved today
                  </Badge>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400 mb-1" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  Current streak:
                </p>
                <p className="font-medium text-orange-700 dark:text-orange-300 flex items-center gap-2" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  <span className="text-orange-500 text-lg">🔥</span>
                  Day {mockData.trackProgress.streakDays}: {mockData.trackProgress.streakType}
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  {mockData.trackProgress.motivationalText}
                </p>
                {/* 7-Day Performance Chart */}
                <div className="mt-3">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs text-slate-600 dark:text-slate-400" style={{ fontFamily: 'Roboto, sans-serif' }}>
                      Last 7 days
                    </span>
                    <span className="text-xs font-medium text-orange-700 dark:text-orange-300">
                      {mockData.trackProgress.trend.change} {mockData.trackProgress.trend.period}
                    </span>
                  </div>
                  <div className="flex items-end gap-1 h-8">
                    {mockData.trackProgress.last7Days.map((value, index) => (
                      <div
                        key={index}
                        className={`flex-1 rounded-sm transition-all duration-500 ${
                          value === 0
                            ? 'bg-orange-500 opacity-90'
                            : value === 1
                            ? 'bg-yellow-400 opacity-70'
                            : 'bg-red-400 opacity-60'
                        }`}
                        style={{
                          height: `${Math.max(20, (3 - value) * 10)}px`,
                          maxHeight: '32px'
                        }}
                        title={`Day ${index + 1}: ${value === 0 ? 'Perfect' : value === 1 ? 'Minor issues' : 'Problems'}`}
                      ></div>
                    ))}
                  </div>
                </div>
              </div>
              <Button
                variant="outline"
                className="w-full mt-3 border-orange-200 hover:bg-orange-50 dark:border-orange-800 dark:hover:bg-orange-900/30 text-orange-700 dark:text-orange-300 font-medium"
                style={{ fontFamily: 'Roboto, sans-serif', borderRadius: '6px' }}
                onClick={(e) => {
                  e.stopPropagation()
                  onNavigate?.('progress')
                }}
              >
                See Your Progress
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Upload New Report Card - Secondary Action Steel Gray */}
        <Card
          className="cursor-pointer hover:shadow-xl transition-all duration-300 border-2 hover:border-slate-300 dark:hover:border-slate-600 hover:scale-[1.03] shadow-md hover:shadow-lg bg-gradient-to-br from-slate-50/40 to-slate-100/30 dark:from-slate-800/40 dark:to-slate-700/30"
          style={{ borderRadius: '6px' }}
          onClick={() => onNavigate?.('upload')}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center border border-slate-200 dark:border-slate-700">
                {/* Warehouse Clipboard Icon - Professional Data Entry */}
                <svg className="w-6 h-6 text-slate-600 dark:text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6" />
                </svg>
              </div>
              <div>
                <CardTitle className="text-slate-800 dark:text-slate-100" style={{ fontFamily: 'Roboto, sans-serif', fontWeight: 'bold', fontSize: '20px', letterSpacing: '-0.025em' }}>
                  Run New Analysis
                </CardTitle>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  Fresh inventory data from warehouse
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-slate-500 dark:text-slate-400 mb-1" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  Upload your latest export:
                </p>
                <p className="font-medium text-slate-700 dark:text-slate-300" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  Excel/CSV from your WMS
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                  Automatic column detection • Instant analysis
                </p>
                {/* Processing Status Indicator */}
                <div className="mt-2">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs text-slate-600 dark:text-slate-400" style={{ fontFamily: 'Roboto, sans-serif' }}>
                      System Ready
                    </span>
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-xs font-medium text-slate-700 dark:text-slate-300">
                        {mockData.processingStatus.confidence}% confidence
                      </span>
                    </div>
                  </div>
                  <div className="bg-slate-100 dark:bg-slate-800 rounded p-2 text-xs text-slate-600 dark:text-slate-400">
                    <div className="flex justify-between">
                      <span>Last processing: {mockData.processingStatus.processingTime}</span>
                      <span>{mockData.processingStatus.lastUpdated}</span>
                    </div>
                  </div>
                </div>
              </div>
              <Button
                variant="outline"
                className="w-full mt-3 border-slate-300 hover:bg-slate-50 dark:border-slate-600 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium"
                style={{ fontFamily: 'Roboto, sans-serif', borderRadius: '6px' }}
                onClick={(e) => {
                  e.stopPropagation()
                  onNavigate?.('upload')
                }}
              >
                Upload & Analyze
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Intelligence Preview Cards - Data-Driven Insights */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Health Score Preview - Steel Gray Professional */}
        <Card
          className="cursor-pointer hover:shadow-lg transition-all duration-300 border-2 border-slate-200 hover:border-slate-300 dark:border-slate-700 dark:hover:border-slate-600 bg-gradient-to-br from-slate-50/40 to-slate-100/30 dark:from-slate-800/40 dark:to-slate-700/30"
          style={{ borderRadius: '6px' }}
          onClick={() => onNavigate?.('progress')}
        >
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              {/* Health Score Circle */}
              <div className="relative w-20 h-20">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="40" cy="40" r="32" stroke="#E2E8F0" strokeWidth="6" fill="none" />
                  <circle
                    cx="40"
                    cy="40"
                    r="32"
                    stroke="#4A5568"
                    strokeWidth="6"
                    fill="none"
                    strokeDasharray={`${(85 / 100) * 201} 201`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-2xl font-bold text-slate-800 dark:text-slate-100">85</span>
                </div>
              </div>
              {/* Score Info */}
              <div className="flex-1">
                <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100 mb-1" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  Warehouse Health
                </h3>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  <span className="text-slate-700 dark:text-slate-300 font-medium">Excellent</span>
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
                  Based on 500 pallets
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Wins Preview - Safety Orange Action */}
        <Card
          className="cursor-pointer hover:shadow-lg transition-all duration-300 border-2 border-orange-100 hover:border-orange-200 dark:border-orange-900/50 dark:hover:border-orange-800/50 bg-gradient-to-br from-orange-50/30 to-orange-100/20 dark:from-orange-950/20 dark:to-orange-900/30"
          style={{ borderRadius: '6px' }}
          onClick={() => onNavigate?.('action')}
        >
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              {/* Quick Wins Icon */}
              <div className="w-20 h-20 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center border-4 border-orange-200 dark:border-orange-800">
                <span className="text-3xl">🎯</span>
              </div>
              {/* Wins Info */}
              <div className="flex-1">
                <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100 mb-1" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  Quick Wins Available
                </h3>
                <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">12</p>
                <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
                  5-15 min fixes
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Space Availability Preview - Steel Gray Professional */}
        <Card
          className="cursor-pointer hover:shadow-lg transition-all duration-300 border-2 border-slate-200 hover:border-slate-300 dark:border-slate-700 dark:hover:border-slate-600 bg-gradient-to-br from-slate-50/40 to-slate-100/30 dark:from-slate-800/40 dark:to-slate-700/30"
          style={{ borderRadius: '6px' }}
          onClick={() => onNavigate?.('analytics')}
        >
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              {/* Space Icon */}
              <div className="w-20 h-20 bg-slate-100 dark:bg-slate-800 rounded-lg flex items-center justify-center border-2 border-slate-200 dark:border-slate-700">
                <span className="text-3xl">📦</span>
              </div>
              {/* Space Info */}
              <div className="flex-1">
                <h3 className="text-sm font-bold text-slate-800 dark:text-slate-100 mb-1" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  Space Available
                </h3>
                <p className="text-2xl font-bold text-slate-700 dark:text-slate-300">79%</p>
                <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
                  1,903 locations open
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Status Summary - Warehouse Professional Style */}
      <Card className="bg-slate-50/50 dark:bg-slate-800/50 border-slate-200 dark:border-slate-700" style={{ borderRadius: '6px' }}>
        <CardContent className="py-4">
          <div className="flex items-center justify-center gap-8 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-orange-500 rounded-full shadow-sm"></div>
              <span className="font-medium text-slate-800 dark:text-slate-200" style={{ fontFamily: 'Roboto, sans-serif' }}>
                {mockData.criticalItems}
              </span>
              <span className="text-slate-600 dark:text-slate-400" style={{ fontFamily: 'Roboto, sans-serif' }}>
                Urgent
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-full shadow-sm"></div>
              <span className="font-medium text-slate-800 dark:text-slate-200" style={{ fontFamily: 'Roboto, sans-serif' }}>
                {mockData.mediumItems}
              </span>
              <span className="text-slate-600 dark:text-slate-400" style={{ fontFamily: 'Roboto, sans-serif' }}>
                Monitor
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full shadow-sm"></div>
              <span className="font-medium text-slate-800 dark:text-slate-200" style={{ fontFamily: 'Roboto, sans-serif' }}>
                {mockData.resolvedToday}
              </span>
              <span className="text-slate-600 dark:text-slate-400" style={{ fontFamily: 'Roboto, sans-serif' }}>
                Fixed Today
              </span>
            </div>
          </div>
          <div className="text-center mt-2">
            <div className="flex items-center justify-center gap-4 text-xs text-slate-500 dark:text-slate-400">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span style={{ fontFamily: 'Roboto, sans-serif' }}>Live Data</span>
              </div>
              <span>•</span>
              <span style={{ fontFamily: 'Roboto, sans-serif' }}>Last updated: {mockData.processingStatus.lastUpdated}</span>
              <span>•</span>
              <span style={{ fontFamily: 'Roboto, sans-serif' }}>Processing: {mockData.processingStatus.processingTime}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}