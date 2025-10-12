export default function Loading() {
  return (
    <div className="min-h-screen bg-[#F7FAFC] flex items-center justify-center">
      <div className="text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-[#FF6B35] border-r-transparent"></div>
        <p className="mt-4 text-sm text-[#718096]">Loading your wins...</p>
      </div>
    </div>
  )
}
