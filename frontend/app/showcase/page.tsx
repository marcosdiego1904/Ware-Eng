import React from "react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ThemeToggle } from "@/components/ui/theme-toggle"

export default function ShowcasePage() {
  return (
    <main className="p-8 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-primary-text">Design System Showcase</h1>
        <ThemeToggle />
      </header>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-secondary-text">Buttons</h2>
        <div className="flex gap-3">
          <Button variant="default" size="lg">Primary Action</Button>
          <Button variant="secondary" size="lg">Secondary</Button>
          <Button variant="success" size="lg">Success</Button>
          <Button variant="warning" size="lg">Warning</Button>
          <Button variant="destructive" size="lg">Delete</Button>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-secondary-text">Badges</h2>
        <div className="flex gap-2 items-center">
          <Badge variant="default">Primary</Badge>
          <Badge variant="success">All Clear</Badge>
          <Badge variant="warning">Needs Review</Badge>
          <Badge variant="emergency">Critical</Badge>
          <Badge variant="success-light">+12% Improvement</Badge>
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-secondary-text">Alert Cards</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="alert-urgent bg-card p-4 rounded-md">
            <h3 className="text-primary-text font-bold">Urgent: Pallet Failure</h3>
            <p className="text-secondary-text">3 pallets blocked in Zone A</p>
          </div>
          <div className="alert-high bg-card p-4 rounded-md">
            <h3 className="text-primary-text font-bold">High: Capacity Warning</h3>
            <p className="text-secondary-text">Section B at 92% capacity</p>
          </div>
          <div className="alert-medium bg-card p-4 rounded-md">
            <h3 className="text-primary-text font-bold">Medium: Review Recommended</h3>
            <p className="text-secondary-text">Orders delayed by 2 hours</p>
          </div>
          <div className="alert-low bg-card p-4 rounded-md">
            <h3 className="text-primary-text font-bold">Low: Completed</h3>
            <p className="text-secondary-text">No action needed</p>
          </div>
        </div>
      </section>
    </main>
  )
}
