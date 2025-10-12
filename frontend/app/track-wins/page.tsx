"use client"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { ArrowLeft, AlertCircle } from "lucide-react"
import Link from "next/link"
import { useState, useEffect } from "react"
import { getLatestWinsData, type WinsData, formatWinsTimestamp } from "@/lib/wins-api"

export default function TrackYourWins() {
  const [winsData, setWinsData] = useState<WinsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [healthScore, setHealthScore] = useState(0)

  // Fetch real wins data on mount
  useEffect(() => {
    async function fetchWins() {
      try {
        setLoading(true)
        const data = await getLatestWinsData()
        setWinsData(data)
        setError(null)

        // Animate health score
        setTimeout(() => {
          setHealthScore(data.health_score.score)
        }, 100)
      } catch (err: any) {
        console.error("Failed to fetch wins data:", err)
        setError(err.message || "Failed to load your wins data")
      } finally {
        setLoading(false)
      }
    }

    fetchWins()
  }, [])

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-[#F7FAFC] flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-[#FF6B35] border-r-transparent"></div>
          <p className="mt-4 text-sm text-[#718096]">Loading your wins...</p>
        </div>
      </div>
    )
  }

  // Show error state
  if (error || !winsData) {
    return (
      <div className="min-h-screen bg-[#F7FAFC]">
        <header className="border-b bg-white">
          <div className="px-6 py-4">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/" className="flex items-center gap-2">
                  <ArrowLeft className="w-4 h-4" />
                  Back to Dashboard
                </Link>
              </Button>
            </div>
          </div>
        </header>
        <main className="px-6 py-8 max-w-7xl mx-auto">
          <Card className="p-8 bg-white border border-[#E2E8F0] shadow-sm text-center">
            <AlertCircle className="w-12 h-12 text-[#FF6B35] mx-auto mb-4" />
            <h2 className="text-xl font-bold text-[#2D3748] mb-2">No Analysis Data Found</h2>
            <p className="text-sm text-[#718096] mb-6">
              {error || "Please run an analysis first to see your wins and achievements."}
            </p>
            <Button className="bg-[#FF6B35] hover:bg-[#E55A2B] text-white" asChild>
              <Link href="/">Go to Dashboard</Link>
            </Button>
          </Card>
        </main>
      </div>
    )
  }

  // Extract data from API response
  const achievements = winsData.achievements.details
  const unlockedCount = winsData.achievements.unlocked
  const highlights = winsData.highlights
  const problemScorecard = winsData.problem_scorecard
  const totalIssues = winsData.totals.total_issues_detected
  const resolutionTracker = winsData.resolution_tracker.categories
  const totalResolved = winsData.resolution_tracker.total_resolved
  const totalToResolve = winsData.resolution_tracker.total_to_resolve
  const specialLocations = winsData.special_locations
  const operationalImpact = winsData.operational_impact
  const healthInfo = winsData.health_score

  // Calculate special location totals
  const totalSpecialLocations = specialLocations.reduce((sum, cat) => sum + cat.locations.length, 0)
  const cleanSpecialLocations = specialLocations.reduce(
    (sum, cat) => sum + cat.locations.filter((loc) => loc.status === "clean").length,
    0,
  )

  return (
    <div className="min-h-screen bg-[#F7FAFC]">
      {/* Header */}
      <header className="border-b bg-white">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/" className="flex items-center gap-2">
                  <ArrowLeft className="w-4 h-4" />
                  Back to Dashboard
                </Link>
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-[#2D3748]">TRACK YOUR WINS</h1>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="px-6 py-8 max-w-7xl mx-auto">
        {/* ELEMENT 1 & 2: Health Score + Achievements */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* Health Score */}
          <Card className="p-6 bg-white border border-[#E2E8F0] shadow-sm">
            <div className="flex flex-col items-center">
              <div className="relative w-48 h-48 mb-4">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="96" cy="96" r="80" stroke="#E2E8F0" strokeWidth="16" fill="none" />
                  <circle
                    cx="96"
                    cy="96"
                    r="80"
                    stroke={healthInfo.color}
                    strokeWidth="16"
                    fill="none"
                    strokeDasharray={`${(healthScore / 100) * 502.4} 502.4`}
                    strokeLinecap="round"
                    style={{ transition: "stroke-dasharray 1s ease-out" }}
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <div className="text-5xl font-bold text-[#2D3748]">{healthScore}</div>
                  <div className="text-sm text-[#718096] mt-1">out of 100</div>
                </div>
              </div>
              <h3 className="text-base font-bold text-[#2D3748] mb-1">Warehouse Health Score</h3>
              <div className="text-sm font-medium mb-2" style={{ color: healthInfo.color }}>
                {healthInfo.label}
              </div>
              <div className="text-xs text-[#718096]">Based on {winsData.totals.total_pallets} pallets analyzed</div>
            </div>
          </Card>

          {/* Achievements */}
          <Card className="lg:col-span-2 p-6 bg-white border border-[#E2E8F0] shadow-sm">
            <div className="mb-4">
              <h3 className="text-lg font-bold text-[#2D3748] mb-1">ACHIEVEMENTS UNLOCKED</h3>
              <div className="text-sm text-[#718096]">{unlockedCount}/11 earned in this report</div>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
              {achievements.map((achievement) => (
                <div
                  key={achievement.id}
                  className={`p-3 rounded-lg border transition-all ${
                    achievement.unlocked
                      ? "bg-white border-[#38A169] shadow-sm hover:scale-105"
                      : "bg-white border-[#E2E8F0] opacity-50"
                  }`}
                  title={achievement.description}
                >
                  <div className="text-2xl mb-2">{achievement.icon}</div>
                  <div className={`text-xs font-medium ${achievement.unlocked ? "text-[#2D3748]" : "text-[#A0AEC0]"}`}>
                    {achievement.name}
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* ELEMENT 3: Report Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {highlights.map((highlight, index) => (
            <Card
              key={index}
              className="p-6 bg-white border border-[#E2E8F0] shadow-sm hover:-translate-y-1 transition-transform"
            >
              <div className="flex flex-col items-center text-center">
                <div className="text-5xl mb-3">{highlight.icon}</div>
                <div className="text-4xl font-bold text-[#2D3748] mb-2">{highlight.number}</div>
                <h4 className="text-base font-medium text-[#4A5568] mb-1">{highlight.title}</h4>
                {highlight.percentage && (
                  <div className="text-lg font-bold text-[#38A169] mb-2">{highlight.percentage}%</div>
                )}
                <p className="text-sm text-[#718096]">{highlight.context}</p>
              </div>
            </Card>
          ))}
        </div>

        {/* ELEMENT 4 & 5: Problem Scorecard + Resolution Tracker */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Problem Resolution Scorecard */}
          <Card className="p-6 bg-white border border-[#E2E8F0] shadow-sm">
            <h3 className="text-lg font-bold text-[#2D3748] mb-1">PREVENTION SCORECARD</h3>
            <p className="text-sm text-[#718096] mb-4">Problems detected proactively</p>

            <div className="space-y-2 mb-4">
              {problemScorecard.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between py-2 border-b border-[#E2E8F0] last:border-0"
                >
                  <span className="text-sm font-medium text-[#4A5568]">{item.type}</span>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold text-[#2D3748]">{item.detected}</span>
                    <Badge
                      className="text-xs font-semibold"
                      style={{ backgroundColor: item.bg, color: item.color, border: "none" }}
                    >
                      {item.priority}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-4 border-t border-[#E2E8F0] text-center">
              <p className="text-sm font-bold text-[#2D3748] mb-3">
                ✨ {totalIssues} issues caught before they became problems
              </p>
              <Button className="w-full bg-[#FF6B35] hover:bg-[#E55A2B] text-white" asChild>
                <Link href="/action-center">Go to Action Hub →</Link>
              </Button>
            </div>
          </Card>

          {/* Anomalies Resolved Tracker */}
          <Card className="p-6 bg-white border border-[#E2E8F0] shadow-sm">
            <h3 className="text-lg font-bold text-[#2D3748] mb-1">PROBLEM RESOLUTION STATUS</h3>
            <p className="text-sm text-[#718096] mb-4">Track your progress fixing issues</p>

            <div className="space-y-4 mb-4">
              {resolutionTracker.map((item, index) => {
                const percentage = Math.round((item.resolved / item.total) * 100)
                return (
                  <div key={index}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{item.icon}</span>
                        <span className="text-sm font-medium text-[#4A5568]">{item.category}</span>
                      </div>
                      <span className="text-xs text-[#718096]">{item.lastResolved}</span>
                    </div>
                    <div className="relative h-6 bg-[#E2E8F0] rounded-full overflow-hidden">
                      <div
                        className="absolute inset-0 bg-gradient-to-r from-[#38A169] to-[#48BB78] transition-all duration-1000 rounded-full"
                        style={{ width: `${percentage}%` }}
                      />
                      <div className="absolute inset-0 flex items-center px-3">
                        <span className="text-xs font-bold text-[#2D3748]">
                          {item.resolved}/{item.total} resolved ({percentage}%)
                        </span>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>

            <div className="pt-4 border-t border-[#E2E8F0] text-center">
              <p className="text-sm font-bold text-[#2D3748] mb-3">
                ✨ TOTAL: {totalResolved}/{totalToResolve} issues resolved (
                {Math.round((totalResolved / totalToResolve) * 100)}%)
              </p>
              <Button className="w-full bg-[#FF6B35] hover:bg-[#E55A2B] text-white" asChild>
                <Link href="/action-center">Go to Action Hub →</Link>
              </Button>
            </div>
          </Card>
        </div>

        {/* ELEMENT 6: Special Location Performance */}
        <Card className="p-6 bg-white border border-[#E2E8F0] shadow-sm mb-6">
          <h3 className="text-lg font-bold text-[#2D3748] mb-4">SPECIAL LOCATION PERFORMANCE</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6">
            {specialLocations.map((category, catIndex) => (
              <div key={catIndex}>
                <h4 className="text-sm font-bold text-[#2D3748] mb-3 pb-2 border-b border-[#E2E8F0]">
                  {category.category}
                </h4>
                <div className="space-y-2 pl-9">
                  {category.locations.map((location, locIndex) => (
                    <div
                      key={locIndex}
                      className={`flex items-center gap-3 py-1 border-l-4 pl-3 ${
                        location.status === "clean" ? "border-[#38A169]" : "border-[#FF6B35]"
                      }`}
                    >
                      <span className="text-base">{location.status === "clean" ? "✅" : "⚠️"}</span>
                      <span className="font-bold text-sm text-[#2D3748]">{location.name}:</span>
                      <span className="text-sm text-[#4A5568]">
                        {location.status === "clean"
                          ? "Clean (0 issues)"
                          : `${location.issues} ${location.description}`}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-6 border-t border-[#E2E8F0] text-center">
            <p className="text-sm font-bold text-[#2D3748]">
              Summary: {cleanSpecialLocations}/{totalSpecialLocations} special locations operating perfectly this report
            </p>
          </div>
        </Card>

        {/* ELEMENT 7: Today's Operational Impact */}
        <Card className="p-6 bg-white border border-[#E2E8F0] shadow-sm mb-6">
          <h3 className="text-lg font-bold text-[#2D3748] mb-4">TODAY'S OPERATIONAL IMPACT</h3>

          <div className="space-y-3 mb-4">
            <div className="flex items-center gap-4 p-3 bg-[#F7FAFC] rounded-lg hover:bg-[#EDF2F7] transition-colors">
              <div className="text-3xl">{operationalImpact.analysis_completed.icon}</div>
              <div>
                <div className="text-sm font-bold text-[#2D3748]">{operationalImpact.analysis_completed.title}</div>
                <div className="text-sm text-[#4A5568]">{operationalImpact.analysis_completed.description}</div>
              </div>
            </div>

            <div className="flex items-center gap-4 p-3 bg-[#F7FAFC] rounded-lg hover:bg-[#EDF2F7] transition-colors">
              <div className="text-3xl">{operationalImpact.problems_prevented.icon}</div>
              <div>
                <div className="text-sm font-bold text-[#2D3748]">{operationalImpact.problems_prevented.title}</div>
                <div className="text-sm text-[#4A5568]">{operationalImpact.problems_prevented.description}</div>
              </div>
            </div>

            <div className="flex items-center gap-4 p-3 bg-[#F7FAFC] rounded-lg hover:bg-[#EDF2F7] transition-colors">
              <div className="text-3xl">{operationalImpact.issues_resolved.icon}</div>
              <div>
                <div className="text-sm font-bold text-[#2D3748]">{operationalImpact.issues_resolved.title}</div>
                <div className="text-sm text-[#4A5568]">{operationalImpact.issues_resolved.description}</div>
              </div>
            </div>

            <div className="flex items-center gap-4 p-3 bg-[#F7FAFC] rounded-lg hover:bg-[#EDF2F7] transition-colors">
              <div className="text-3xl">{operationalImpact.processing_efficiency.icon}</div>
              <div>
                <div className="text-sm font-bold text-[#2D3748]">
                  {operationalImpact.processing_efficiency.title}
                </div>
                <div className="text-sm text-[#4A5568]">{operationalImpact.processing_efficiency.description}</div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-[#E2E8F0] text-center">
            <p className="text-sm text-[#4A5568]">
              Report: {winsData.report_name} • {formatWinsTimestamp(winsData.timestamp)}
            </p>
          </div>
        </Card>
      </main>
    </div>
  )
}
