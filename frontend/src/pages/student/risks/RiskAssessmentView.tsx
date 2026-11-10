import { Fragment, type ReactNode } from "react";
import type { RiskAssessmentEntryResponse, RiskDomainInfo } from "@/lib/api/types";
import { cn } from "@/lib/utils/cn";
import {
  COLUMN_TITLES,
  groupByCategory,
  levelOption,
} from "@/pages/student/risks/riskLevels";

export function RiskAssessmentView({
  domains,
  entry,
}: {
  domains: RiskDomainInfo[];
  entry: RiskAssessmentEntryResponse;
}): ReactNode {
  const byDomain = new Map(entry.items.map((item) => [item.domain, item]));

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="bg-brand-600 text-white">
            {COLUMN_TITLES.map((title) => (
              <th key={title} className="p-2 text-start font-medium">
                {title}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {groupByCategory(domains).map((group) => (
            <Fragment key={group.category}>
              <tr className="bg-brand-50">
                <td
                  colSpan={COLUMN_TITLES.length}
                  className="p-2 font-semibold text-brand-700"
                >
                  {group.label}
                </td>
              </tr>
              {group.domains.map((domain) => {
                const item = byDomain.get(domain.domain);
                const level = levelOption(item?.level ?? null);
                return (
                  <tr key={domain.domain} className="border-b border-slate-200 align-top">
                    <td className="w-1/5 p-2 font-medium text-ink">{domain.label}</td>
                    <td className="whitespace-pre-wrap p-2 text-ink">{item?.nature}</td>
                    <td className="p-2">
                      {level && (
                        <span
                          className={cn(
                            "inline-block whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-medium",
                            level.className
                          )}
                        >
                          {level.label}
                        </span>
                      )}
                    </td>
                    <td className="whitespace-pre-wrap p-2 text-ink">
                      {item?.intervention_plan}
                    </td>
                    <td className="p-2 text-ink">
                      {item?.responsible.map((member) => member.full_name).join(", ")}
                    </td>
                  </tr>
                );
              })}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
