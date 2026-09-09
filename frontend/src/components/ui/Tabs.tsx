import {
  createContext,
  forwardRef,
  useContext,
  type ComponentPropsWithoutRef,
  type ElementRef,
} from "react";
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { cn } from "@/lib/utils/cn";

export type TabsVariant = "underline" | "pill";

const TabsVariantContext = createContext<TabsVariant>("underline");

const listVariants: Record<TabsVariant, string> = {
  underline: "flex gap-1 border-b border-slate-200",
  pill: "inline-flex gap-1 rounded-xl bg-slate-100 p-1",
};

const triggerVariants: Record<TabsVariant, string> = {
  underline:
    "-mb-px border-b-2 border-transparent px-4 py-2.5 text-sm font-medium text-ink-muted transition-colors hover:text-ink data-[state=active]:border-brand data-[state=active]:text-brand",
  pill: "rounded-lg px-4 py-2 text-sm font-medium text-ink-muted transition-colors hover:text-ink data-[state=active]:bg-white data-[state=active]:font-semibold data-[state=active]:text-brand-700 data-[state=active]:shadow-sm",
};

export const Tabs = forwardRef<
  ElementRef<typeof TabsPrimitive.Root>,
  ComponentPropsWithoutRef<typeof TabsPrimitive.Root>
>(({ dir = "rtl", ...props }, ref) => (
  <TabsPrimitive.Root ref={ref} dir={dir} {...props} />
));
Tabs.displayName = "Tabs";

export const TabsList = forwardRef<
  ElementRef<typeof TabsPrimitive.List>,
  ComponentPropsWithoutRef<typeof TabsPrimitive.List> & { variant?: TabsVariant }
>(({ className, variant = "underline", ...props }, ref) => (
  <TabsVariantContext.Provider value={variant}>
    <TabsPrimitive.List
      ref={ref}
      className={cn(listVariants[variant], className)}
      {...props}
    />
  </TabsVariantContext.Provider>
));
TabsList.displayName = "TabsList";

export const TabsTrigger = forwardRef<
  ElementRef<typeof TabsPrimitive.Trigger>,
  ComponentPropsWithoutRef<typeof TabsPrimitive.Trigger>
>(({ className, ...props }, ref) => {
  const variant = useContext(TabsVariantContext);
  return (
    <TabsPrimitive.Trigger
      ref={ref}
      className={cn(triggerVariants[variant], className)}
      {...props}
    />
  );
});
TabsTrigger.displayName = "TabsTrigger";

export const TabsContent = forwardRef<
  ElementRef<typeof TabsPrimitive.Content>,
  ComponentPropsWithoutRef<typeof TabsPrimitive.Content>
>(({ className, ...props }, ref) => (
  <TabsPrimitive.Content
    ref={ref}
    className={cn("py-5 focus-visible:outline-none", className)}
    {...props}
  />
));
TabsContent.displayName = "TabsContent";
