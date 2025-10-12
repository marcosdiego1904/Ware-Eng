"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"
import { useState } from "react"

const categories = [
  {
    id: "core",
    name: "Core Operations",
    description: "Keeping inventory moving efficiently through your warehouse",
    color: "primary",
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" strokeWidth="2" />
        <path d="M12 6v6l4 2" strokeWidth="2" strokeLinecap="round" />
      </svg>
    ),
    rules: [
      {
        id: 1,
        name: "Forgotten Pallets Alert",
        tagline: "Finds pallets in receiving for too long",
        icon: "⏰",
        problem:
          "Detects pallets that have remained in 'Receiving' or transitional areas for an excessively long period (e.g., more than 10 hours).",
        importance:
          "A pallet that doesn't move from receiving is a red flag. It might have documentation issues, be damaged, or simply have been forgotten, causing bottlenecks.",
        example:
          "A pallet arrived and was scanned into 'Receiving' at 8:00 AM. At 8:00 PM on the same day, it is still in the same location with no movement.",
        action:
          "An anomaly is generated for each pallet that exceeds the time limit in receiving. The action is to investigate the status of that specific pallet to determine why it hasn't been processed and resolve the issue.",
      },
      {
        id: 2,
        name: "Overcapacity Alert",
        tagline: "Detects locations with more pallets than capacity allows",
        icon: "📦",
        problem: "Detects locations that contain more pallets than their physical or designated capacity allows.",
        importance:
          "Critical for inventory data integrity. If there's systematically more than one pallet in a single-space location, it means there's either a 'ghost' pallet in the system or one that is physically lost.",
        example:
          "The rack location S-01-B-04 has a designated capacity of 1 pallet. However, your inventory report shows that pallets PALLET-A and PALLET-B are assigned to the same location.",
        action:
          "The system generates an 'Overcapacity' anomaly. This creates a clear to-do list for your team: physically investigate the conflicting location to identify which pallet is actually there, find the correct location for the other one, and update the data in the system.",
      },
      {
        id: 3,
        name: "Aisle-Stuck Pallets Alert",
        tagline: "Detects pallets stuck in aisles too long",
        icon: "🚧",
        problem:
          "Detects pallets that remain in an 'Aisle' type location for a prolonged period, usually because they were put away in the rack without being scanned into their final location.",
        importance:
          "A pallet that is physically in a rack but systemically in an aisle is a 'lost' pallet. This rule helps ensure the systemic location matches the physical location.",
        example:
          "A pallet is moved to AISLE-05 at 10:00 AM to be stored. At 4:00 PM, the system still shows it in AISLE-05, suggesting the operator put it away but forgot to scan the final rack location.",
        action:
          "Flags each pallet stuck in an aisle as an anomaly. The task is to go to that aisle, find the pallet, and scan it into its correct rack location to sync the system with reality.",
      },
      {
        id: 4,
        name: "Incomplete Lots Alert",
        tagline: "Identifies pallets left behind from their lot",
        icon: "📋",
        problem:
          "Identifies pallets that have been left behind in receiving or transitional areas when the vast majority of their lot has already been moved to its final storage location.",
        importance:
          "Prevents lot fragmentation. Keeping lots together is crucial for efficient picking, accurate inventory control, and proper expiration date management.",
        example:
          "The receiving lot LOT-123 consists of 10 pallets. The system detects that 8 of those pallets are already in storage racks, but 2 of them are still listed in the 'Receiving' area.",
        action:
          "Flags each 'straggler' pallet as an anomaly. The action for the team is to immediately locate those pallets and complete their put-away process to reunite the lot.",
      },
    ],
  },
  {
    id: "quality",
    name: "Quality & Compliance",
    description: "Ensuring every pallet is in a valid, properly tracked location",
    color: "secondary",
    icon: (
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    ),
    rules: [
      {
        id: 5,
        name: "Invalid Locations Alert",
        tagline: "Finds pallets in non-existent location codes",
        icon: "⚠️",
        problem:
          "Finds pallets that have been scanned into a location code that does not exist in your warehouse's configuration or map.",
        importance:
          "Ensures that all inventory is registered in known and valid places. This prevents the creation of 'ghost stock' in non-existent locations due to typing or scanning errors.",
        example:
          "Your warehouse map defines aisles from A-01 to A-50. The inventory report shows a pallet in location A-99. Since A-99 is not a valid location, the system flags it.",
        action:
          "An anomaly is created for each pallet in an undefined location. Your team's task is to locate these pallets and re-scan them into their correct location, thereby correcting the data error.",
      },
      {
        id: 6,
        name: "Scanner Error Detection",
        tagline: "Identifies data integrity issues from scanning errors",
        icon: "🔍",
        problem:
          "Identifies common data integrity issues, such as the same pallet being scanned in multiple locations simultaneously or location codes with impossible formats.",
        importance:
          "Helps maintain a clean and reliable inventory database by detecting errors that are often invisible but can cause significant discrepancies.",
        example:
          "PALLET-123 appears in your report at location S-10-A-01 and, at the same time, at S-25-C-03. This is physically impossible, indicating a scanning or system error.",
        action:
          "Generates a 'Data Integrity' anomaly. The task for your team is to check the pallet's movement history to determine its actual location and remove the duplicate or incorrect record.",
      },
    ],
  },
]

