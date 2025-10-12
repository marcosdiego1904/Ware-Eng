import { Report, ReportDetails } from './reports'
import { ActionCategory } from './action-center-api'

export interface ProgressComparison {
  bestCategory: string
  improvement: number
  isCleared: boolean
  overallChange: number
  trendDirection: 'up' | 'down' | 'stable'
}

/**
 * Calculate the best performing MVP category improvement
 * Compares current vs previous report to find biggest reduction
 */
export function calculateBestMVPImprovement(
  currentCategories: ActionCategory[],
  previousCategories: ActionCategory[]
): { category: string; improvement: number; isCleared: boolean } {

  const mvpCategories = currentCategories.filter(cat => cat.category === 'MVP')

  let bestImprovement = 0
  let bestCategory = ''
  let isCleared = false

  mvpCategories.forEach(currentCat => {
    const previousCat = previousCategories.find(p => p.id === currentCat.id)

    if (!previousCat) return

    // Calculate improvement (reduction in count)
    const reduction = previousCat.count - currentCat.count

    // Skip if no improvement
    if (reduction <= 0) return

    // Calculate percentage improvement
    const percentImprovement = previousCat.count > 0
      ? (reduction / previousCat.count) * 100
      : 0

    // Check if this category is now cleared (zero anomalies)
    const categoryCleared = currentCat.count === 0 && previousCat.count > 0

    // Prefer cleared categories, otherwise take best percentage
    if (categoryCleared || percentImprovement > bestImprovement) {
      bestImprovement = percentImprovement
      bestCategory = currentCat.title
      isCleared = categoryCleared
    }
  })

  return {
    category: bestCategory || 'No improvements',
    improvement: Math.round(bestImprovement),
    isCleared
  }
}

/**
 * Calculate overall improvement across all anomalies
 * Compares total active items between current and previous report
 */
export function calculateOverallImprovement(
  currentTotal: number,
  previousTotal: number
): { percentChange: number; direction: 'up' | 'down' | 'stable' } {

  if (previousTotal === 0) {
    return { percentChange: 0, direction: 'stable' }
  }

  const change = previousTotal - currentTotal
  const percentChange = (change / previousTotal) * 100

  let direction: 'up' | 'down' | 'stable' = 'stable'
  if (percentChange > 2) direction = 'up' // Improvement
  else if (percentChange < -2) direction = 'down' // Getting worse

  return {
    percentChange: Math.round(percentChange),
    direction
  }
}

/**
 * Generate warehouse-appropriate text for improvement display
 */
export function getImprovementDisplayText(
  category: string,
  improvement: number,
  isCleared: boolean
): string {
  if (isCleared) {
    return `${category} Cleared`
  }

  if (improvement > 0) {
    return `${improvement}% Fewer ${category}`
  }

  return 'No improvements'
}

/**
 * Main function to calculate progress comparison
 * Returns data ready for display in Track Progress card
 */
export function calculateProgressComparison(
  currentCategories: ActionCategory[],
  previousCategories: ActionCategory[],
  currentTotal: number,
  previousTotal: number
): ProgressComparison {

  const bestMVP = calculateBestMVPImprovement(currentCategories, previousCategories)
  const overall = calculateOverallImprovement(currentTotal, previousTotal)

  return {
    bestCategory: bestMVP.category,
    improvement: bestMVP.improvement,
    isCleared: bestMVP.isCleared,
    overallChange: overall.percentChange,
    trendDirection: overall.direction
  }
}
