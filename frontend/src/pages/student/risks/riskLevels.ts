import type {
  RiskAssessmentEntryResponse,
  RiskAssessmentRequest,
  RiskDomainInfo,
  RiskItemFields,
  RiskLevel,
} from "@/lib/api/types";

export const RISK_LEVELS: { value: RiskLevel; label: string; className: string }[] = [
  { value: "low", label: "נמוך", className: "bg-green-100 text-green-800" },
  { value: "medium", label: "בינוני", className: "bg-amber-100 text-amber-800" },
  { value: "high", label: "גבוה", className: "bg-red-100 text-red-800" },
  {
    value: "not_relevant",
    label: "לא רלוונטי",
    className: "bg-slate-100 text-slate-600",
  },
];

export function levelOption(
  level: RiskLevel | null
): (typeof RISK_LEVELS)[number] | undefined {
  return RISK_LEVELS.find((option) => option.value === level);
}

export function emptyItem(domainId: string): RiskItemFields {
  return {
    domain_id: domainId,
    nature: "",
    level: null,
    intervention_plan: "",
    responsible_user_ids: [],
  };
}

export function emptyRequest(
  domains: RiskDomainInfo[],
  assessmentDate: string
): RiskAssessmentRequest {
  return {
    assessment_date: assessmentDate,
    items: domains
      .filter((domain) => domain.is_active)
      .map((domain) => emptyItem(domain.id)),
  };
}

export function requestOf(
  domains: RiskDomainInfo[],
  entry: RiskAssessmentEntryResponse
): RiskAssessmentRequest {
  const byDomain = new Map(entry.items.map((item) => [item.domain_id, item]));
  return {
    assessment_date: entry.assessment_date,
    items: domainsFor(domains, entry).map((domain) => {
      const item = byDomain.get(domain.id);
      return item
        ? {
            domain_id: item.domain_id,
            nature: item.nature,
            level: item.level,
            intervention_plan: item.intervention_plan,
            responsible_user_ids: item.responsible_user_ids,
          }
        : emptyItem(domain.id);
    }),
  };
}

export function domainsFor(
  domains: RiskDomainInfo[],
  entry: RiskAssessmentEntryResponse
): RiskDomainInfo[] {
  const used = new Set(entry.items.map((item) => item.domain_id));
  return domains.filter((domain) => domain.is_active || used.has(domain.id));
}

export interface RiskCategoryGroup {
  category: string;
  label: string;
  domains: RiskDomainInfo[];
}

export function groupByCategory(domains: RiskDomainInfo[]): RiskCategoryGroup[] {
  const groups: RiskCategoryGroup[] = [];
  for (const domain of domains) {
    const last = groups[groups.length - 1];
    if (last && last.category === domain.category) {
      last.domains.push(domain);
    } else {
      groups.push({
        category: domain.category,
        label: domain.category_label,
        domains: [domain],
      });
    }
  }
  return groups;
}

export const COLUMN_TITLES = [
  "תחום הסיכון",
  "מהות הסיכון ודוגמא לאירועים שהיו בהקשר לסיכון",
  "רמת סיכון",
  "תוכנית ההתערבות המוצעת ולו״ז",
  "אחראי ביצוע",
];
