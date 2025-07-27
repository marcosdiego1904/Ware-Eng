"use client"

import { cn } from "@/lib/utils"
import { Loader2, BarChart3, Upload, Database, Zap } from "lucide-react"

interface LoadingProps {
  className?: string
  size?: "sm" | "md" | "lg"
  text?: string
  variant?: "spinner" | "pulse" | "dots" | "bars" | "process"
}

export function Loading({ 
  className, 
  size = "md", 
  text = "Loading...", 
  variant = "spinner" 
}: LoadingProps) {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6", 
    lg: "w-8 h-8"
  }

  const textSizes = {
    sm: "text-sm",
    md: "text-base",
    lg: "text-lg"
  }

  if (variant === "spinner") {
    return (
      <div className={cn("flex items-center justify-center gap-2", className)}>
        <Loader2 className={cn("animate-spin text-blue-600", sizeClasses[size])} />
        <span className={cn("text-gray-600 font-medium", textSizes[size])}>{text}</span>
      </div>
    )
  }

  if (variant === "pulse") {
    return (
      <div className={cn("flex items-center justify-center gap-2", className)}>
        <div className={cn(
          "bg-blue-600 rounded-full animate-pulse",
          sizeClasses[size]
        )} />
        <span className={cn("text-gray-600 font-medium", textSizes[size])}>{text}</span>
      </div>
    )
  }

  if (variant === "dots") {
    return (
      <div className={cn("flex items-center justify-center gap-3", className)}>
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={cn(
                "bg-blue-600 rounded-full animate-bounce",
                size === "sm" ? "w-2 h-2" : size === "md" ? "w-3 h-3" : "w-4 h-4"
              )}
              style={{
                animationDelay: `${i * 0.1}s`,
                animationDuration: "0.6s"
              }}
            />
          ))}
        </div>
        <span className={cn("text-gray-600 font-medium", textSizes[size])}>{text}</span>
      </div>
    )
  }

  if (variant === "bars") {
    return (
      <div className={cn("flex items-center justify-center gap-3", className)}>
        <div className="flex items-end gap-1">
          {[0, 1, 2, 3].map((i) => (
            <div
              key={i}
              className={cn(
                "bg-blue-600 animate-pulse",
                size === "sm" ? "w-1" : size === "md" ? "w-1.5" : "w-2"
              )}
              style={{
                height: `${12 + Math.sin(i * 0.5) * 8}px`,
                animationDelay: `${i * 0.1}s`,
                animationDuration: "1s"
              }}
            />
          ))}
        </div>
        <span className={cn("text-gray-600 font-medium", textSizes[size])}>{text}</span>
      </div>
    )
  }

  if (variant === "process") {
    return (
      <div className={cn("flex flex-col items-center gap-4", className)}>
        <div className="relative">
          <div className="w-16 h-16 border-4 border-blue-200 rounded-full animate-spin">
            <div className="absolute top-1 left-1 w-2 h-2 bg-blue-600 rounded-full" />
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <BarChart3 className="w-6 h-6 text-blue-600" />
          </div>
        </div>
        <div className="text-center">
          <p className="font-semibold text-gray-900">{text}</p>
          <p className="text-sm text-gray-500 mt-1">Please wait while we process your data</p>
        </div>
      </div>
    )
  }

  return <Loading variant="spinner" size={size} text={text} className={className} />
}

// Specialized loading components for different contexts
export function AnalysisLoading({ stage = "uploading" }: { stage?: "uploading" | "processing" | "analyzing" | "completing" }) {
  const stages = {
    uploading: { icon: Upload, text: "Uploading files...", color: "text-blue-600" },
    processing: { icon: Database, text: "Processing data...", color: "text-yellow-600" },
    analyzing: { icon: BarChart3, text: "Analyzing patterns...", color: "text-purple-600" },
    completing: { icon: Zap, text: "Finalizing results...", color: "text-green-600" }
  }

  const current = stages[stage]
  const Icon = current.icon

  return (
    <div className="flex flex-col items-center gap-6 py-8">
      <div className="relative">
        <div className={cn(
          "w-20 h-20 border-4 border-gray-200 rounded-full animate-spin",
          current.color.replace('text-', 'border-').replace('-600', '-300')
        )}>
          <div className={cn(
            "absolute top-1 left-1 w-3 h-3 rounded-full",
            current.color.replace('text-', 'bg-')
          )} />
        </div>
        <div className="absolute inset-0 flex items-center justify-center">
          <Icon className={cn("w-8 h-8", current.color)} />
        </div>
      </div>
      
      <div className="text-center max-w-sm">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{current.text}</h3>
        <div className="w-64 bg-gray-200 rounded-full h-2 overflow-hidden">
          <div 
            className={cn(
              "h-full rounded-full transition-all duration-1000 ease-out",
              current.color.replace('text-', 'bg-')
            )}
            style={{ 
              width: stage === "uploading" ? "25%" : 
                     stage === "processing" ? "50%" : 
                     stage === "analyzing" ? "75%" : "100%" 
            }}
          />
        </div>
        <p className="text-sm text-gray-500 mt-3">
          This may take a few moments depending on file size
        </p>
      </div>
    </div>
  )
}

export function PageLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="relative mb-8">
          <div className="w-24 h-24 border-4 border-blue-200 rounded-full animate-spin">
            <div className="absolute top-2 left-2 w-4 h-4 bg-blue-600 rounded-full" />
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <BarChart3 className="w-10 h-10 text-blue-600" />
          </div>
        </div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Loading Dashboard</h2>
        <p className="text-gray-600">Preparing your warehouse intelligence interface...</p>
      </div>
    </div>
  )
}

export function InlineLoading({ text = "Loading..." }: { text?: string }) {
  return (
    <div className="flex items-center gap-2 text-gray-600">
      <Loader2 className="w-4 h-4 animate-spin" />
      <span className="text-sm font-medium">{text}</span>
    </div>
  )
}

// Alias for backward compatibility
export const LoadingSpinner = Loading