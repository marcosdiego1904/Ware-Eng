import { WarehouseIntelligenceDemo } from "@/components/demo-interfaces"

export default function DemoInterfacesPage() {
  return (
    <div className="min-h-screen">
      <WarehouseIntelligenceDemo showStatusBar={true} />
    </div>
  )
}

export const metadata = {
  title: "Warehouse Intelligence Demo - Three Interface Architecture",
  description: "Visual demonstration of the task-oriented UX approach with Smart Landing Hub, Action Hub, Analytics Dashboard, and Progress Tracker"
}