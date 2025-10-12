import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-md border px-2.5 py-1 text-xs font-semibold w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
  {
    variants: {
      variant: {
        // Warehouse Primary - Safety Orange
        default:
          "border-transparent bg-primary text-primary-foreground [a&]:hover:bg-[var(--primary-hover)]",
        // Steel Gray
        secondary:
          "border-transparent bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90",
        // Industrial Red - Danger/Critical
        destructive:
          "border-transparent bg-destructive text-white [a&]:hover:bg-[var(--danger-emergency)] focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
        // Emergency variant for urgent items
        emergency:
          "border-transparent bg-[var(--danger-emergency)] text-white [a&]:hover:bg-destructive focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40",
        // Warehouse Green - Success
        success:
          "border-transparent bg-success text-success-foreground [a&]:hover:bg-success/90 focus-visible:ring-success/20 dark:focus-visible:ring-success/40",
        // Light success for positive trends
        "success-light":
          "border-transparent bg-[var(--success-light)] text-success [a&]:hover:bg-success/20",
        // Hi-Vis Yellow - Warning
        warning:
          "border-transparent bg-warning text-warning-foreground [a&]:hover:bg-[var(--warning-caution)] focus-visible:ring-warning/20 dark:focus-visible:ring-warning/40",
        // Caution for medium priority
        caution:
          "border-transparent bg-[var(--warning-caution)] text-warning-foreground [a&]:hover:bg-warning/90",
        // Standard outline
        outline:
          "text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground",
        // Neutral/muted for low priority
        muted:
          "border-transparent bg-muted text-muted-foreground [a&]:hover:bg-muted/80",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

function Badge({
  className,
  variant,
  asChild = false,
  ...props
}: React.ComponentProps<"span"> &
  VariantProps<typeof badgeVariants> & { asChild?: boolean }) {
  const Comp = asChild ? Slot : "span"

  return (
    <Comp
      data-slot="badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    />
  )
}

export { Badge, badgeVariants }
