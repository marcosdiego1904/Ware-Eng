import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-bold transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
  {
    variants: {
      variant: {
        // Warehouse Primary - Safety Orange "Action-Ready" style
        default:
          "bg-primary text-primary-foreground shadow-sm hover:bg-[var(--primary-hover)] rounded-md",
        // Warehouse Secondary - Steel Gray outline
        secondary:
          "bg-transparent text-secondary border-2 border-secondary font-medium shadow-sm hover:bg-secondary hover:text-secondary-foreground rounded-md",
        // Danger - Industrial Red
        destructive:
          "bg-destructive text-white shadow-sm hover:bg-[var(--danger-emergency)] focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 rounded-md",
        // Success - Warehouse Green
        success:
          "bg-success text-success-foreground shadow-sm hover:bg-success/90 focus-visible:ring-success/20 dark:focus-visible:ring-success/40 rounded-md",
        // Warning - Hi-Vis Yellow
        warning:
          "bg-warning text-warning-foreground shadow-sm hover:bg-[var(--warning-caution)] focus-visible:ring-warning/20 dark:focus-visible:ring-warning/40 rounded-md",
        // Standard outline
        outline:
          "border bg-background shadow-sm hover:bg-accent hover:text-accent-foreground dark:bg-input/30 dark:border-input dark:hover:bg-input/50 rounded-md",
        // Ghost for minimal actions
        ghost:
          "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50 rounded-md",
        // Link style
        link: "text-primary underline-offset-4 hover:underline font-medium",
      },
      size: {
        // Standard sizes
        default: "h-10 px-4 py-2 has-[>svg]:px-3",
        sm: "h-9 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5 text-xs font-medium",
        lg: "h-12 rounded-md px-6 has-[>svg]:px-5 text-base", // 48px - Warehouse safety button
        icon: "size-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant,
  size,
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
  const Comp = asChild ? Slot : "button"

  return (
    <Comp
      data-slot="button"
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}

export { Button, buttonVariants }
