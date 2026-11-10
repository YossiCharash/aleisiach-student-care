import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithClient } from "@/test/renderWithClient";
import { MedicalSummaryTab } from "@/pages/student/MedicalSummaryTab";
import { medicalSummaryApi } from "@/lib/api/endpoints";
import { formatDate } from "@/lib/utils/hebrew";
import { EMPTY_FIELDS } from "@/pages/student/medical/medicalSummaryLayout";
import type {
  MedicalSummaryEntryResponse,
  MedicalSummaryHistoryResponse,
} from "@/lib/api/types";

vi.mock("@/lib/api/endpoints", () => ({
  medicalSummaryApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    archive: vi.fn(),
    pdfUrl: vi.fn(() => ""),
    combinedPdfUrl: vi.fn(() => ""),
  },
}));

const listMock = vi.mocked(medicalSummaryApi.list);
const createMock = vi.mocked(medicalSummaryApi.create);
const updateMock = vi.mocked(medicalSummaryApi.update);
const archiveMock = vi.mocked(medicalSummaryApi.archive);

const blankEntry: MedicalSummaryEntryResponse = {
  id: "e1",
  student_id: "s1",
  summary_date: "2026-11-01",
  author_id: "u1",
  author_name: "מנהלת",
  created_at: "2026-11-01T10:00:00Z",
  updated_at: "2026-11-01T10:00:00Z",
  ...EMPTY_FIELDS,
};

const filledEntry: MedicalSummaryEntryResponse = {
  ...blankEntry,
  allergies: "בוטנים",
  mobility: ["escort", "aids"],
  diet: ["other"],
  diet_other: "ללא גלוטן",
  epilepsy_known: false,
};

function historyOf(
  ...entries: MedicalSummaryEntryResponse[]
): MedicalSummaryHistoryResponse {
  return {
    student_id: "s1",
    student_name: "נועה כהן",
    national_id: "123456782",
    date_of_birth: "2000-05-01",
    address: "רחוב הגפן 3",
    entries,
  };
}

