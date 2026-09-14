import type { ReactNode } from "react";
import { HelpCircle } from "lucide-react";
import { useAuth } from "@/lib/auth/AuthContext";
import { helpTopics } from "@/lib/help/content";
import { visibleSections } from "@/lib/help/visibleSections";
import type { HelpBlock, HelpSection, HelpTopicId } from "@/lib/help/types";
import { cn } from "@/lib/utils/cn";
import { Button } from "@/components/ui/Button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/Dialog";

const calloutTone: Record<"info" | "tip" | "warn", string> = {
  info: "border-brand-400 bg-brand-50 text-ink",
  tip: "border-accent-400 bg-accent-50 text-ink",
  warn: "border-rating-yellow bg-rating-yellow/10 text-ink",
};

export function HelpButton({
  topic,
  className,
}: {
  topic: HelpTopicId;
  className?: string;
}): ReactNode {
  const { user } = useAuth();
  if (!user) {
    return null;
  }

  const content = helpTopics[topic];
  const sections = visibleSections(content, user.role);
  if (sections.length === 0) {
    return null;
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className={cn("text-ink-muted", className)}
          aria-label="עזרה למסך זה"
        >
          <HelpCircle className="h-4 w-4" />
          עזרה
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{content.title}</DialogTitle>
          {content.intro && <DialogDescription>{content.intro}</DialogDescription>}
        </DialogHeader>
        <div className="space-y-5">
          {sections.map((section) => (
            <HelpSectionView key={section.id} section={section} />
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}

function HelpSectionView({ section }: { section: HelpSection }): ReactNode {
  return (
    <section>
      <h3 className="mb-1.5 text-base font-bold text-ink">{section.title}</h3>
      <div className="space-y-2.5">
        {section.blocks.map((block, index) => (
          <HelpBlockView key={index} block={block} />
        ))}
      </div>
    </section>
  );
}

function HelpBlockView({ block }: { block: HelpBlock }): ReactNode {
  if (block.kind === "text") {
    return <p className="text-sm leading-relaxed text-ink-muted">{block.text}</p>;
  }
  if (block.kind === "bullets") {
    return (
      <ul className="space-y-1.5">
        {block.items.map((item, index) => (
          <li
            key={index}
            className="relative ps-5 text-sm leading-relaxed text-ink-muted before:absolute before:end-auto before:start-1 before:top-2 before:h-1.5 before:w-1.5 before:rounded-sm before:bg-brand before:content-['']"
          >
            {item}
          </li>
        ))}
      </ul>
    );
  }
  if (block.kind === "steps") {
    return (
      <ol className="space-y-2">
        {block.items.map((item, index) => (
          <li key={index} className="flex gap-2.5 text-sm leading-relaxed text-ink-muted">
            <span
              className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brand text-xs font-bold text-white"
              aria-hidden
            >
              {index + 1}
            </span>
            <span>{item}</span>
          </li>
        ))}
      </ol>
    );
  }
  return (
    <div
      className={cn("rounded-control border-s-4 px-3.5 py-2.5", calloutTone[block.tone])}
    >
      {block.title && <p className="text-sm font-bold">{block.title}</p>}
      <p className="text-sm leading-relaxed text-ink-muted">{block.text}</p>
    </div>
  );
}
