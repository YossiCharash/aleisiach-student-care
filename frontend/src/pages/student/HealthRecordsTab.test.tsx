import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { HealthRecordsTab } from "@/pages/student/HealthRecordsTab";
import { healthRecordsApi } from "@/lib/api/endpoints";
import type {
  HealthDomainInfo,
  HealthRecordHistoryResponse,
  HealthRecordResponse,
  UserResponse,
  UserRole,
} from "@/lib/api/types";

const useAuth = vi.hoisted(() => vi.fn());
vi.mock("@/lib/auth/AuthContext", () => ({ useAuth }));

vi.mock("@/lib/api/endpoints", () => ({
  healthRecordsApi: {
    list: vi.fn(),
    responsibleCandidates: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    archive: vi.fn(),
    pdfUrl: vi.fn(() => ""),
  },
}));

const api = vi.mocked(healthRecordsApi);

const DOMAINS: HealthDomainInfo[] = [
  { id: "physio", name: "פיזיותרפיה", order: 0, is_active: true },
  { id: "speech", name: "קלינאות תקשורת", order: 1, is_active: true },
];

function signedInAs(role: UserRole): void {
  const user: Partial<UserResponse> = { id: "u1", full_name: "מור", role };
  useAuth.mockReturnValue({ user });
}

function record(overrides: Partial<HealthRecordResponse> = {}): HealthRecordResponse {
  return {
    id: "r1",
    student_id: "s1",
    domain_id: "physio",
    record_date: "2026-09-08",
    session_type: "group",
    support_given: "תרגול הליכה",
    responsible_user_ids: ["u2"],
    responsible: [{ id: "u2", full_name: "דנה" }],
    notes: "שיתף פעולה",
    execution_review: "בוצע",
    author_id: "u2",
    author_name: "דנה",
    created_at: "2026-09-08T10:00:00Z",
    updated_at: "2026-09-08T10:00:00Z",
    ...overrides,
  };
}

function history(
  entries: HealthRecordResponse[],
  domains: HealthDomainInfo[] = DOMAINS
): HealthRecordHistoryResponse {
  return { student_id: "s1", student_name: "נועה", domains, entries };
}

describe("HealthRecordsTab", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.pdfUrl.mockReturnValue("");
    api.responsibleCandidates.mockResolvedValue([
      { id: "u1", full_name: "מור" },
      { id: "u2", full_name: "דנה" },
    ]);
  });

  it("shows a table per used domain with the row's columns", async () => {
    signedInAs("manager");
    api.list.mockResolvedValue(history([record()]));

    renderWithClient(<HealthRecordsTab studentId="s1" />);

    expect(await screen.findByText("תחום: פיזיותרפיה")).toBeInTheDocument();
    expect(screen.queryByText("תחום: קלינאות תקשורת")).not.toBeInTheDocument();
    const table = screen.getByRole("table");
    expect(within(table).getByText("קבוצתי")).toBeInTheDocument();
    expect(within(table).getByText("תרגול הליכה")).toBeInTheDocument();
    expect(within(table).getByText("בקרת ביצוע")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /מחיקת שורה/ })).toBeInTheDocument();
  });

  it("explains that domains are missing when the institution has none", async () => {
    signedInAs("manager");
    api.list.mockResolvedValue(history([], []));

    renderWithClient(<HealthRecordsTab studentId="s1" />);

    expect(
      await screen.findByText(/לא הוגדרו תחומי מקצועות הבריאות/)
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /שורת תיעוד חדשה/ })
    ).not.toBeInTheDocument();
  });

  it("lets a professional teacher add a row but not delete one", async () => {
    signedInAs("professional_teacher");
    api.list.mockResolvedValue(history([record()]));
    api.create.mockResolvedValue(record({ id: "r2" }));
    const user = userEvent.setup();

    renderWithClient(<HealthRecordsTab studentId="s1" />);

    await user.click(await screen.findByRole("button", { name: /שורת תיעוד חדשה/ }));
    expect(screen.queryByRole("button", { name: /מחיקת שורה/ })).not.toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText("תחום"), "speech");
    await user.selectOptions(screen.getByLabelText("אישי/קבוצתי"), "individual");
    await user.type(screen.getByLabelText("תמיכה שניתנה"), "תרגול דיבור");
    await user.click(await screen.findByRole("button", { name: "מור" }));
    await user.click(screen.getByRole("button", { name: "הוספת השורה" }));

    expect(api.create).toHaveBeenCalledWith(
      "s1",
      expect.objectContaining({
        domain_id: "speech",
        session_type: "individual",
        support_given: "תרגול דיבור",
        responsible_user_ids: ["u1"],
      })
    );
  });

  it("disables saving an empty row", async () => {
    signedInAs("instructor");
    api.list.mockResolvedValue(history([record()]));
    const user = userEvent.setup();

    renderWithClient(<HealthRecordsTab studentId="s1" />);

    await user.click(await screen.findByRole("button", { name: "הוספת שורה" }));

    expect(screen.getByLabelText("תחום")).toHaveValue("physio");
    expect(screen.getByRole("button", { name: "הוספת השורה" })).toBeDisabled();
  });

  it("edits an existing row", async () => {
    signedInAs("manager");
    api.list.mockResolvedValue(history([record()]));
    api.update.mockResolvedValue(record());
    const user = userEvent.setup();

    renderWithClient(<HealthRecordsTab studentId="s1" />);

    await user.click(await screen.findByRole("button", { name: /עריכת שורה/ }));
    const notes = screen.getByLabelText("הערות");
    await user.clear(notes);
    await user.type(notes, "התקדמות יפה");
    await user.click(screen.getByRole("button", { name: "שמירה" }));

    expect(api.update).toHaveBeenCalledWith(
      "s1",
      "r1",
      expect.objectContaining({ notes: "התקדמות יפה", domain_id: "physio" })
    );
  });
});
