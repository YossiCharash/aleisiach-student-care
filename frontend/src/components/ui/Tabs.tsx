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
  underline: "flex gap-1.5 border-b border-slate-200",
  pill: "inline-flex flex-wrap gap-1 rounded-control border border-slate-200/70 bg-gradient-to-b from-slate-50 to-slate-100 p-1.5 shadow-[inset_0_1px_2px_rgba(38,52,20,0.05)]",
};

const triggerVariants: Record<TabsVariant, string> = {
  underline:
    "relative -mb-px border-b-2 border-transparent px-4 py-3 text-sm font-medium text-ink-muted transition-colors hover:text-ink data-[state=active]:border-brand data-[state=active]:font-semibold data-[state=active]:text-brand-700",
  pill: "relative rounded-[0.6rem] px-4 py-2 text-sm font-medium text-ink-muted outline-none transition-all duration-200 hover:bg-white/60 hover:text-brand-700 focus-visible:ring-2 focus-visible:ring-brand-300 data-[state=active]:bg-white data-[state=active]:font-semibold data-[state=active]:text-brand-700 data-[state=active]:shadow-brand-sm data-[state=active]:ring-1 data-[state=active]:ring-brand-100 data-[state=active]:before:absolute data-[state=active]:before:inset-x-4 data-[state=active]:before:-bottom-px data-[state=active]:before:h-0.5 data-[state=active]:before:rounded-full data-[state=active]:before:bg-gradient-to-r data-[state=active]:before:from-brand-400 data-[state=active]:before:to-accent-400 data-[state=active]:before:content-['']",
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