export function RuleCenterView() {
  const [activeCategory, setActiveCategory] = useState("core")
  const [expandedRule, setExpandedRule] = useState<number | null>(null)

  const currentCategory = categories.find((c) => c.id === activeCategory)

  return (
    <div className="min-h-screen bg-background">
      <main className="px-8 py-12 max-w-7xl mx-auto">
        <div className="mb-12 text-center max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-foreground mb-4">How WareWise Protects Your Inventory</h2>
          <p className="text-muted-foreground leading-relaxed">
            Our system continuously monitors your warehouse using 6 intelligent rules organized into 2 core categories.
            Each rule detects problems before they become emergencies.
          </p>
        </div>

        <div className="flex gap-4 mb-6 justify-center flex-wrap">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => {
                setActiveCategory(category.id)
                setExpandedRule(null)
              }}
              className={`flex items-center gap-3 px-8 py-5 rounded-xl border-2 transition-all shadow-sm hover:shadow-md ${
                activeCategory === category.id
                  ? category.color === "primary"
                    ? "border-primary bg-primary/5 shadow-md"
                    : "border-[#4A5568] bg-[#4A5568]/5 shadow-md"
                  : "border-border bg-card hover:border-muted-foreground/30"
              }`}
            >
              <div
                className={`w-12 h-12 rounded-lg flex items-center justify-center transition-colors ${
                  activeCategory === category.id
                    ? category.color === "primary"
                      ? "bg-primary/10 text-primary"
                      : "bg-[#4A5568]/10 text-[#4A5568]"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {category.icon}
              </div>
              <div className="text-left">
                <div className="font-bold text-foreground text-lg">{category.name}</div>
                <div className="text-sm text-muted-foreground">{category.rules.length} rules</div>
              </div>
            </button>
          ))}
        </div>

        {currentCategory && (
          <div className="mb-10 text-center">
            <p className="text-muted-foreground italic">{currentCategory.description}</p>
          </div>
        )}

        {currentCategory && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {currentCategory.rules.map((rule) => (
              <Card
                key={rule.id}
                className={`cursor-pointer transition-all hover:shadow-lg hover:-translate-y-1 ${
                  expandedRule === rule.id ? "ring-2 ring-primary shadow-lg" : "shadow-sm"
                }`}
                onClick={() => setExpandedRule(expandedRule === rule.id ? null : rule.id)}
              >
                <CardHeader className="pb-4">
                  <div className="flex items-start gap-4 mb-3">
                    <div className="text-5xl flex-shrink-0">{rule.icon}</div>
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-lg mb-2 leading-tight">{rule.name}</CardTitle>
                      <Badge
                        className={
                          currentCategory.color === "primary"
                            ? "bg-primary/10 text-primary border border-primary/20"
                            : "bg-[#4A5568]/10 text-[#4A5568] border border-[#4A5568]/20"
                        }
                      >
                        {currentCategory.name}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">{rule.tagline}</p>
                </CardHeader>
                <CardContent className="pt-0">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full hover:bg-primary/5"
                    onClick={(e) => {
                      e.stopPropagation()
                      setExpandedRule(expandedRule === rule.id ? null : rule.id)
                    }}
                  >
                    {expandedRule === rule.id ? "Hide Details ↑" : "Show Details ↓"}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {expandedRule && currentCategory && (
          <div className="mb-12 animate-in fade-in slide-in-from-top-4 duration-300">
            {currentCategory.rules
              .filter((rule) => rule.id === expandedRule)
              .map((rule) => (
                <Card key={rule.id} className="border-2 border-primary shadow-lg">
                  <CardHeader className="pb-6">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-start gap-4">
                        <div className="text-6xl flex-shrink-0">{rule.icon}</div>
                        <div>
                          <CardTitle className="text-2xl mb-2">{rule.name}</CardTitle>
                          <p className="text-muted-foreground text-lg">{rule.tagline}</p>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm" onClick={() => setExpandedRule(null)} className="flex-shrink-0">
                        ✕
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-8">
                    <div className="grid md:grid-cols-2 gap-8">
                      <div className="space-y-6">
                        <div>
                          <h4 className="font-bold text-foreground mb-3 flex items-center gap-2 text-lg">
                            <span className="text-primary text-xl">●</span> What Problem Does It Detect?
                          </h4>
                          <p className="text-muted-foreground pl-7 leading-relaxed">{rule.problem}</p>
                        </div>
                        <div>
                          <h4 className="font-bold text-foreground mb-3 flex items-center gap-2 text-lg">
                            <span className="text-primary text-xl">●</span> Why Is It Important?
                          </h4>
                          <p className="text-muted-foreground pl-7 leading-relaxed">{rule.importance}</p>
                        </div>
                      </div>
                      <div className="space-y-6">
                        <div className="bg-muted/50 p-6 rounded-xl border border-border">
                          <h4 className="font-bold text-foreground mb-3 text-lg">📝 Practical Example</h4>
                          <p className="text-muted-foreground leading-relaxed">{rule.example}</p>
                        </div>
                        <div className="bg-[#38A169]/5 p-6 rounded-xl border-2 border-[#38A169]/20">
                          <h4 className="font-bold text-[#38A169] mb-3 text-lg">✓ Actionable Results</h4>
                          <p className="text-foreground leading-relaxed">{rule.action}</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
          </div>
        )}

        <div className="bg-primary/5 border-2 border-primary/20 rounded-xl p-10 text-center shadow-sm">
          <h3 className="text-2xl font-bold text-foreground mb-4">Ready to Take Action?</h3>
          <p className="text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
            These rules are working right now to protect your inventory. Check your Action Center to see what needs
            attention today.
          </p>
          <Button
            className="bg-primary hover:bg-primary/90 text-primary-foreground shadow-md hover:shadow-lg transition-all"
            size="lg"
            asChild
          >
            <Link href="/action-center">View Action Items →</Link>
          </Button>
        </div>
      </main>
    </div>
  )
}
