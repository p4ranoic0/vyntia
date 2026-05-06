import { cn } from "@/shared/utils/cn"
import { cva, type VariantProps } from "class-variance-authority"

const statusBadgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      variant: {
        success: "bg-success/10 text-success border border-success/20",
        warning: "bg-warning/10 text-warning border border-warning/20",
        error: "bg-destructive/10 text-destructive border border-destructive/20",
        info: "bg-info/10 text-info border border-info/20",
        neutral: "bg-muted text-muted-foreground border border-border",
      },
    },
    defaultVariants: {
      variant: "neutral",
    },
  }
)

interface StatusBadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof statusBadgeVariants> {
  dot?: boolean
}

export function StatusBadge({ className, variant, dot = true, children, ...props }: StatusBadgeProps) {
  return (
    <span className={cn(statusBadgeVariants({ variant, className }))} {...props}>
      {dot && (
        <span
          className={cn(
            "h-1.5 w-1.5 rounded-full",
            variant === "success" && "bg-success",
            variant === "warning" && "bg-warning",
            variant === "error" && "bg-destructive",
            variant === "info" && "bg-info",
            (!variant || variant === "neutral") && "bg-muted-foreground"
          )}
        />
      )}
      {children}
    </span>
  )
}
