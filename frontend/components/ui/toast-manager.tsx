"use client"

import React from 'react'
import { 
  Toast, 
  ToastClose, 
  ToastDescription, 
  ToastProvider, 
  ToastTitle, 
  ToastViewport 
} from "./toast"
import { useToastStore } from '@/lib/store-enhanced'
import { CheckCircle2, AlertCircle, AlertTriangle, Info } from 'lucide-react'

export function ToastManager() {
  const { toasts, removeToast } = useToastStore()

  const getToastIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-600" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-600" />
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      case 'info':
        return <Info className="h-4 w-4 text-blue-600" />
      default:
        return null
    }
  }

  const getToastVariant = (type: string) => {
    switch (type) {
      case 'success':
        return 'success' as const
      case 'error':
        return 'destructive' as const
      case 'warning':
        return 'warning' as const
      case 'info':
        return 'info' as const
      default:
        return 'default' as const
    }
  }

  return (
    <ToastProvider>
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          variant={getToastVariant(toast.type)}
          onOpenChange={(open) => {
            if (!open) {
              removeToast(toast.id)
            }
          }}
        >
          <div className="flex items-start gap-3">
            {getToastIcon(toast.type)}
            <div className="grid gap-1">
              <ToastTitle>{toast.title}</ToastTitle>
              {toast.description && (
                <ToastDescription>{toast.description}</ToastDescription>
              )}
            </div>
          </div>
          <ToastClose />
        </Toast>
      ))}
      <ToastViewport />
    </ToastProvider>
  )
}