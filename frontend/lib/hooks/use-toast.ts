import { useToastStore } from '@/lib/store-enhanced'

export const useToast = () => {
  const { addToast } = useToastStore()
  
  const toast = (options: {
    title: string
    description?: string
    variant?: 'default' | 'destructive' | 'success' | 'warning' | 'info'
  }) => {
    const type = options.variant === 'destructive' ? 'error' : (options.variant || 'info')
    addToast({
      type: type as 'success' | 'error' | 'warning' | 'info',
      title: options.title,
      description: options.description
    })
  }
  
  return { toast }
}

export const toast = (options: {
  title: string
  description?: string
  variant?: 'default' | 'destructive' | 'success' | 'warning' | 'info'
}) => {
  const { addToast } = useToastStore.getState()
  const type = options.variant === 'destructive' ? 'error' : (options.variant || 'info')
  addToast({
    type: type as 'success' | 'error' | 'warning' | 'info',
    title: options.title,
    description: options.description
  })
}