describe("MedicalSummaryTab", () => {
  beforeEach(() => {
    listMock.mockReset();
    createMock.mockReset();
    updateMock.mockReset();
    archiveMock.mockReset();
  });

  it("shows the auto-filled identity and the empty state", async () => {
    listMock.mockResolvedValue(historyOf());

    renderWithClient(<MedicalSummaryTab studentId="s1" />);

    expect(
      await screen.findByText("עדיין לא מולא סיכום מידע רפואי לחניך.")
    ).toBeInTheDocument();
    expect(screen.getByText("נועה כהן")).toBeInTheDocument();
    expect(screen.getByText("123456782")).toBeInTheDocument();
    expect(screen.getByText("רחוב הגפן 3")).toBeInTheDocument();
  });

  it("shows the chosen options and texts of the latest summary", async () => {
    listMock.mockResolvedValue(historyOf(filledEntry));

    renderWithClient(<MedicalSummaryTab studentId="s1" />);

    expect(await screen.findByText("בוטנים")).toBeInTheDocument();
    expect(
      screen.getByText("זקוק לליווי · משתמש בעזרים (הליכון, כסא גלגלים, קביים)")
    ).toBeInTheDocument();
    expect(screen.getByText("אחר: ללא גלוטן")).toBeInTheDocument();
    expect(screen.getByText("לא")).toBeInTheDocument();
  });

  it("lists every dated summary with the newest one open", async () => {
    listMock.mockResolvedValue(
      historyOf(
        { ...filledEntry, id: "e2", summary_date: "2026-11-09", allergies: "חלב" },
        filledEntry
      )
    );

    renderWithClient(<MedicalSummaryTab studentId="s1" />);

    expect(await screen.findByText(formatDate("2026-11-09"))).toBeInTheDocument();
    expect(screen.getByText(formatDate("2026-11-01"))).toBeInTheDocument();
    expect(screen.getByText("חלב")).toBeInTheDocument();
    expect(screen.queryByText("בוטנים")).not.toBeInTheDocument();
    expect(screen.getByText("דוח מרוכז")).toBeInTheDocument();
  });

  it("creates a new dated summary from an empty form", async () => {
    listMock.mockResolvedValue(historyOf());
    createMock.mockResolvedValue(filledEntry);

    renderWithClient(<MedicalSummaryTab studentId="s1" />);

    await userEvent.click(await screen.findByText("סיכום מידע רפואי חדש"));
    await userEvent.type(screen.getByLabelText("רגישויות / אלרגיה ידועה"), "בוטנים");
    await userEvent.click(screen.getByLabelText("זקוק לליווי"));
    await userEvent.click(screen.getByLabelText("מתבטא במילים בודדות"));
    const date = screen.getByLabelText("תאריך הסיכום");
    await userEvent.clear(date);
    await userEvent.type(date, "2026-11-05");
    await userEvent.click(screen.getByText("שמירה"));

    expect(createMock).toHaveBeenCalledTimes(1);
    const [studentId, body] = createMock.mock.calls[0];
    expect(studentId).toBe("s1");
    expect(body.summary_date).toBe("2026-11-05");
    expect(body.allergies).toBe("בוטנים");
    expect(body.mobility).toEqual(["escort"]);
    expect(body.communication).toEqual(["single_words"]);
  });

  it("prefills a new summary from the latest one", async () => {
    listMock.mockResolvedValue(historyOf(filledEntry));
    createMock.mockResolvedValue(filledEntry);

    renderWithClient(<MedicalSummaryTab studentId="s1" />);

    await userEvent.click(await screen.findByText("סיכום מידע רפואי חדש"));
    expect(screen.getByLabelText("רגישויות / אלרגיה ידועה")).toHaveValue("בוטנים");
    expect(screen.getAllByText("מספר זהות")).toHaveLength(1);
    await userEvent.click(screen.getByText("שמירה"));

    const [, body] = createMock.mock.calls[0];
    expect(body.mobility).toEqual(["escort", "aids"]);
    expect(body).not.toHaveProperty("id");
    expect(body).not.toHaveProperty("author_name");
  });

  it("drops retired option values when prefilling a new summary", async () => {
    listMock.mockResolvedValue(
      historyOf({ ...filledEntry, mobility: ["escort", "retired_value"] })
    );
    createMock.mockResolvedValue(filledEntry);

    renderWithClient(<MedicalSummaryTab studentId="s1" />);

    await userEvent.click(await screen.findByText("סיכום מידע רפואי חדש"));
    await userEvent.click(screen.getByText("שמירה"));

    const [, body] = createMock.mock.calls[0];
    expect(body.mobility).toEqual(["escort"]);
  });

  it("edits an existing summary and clears an unticked detail", async () => {
    listMock.mockResolvedValue(historyOf(filledEntry));
    updateMock.mockResolvedValue(filledEntry);

    renderWithClient(<MedicalSummaryTab studentId="s1" />);

    await userEvent.click(await screen.findByText("עריכה"));
    expect(screen.queryByLabelText("תאריך הסיכום")).not.toBeInTheDocument();
    expect(screen.getAllByText("מספר זהות")).toHaveLength(1);
    await userEvent.click(screen.getByLabelText("אחר"));
    await userEvent.click(screen.getByText("שמירה"));

    const [studentId, entryId, body] = updateMock.mock.calls[0];
    expect(studentId).toBe("s1");
    expect(entryId).toBe("e1");
    expect(body.diet).toEqual([]);
    expect(body.diet_other).toBe("");
  });

  it("archives a summary after confirmation", async () => {
    listMock.mockResolvedValue(historyOf(filledEntry));
    archiveMock.mockResolvedValue(filledEntry);

    renderWithClient(<MedicalSummaryTab studentId="s1" />);

    await userEvent.click(await screen.findByText("מחיקה"));
    await userEvent.click(screen.getByText("כן, למחוק"));

    expect(archiveMock).toHaveBeenCalledWith("s1", "e1");
  });
});
