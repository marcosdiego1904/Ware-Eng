"use client"

import React, { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { AlertTriangle, Loader2, Database } from 'lucide-react'

interface ClearAnomaliesModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  anomaliesCount: number
  isLoading?: boolean
  onConfirm: (dontShowAgain: boolean) => void
  onCancel?: () => void
}

export function ClearAnomaliesModal({
  open,
  onOpenChange,
  anomaliesCount,
  isLoading = false,
  onConfirm,
  onCancel
}: ClearAnomaliesModalProps) {
  const [dontShowAgain, setDontShowAgain] = useState(false)

  const handleConfirm = () => {
    onConfirm(dontShowAgain)
  }

  const handleCancel = () => {
    if (onCancel) {
      onCancel()
    } else {
      onOpenChange(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <div className="flex items-center gap-3 mb-3">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-warning/10">
              <Database className="w-6 h-6 text-warning" />
            </div>
            <div>
              <DialogTitle className="text-xl font-semibold">Clear Previous Anomalies?</DialogTitle>
              <DialogDescription className="text-sm text-muted-foreground mt-1">
                This will help keep your data clean and accurate
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="py-4">
          <div className="bg-muted/50 rounded-lg p-4 mb-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-warning mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-foreground mb-2">
                  You have <span className="font-bold text-primary">{anomaliesCount}</span> unresolved anomalies from previous analyses.
                </p>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  Running a new analysis will clear these and show only current warehouse issues.
                  This helps provide accurate insights and keeps your dashboard focused on what needs attention now.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <p className="text-sm font-medium text-green-800 mb-1">
              ✅ Recommended Approach
            </p>
            <p className="text-xs text-green-700">
              Clearing previous anomalies provides cleaner data analysis and meaningful before/after comparisons.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 py-3 border-t">
          <Checkbox
            id="dont-show-again"
            checked={dontShowAgain}
            onCheckedChange={(checked) => setDontShowAgain(checked as boolean)}
            disabled={isLoading}
          />
          <label
            htmlFor="dont-show-again"
            className="text-sm text-muted-foreground cursor-pointer"
          >
            Don't show this warning again (save preference)
          </label>
        </div>

        <DialogFooter className="gap-3">
          <Button
            variant="outline"
            onClick={handleCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            variant="default"
            onClick={handleConfirm}
            disabled={isLoading}
            className="min-w-[140px] bg-primary hover:bg-primary/90"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Clearing...
              </>
            ) : (
              <>
                <Database className="w-4 h-4 mr-2" />
                Clear & Continue
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}