import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { formatDate } from "@/lib/utils/hebrew";
import { RiskAssessmentTab } from "@/pages/student/RiskAssessmentTab";
import { riskAssessmentApi } from "@/lib/api/endpoints";
import type {
  RiskAssessmentEntryResponse,
  RiskAssessmentHistoryResponse,
  RiskDomainInfo,
  UserResponse,
  UserRole,
} from "@/lib/api/types";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/lib/api/endpoints", () => ({
  riskAssessmentApi: {
    list: vi.fn(),
    responsibleCandidates: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    archive: vi.fn(),
    pdfUrl: vi.fn(() => ""),
    combinedPdfUrl: vi.fn(() => ""),
  },
}));

const listMock = vi.mocked(riskAssessmentApi.list);
const candidatesMock = vi.mocked(riskAssessmentApi.responsibleCandidates);
const createMock = vi.mocked(riskAssessmentApi.create);
const updateMock = vi.mocked(riskAssessmentApi.update);

const DOMAINS: RiskDomainInfo[] = [
  {
    domain: "weight",
    category: "medical",
    category_label: "רפואי",
    label: "עודף / חוסר משקל",
  },
  {
    domain: "harm",
    category: "behavioral",
    category_label: "התנהגותי",
    label: "פגיעה עצמית",
  },
];

function signedInAs(role: UserRole): void {
  const user: Partial<UserResponse> = { id: "u1", full_name: "מור", role };
  useAuth.mockReturnValue({ user });
}

function entry(
  overrides: Partial<RiskAssessmentEntryResponse>
): RiskAssessmentEntryResponse {
  return {
    id: "e1",
    student_id: "s1",
    assessment_date: "2026-09-08",
    items: [
      {
        domain: "weight",
        nature: "אוכל מהר",
        level: "high",
        intervention_plan: "תפריט מסודר",
        responsible_user_ids: ["u2"],
        responsible: [{ id: "u2", full_name: "דנה" }],
      },
      {
        domain: "harm",
        nature: "",
        level: null,
        intervention_plan: "",
        responsible_user_ids: [],
        responsible: [],
      },
    ],
    author_id: "u2",
    author_name: "רכזת",
    created_at: "2026-09-08T10:00:00Z",
    updated_at: "2026-09-08T10:00:00Z",
    ...overrides,
  };
}

function history(entries: RiskAssessmentEntryResponse[]): RiskAssessmentHistoryResponse {
  return { student_id: "s1", student_name: "נועה", domains: DOMAINS, entries };
}

describe("RiskAssessmentTab", () => {
  beforeEach(() => {
    useAuth.mockReset();
    listMock.mockReset();
    candidatesMock.mockReset();
    createMock.mockReset();
    updateMock.mockReset();
    candidatesMock.mockResolvedValue([
      { id: "u1", full_name: "מור" },
      { id: "u2", full_name: "דנה" },
    ]);
  });

  it("shows the empty state and the new-table button to an instructor", async () => {
    signedInAs("instructor");
    listMock.mockResolvedValue(history([]));

    renderWithClient(<RiskAssessmentTab studentId="s1" />);

    expect(
      await screen.findByText("עדיין לא מולאה טבלת ניהול סיכונים לתלמיד.")
    ).toBeInTheDocument();
    expect(screen.getByText("טבלת ניהול סיכונים חדשה")).toBeInTheDocument();
  });

  it("shows the latest table grouped by category, older ones collapsed", async () => {
    signedInAs("manager");
    listMock.mockResolvedValue(
      history([entry({ id: "new" }), entry({ id: "old", assessment_date: "2026-01-01" })])
    );

    renderWithClient(<RiskAssessmentTab studentId="s1" />);

    expect(await screen.findByText("אוכל מהר")).toBeInTheDocument();
    expect(screen.getByText("רפואי")).toBeInTheDocument();
    expect(screen.getByText("התנהגותי")).toBeInTheDocument();
    expect(screen.getByText("גבוה")).toBeInTheDocument();
    expect(screen.getByText("דנה")).toBeInTheDocument();
    expect(screen.getByText(formatDate("2026-01-01"))).toBeInTheDocument();
    expect(screen.getAllByText("אוכל מהר")).toHaveLength(1);
  });

  it("hides write actions from a professional teacher", async () => {
    signedInAs("professional_teacher");
    listMock.mockResolvedValue(history([entry({})]));

    renderWithClient(<RiskAssessmentTab studentId="s1" />);

    expect(await screen.findByText("אוכל מהר")).toBeInTheDocument();
    expect(screen.queryByText("עריכה")).not.toBeInTheDocument();
    expect(screen.queryByText("מחיקה")).not.toBeInTheDocument();
    expect(screen.queryByText("טבלת ניהול סיכונים חדשה")).not.toBeInTheDocument();
  });

  it("lets an instructor edit but not delete", async () => {
    signedInAs("instructor");
    listMock.mockResolvedValue(history([entry({})]));

    renderWithClient(<RiskAssessmentTab studentId="s1" />);

    expect(await screen.findByText("עריכה")).toBeInTheDocument();
    expect(screen.queryByText("מחיקה")).not.toBeInTheDocument();
  });

  it("creates a table with nature, level, plan and several responsible users", async () => {
    signedInAs("instructor");
    listMock.mockResolvedValue(history([]));
    createMock.mockResolvedValue(entry({ id: "e2" }));

    renderWithClient(<RiskAssessmentTab studentId="s1" />);

    await userEvent.click(await screen.findByText("טבלת ניהול סיכונים חדשה"));
    await userEvent.type(screen.getByLabelText("מהות הסיכון — פגיעה עצמית"), "מכה בראש");
    await userEvent.selectOptions(
      screen.getByLabelText("רמת סיכון — פגיעה עצמית"),
      "medium"
    );
    await userEvent.type(screen.getByLabelText("תוכנית התערבות — פגיעה עצמית"), "השגחה");
    await userEvent.click(await screen.findByLabelText("מור — אחראי ביצוע לפגיעה עצמית"));
    await userEvent.click(screen.getByLabelText("דנה — אחראי ביצוע לפגיעה עצמית"));
    await userEvent.click(screen.getByText("שמירת הטבלה"));

    expect(createMock).toHaveBeenCalledWith("s1", {
      assessment_date: expect.stringMatching(/^\d{4}-\d{2}-\d{2}$/),
      items: [
        {
          domain: "weight",
          nature: "",
          level: null,
          intervention_plan: "",
          responsible_user_ids: [],
        },
        {
          domain: "harm",
          nature: "מכה בראש",
          level: "medium",
          intervention_plan: "השגחה",
          responsible_user_ids: ["u1", "u2"],
        },
      ],
    });
  });

  it("edits an existing table without sending response-only fields", async () => {
    signedInAs("manager");
    listMock.mockResolvedValue(history([entry({})]));
    updateMock.mockResolvedValue(entry({}));

    renderWithClient(<RiskAssessmentTab studentId="s1" />);

    await userEvent.click(await screen.findByText("עריכה"));
    await userEvent.selectOptions(
      screen.getByLabelText("רמת סיכון — עודף / חוסר משקל"),
      "low"
    );
    await userEvent.click(screen.getByText("שמירה"));

    const request = updateMock.mock.calls[0][2];
    expect(updateMock.mock.calls[0][1]).toBe("e1");
    expect(request.items[0]).toEqual({
      domain: "weight",
      nature: "אוכל מהר",
      level: "low",
      intervention_plan: "תפריט מסודר",
      responsible_user_ids: ["u2"],
    });
  });
});
