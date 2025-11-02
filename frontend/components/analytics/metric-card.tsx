"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import { TrendingUp, TrendingDown, Minus, ArrowUp, ArrowDown } from "lucide-react"

interface MetricCardProps {
  title: string
  value: string | number
  description?: string
  trend?: {
    value: number
    label?: string
    direction?: 'up' | 'down' | 'neutral'
  }
  icon?: React.ReactNode
  className?: string
  valueClassName?: string
  loading?: boolean
}

export function MetricCard({
  title,
  value,
  description,
  trend,
  icon,
  className,
  valueClassName,
  loading = false
}: MetricCardProps) {
  const getTrendIcon = () => {
    if (!trend) return null

    const iconClass = "w-4 h-4"

    if (trend.direction === 'up') {
      return <TrendingUp className={cn(iconClass, "text-green-600")} />
    } else if (trend.direction === 'down') {
      return <TrendingDown className={cn(iconClass, "text-red-600")} />
    } else {
      return <Minus className={cn(iconClass, "text-gray-400")} />
    }
  }

  const getTrendColor = () => {
    if (!trend) return 'text-gray-500'

    if (trend.direction === 'up') return 'text-green-600'
    if (trend.direction === 'down') return 'text-red-600'
    return 'text-gray-500'
  }

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardDescription className="animate-pulse bg-gray-200 h-4 w-24 rounded" />
          <CardTitle className="animate-pulse bg-gray-200 h-8 w-32 rounded mt-2" />
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardDescription className="text-sm font-medium">
              {title}
            </CardDescription>
          </div>
          {icon && (
            <div className="ml-2 text-muted-foreground">
              {icon}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className={cn("text-3xl font-bold", valueClassName)}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </div>

        {(description || trend) && (
          <div className="mt-2 flex items-center gap-2 text-sm">
            {trend && (
              <div className={cn("flex items-center gap-1", getTrendColor())}>
                {getTrendIcon()}
                <span className="font-medium">
                  {trend.value > 0 ? '+' : ''}{trend.value}%
                </span>
                {trend.label && (
                  <span className="text-muted-foreground ml-1">
                    {trend.label}
                  </span>
                )}
              </div>
            )}

            {description && !trend && (
              <p className="text-muted-foreground">
                {description}
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

interface StatCardProps {
  label: string
  value: string | number
  subtext?: string
  icon?: React.ReactNode
  color?: 'blue' | 'green' | 'orange' | 'red' | 'purple' | 'gray'
  loading?: boolean
}

export function StatCard({
  label,
  value,
  subtext,
  icon,
  color = 'blue',
  loading = false
}: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 border-blue-200',
    green: 'bg-green-50 text-green-600 border-green-200',
    orange: 'bg-orange-50 text-orange-600 border-orange-200',
    red: 'bg-red-50 text-red-600 border-red-200',
    purple: 'bg-purple-50 text-purple-600 border-purple-200',
    gray: 'bg-gray-50 text-gray-600 border-gray-200'
  }

  if (loading) {
    return (
      <div className="p-4 rounded-lg border bg-white">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-20 mb-2" />
          <div className="h-8 bg-gray-200 rounded w-24" />
        </div>
      </div>
    )
  }

  return (
    <div className={cn("p-4 rounded-lg border", colorClasses[color])}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium opacity-80 mb-1">
            {label}
          </p>
          <p className="text-2xl font-bold">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </p>
          {subtext && (
            <p className="text-xs opacity-70 mt-1">
              {subtext}
            </p>
          )}
        </div>
        {icon && (
          <div className="ml-2 opacity-60">
            {icon}
          </div>
        )}
      </div>
    </div>
  )
}

interface ComparisonCardProps {
  title: string
  current: number
  previous: number
  unit?: string
  format?: 'number' | 'percentage' | 'currency' | 'time'
  loading?: boolean
}

export function ComparisonCard({
  title,
  current,
  previous,
  unit = '',
  format = 'number',
  loading = false
}: ComparisonCardProps) {
  const formatValue = (val: number): string => {
    switch (format) {
      case 'percentage':
        return `${val.toFixed(1)}%`
      case 'currency':
        return `$${val.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
      case 'time':
        return `${val.toFixed(1)} ${unit || 'min'}`
      default:
        return val.toLocaleString() + (unit ? ` ${unit}` : '')
    }
  }

  const change = previous > 0 ? ((current - previous) / previous) * 100 : 0
  const isImprovement = change > 0
  const isDecline = change < 0

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-32 mb-2" />
            <div className="h-8 bg-gray-200 rounded w-24" />
          </div>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{title}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold mb-2">
          {formatValue(current)}
        </div>

        <div className="flex items-center gap-2 text-sm">
          {isImprovement && (
            <div className="flex items-center gap-1 text-green-600">
              <ArrowUp className="w-4 h-4" />
              <span className="font-medium">+{Math.abs(change).toFixed(1)}%</span>
            </div>
          )}

          {isDecline && (
            <div className="flex items-center gap-1 text-red-600">
              <ArrowDown className="w-4 h-4" />
              <span className="font-medium">-{Math.abs(change).toFixed(1)}%</span>
            </div>
          )}

          {!isImprovement && !isDecline && (
            <div className="flex items-center gap-1 text-gray-500">
              <Minus className="w-4 h-4" />
              <span className="font-medium">No change</span>
            </div>
          )}

          <span className="text-muted-foreground">
            vs. previous period ({formatValue(previous)})
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
