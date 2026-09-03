import uuid
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.class_entity import ClassEntity
from backend.app.models.client.institution import Institution
from backend.app.models.client.label import Label
from backend.app.models.client.legal_status import LegalStatus
from backend.app.models.client.meeting_entry import MeetingEntry
from backend.app.models.client.meeting_entry_solution import MeetingEntrySolution
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.social_note import SocialNote
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.student_details import StudentDetails
from backend.app.models.client.sub_label import SubLabel
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.models.client.user import User
from backend.app.models.client.user_status import UserStatus
from backend.app.seed.demo_credentials import (
    ALL_ACCOUNTS,
    DEMO_INSTITUTION_CODE,
    DEMO_INSTITUTION_NAME,
    DEMO_PASSWORD,
    INSTRUCTOR,
    MANAGER,
    DemoAccount,
)
from backend.app.utils.service.password_hasher import PasswordHasher


class DemoSeeder:
    def __init__(self, session: Session, password_hasher: PasswordHasher) -> None:
        self._session = session
        self._hasher = password_hasher

    def is_seeded(self) -> bool:
        return self._find_user(MANAGER.email) is not None

    def run(self) -> None:
        if self.is_seeded():
            return
        institution = self._seed_institution()
        classes = self._seed_classes(institution.id)
        self._seed_users(classes["כיתה א׳"].id, institution.id)
        skills = self._seed_taxonomy(institution.id)
        students = self._seed_students(classes, institution.id)
        self._seed_meeting(students["נועה כהן"].id, skills)
        self._seed_details(students["נועה כהן"].id)
        self._seed_social_note(students["נועה כהן"].id)

    def _seed_institution(self) -> Institution:
        institution = Institution(name=DEMO_INSTITUTION_NAME, code=DEMO_INSTITUTION_CODE)
        self._session.add(institution)
        self._session.flush()
        TenantBinding.bind(self._session, institution.id)
        return institution

    def _seed_classes(self, institution_id: uuid.UUID) -> dict[str, ClassEntity]:
        classes = {
            name: ClassEntity(name=name, institution_id=institution_id)
            for name in ("כיתה א׳", "כיתה ב׳")
        }
        self._session.add_all(classes.values())
        self._session.flush()
        return classes

    def _seed_users(self, instructor_class_id: uuid.UUID, institution_id: uuid.UUID) -> None:
        for account in ALL_ACCOUNTS:
            class_id = instructor_class_id if account is INSTRUCTOR else None
            self._session.add(self._build_user(account, class_id, institution_id))
        self._session.flush()

    def _build_user(
        self, account: DemoAccount, class_id: uuid.UUID | None, institution_id: uuid.UUID
    ) -> User:
        return User(
            full_name=account.full_name,
            email=account.email,
            username=account.username,
            password_hash=self._hasher.hash(DEMO_PASSWORD),
            role=account.role,
            class_id=class_id,
            status=UserStatus.ACTIVE,
            institution_id=institution_id,
        )

    def _seed_taxonomy(self, institution_id: uuid.UUID) -> dict[str, Skill]:
        communication = self._add_label("תקשורת", 0, institution_id)
        independence = self._add_label("עצמאות", 1, institution_id)
        verbal = self._add_sub_label("תקשורת מילולית", communication.id, 0, institution_id)
        daily = self._add_sub_label("כישורי יומיום", independence.id, 0, institution_id)

        expression = self._add_skill("הבעה בעל פה", verbal.id, 0, institution_id)
        listening = self._add_skill("הקשבה בקבוצה", verbal.id, 1, institution_id)
        organization = self._add_skill("התארגנות בוקר", daily.id, 0, institution_id)

        self._add_solution("תרגול יומי מול המראה", expression.id, institution_id)
        self._add_solution("שימוש בכרטיסיות תמונה", expression.id, institution_id)
        self._add_solution("ישיבה בקדמת הקבוצה", listening.id, institution_id)
        self._add_solution("לוח משימות מצויר", organization.id, institution_id)
        self._session.flush()

        return {"expression": expression, "listening": listening, "organization": organization}

    def _seed_students(
        self, classes: dict[str, ClassEntity], institution_id: uuid.UUID
    ) -> dict[str, Student]:
        students = {
            name: Student(
                full_name=name,
                class_id=classes[class_name].id,
                institution_id=institution_id,
            )
            for name, class_name in (
                ("נועה כהן", "כיתה א׳"),
                ("איתי לוי", "כיתה א׳"),
                ("מאיה ברק", "כיתה ב׳"),
            )
        }
        self._session.add_all(students.values())
        self._session.flush()
        return students

    def _seed_meeting(self, student_id: uuid.UUID, skills: dict[str, Skill]) -> None:
        author = self._find_user(INSTRUCTOR.email)
        assert author is not None
        meeting = TeamMeeting(student_id=student_id, year=2026, month=6, author_id=author.id)
        meeting.entries = [
            self._entry(skills["expression"], MeetingRating.GREEN, 0, []),
            self._entry(skills["listening"], MeetingRating.YELLOW, 1, ["ישיבה בקדמת הקבוצה"]),
            self._entry(skills["organization"], MeetingRating.RED, 2, ["לוח משימות מצויר"]),
        ]
        self._session.add(meeting)
        self._session.flush()

    def _entry(
        self, skill: Skill, rating: MeetingRating, position: int, solution_texts: list[str]
    ) -> MeetingEntry:
        entry = MeetingEntry(
            skill_id=skill.id,
            skill_name_snapshot=skill.name,
            rating=rating,
            position=position,
        )
        entry.solutions = [
            self._entry_solution(skill.id, text, index) for index, text in enumerate(solution_texts)
        ]
        return entry

    def _entry_solution(
        self, skill_id: uuid.UUID, text: str, position: int
    ) -> MeetingEntrySolution:
        solution = self._session.scalars(
            select(Solution).where(Solution.skill_id == skill_id, Solution.text == text)
        ).one()
        return MeetingEntrySolution(
            solution_id=solution.id, solution_text_snapshot=text, position=position
        )

    def _seed_details(self, student_id: uuid.UUID) -> None:
        self._session.add(
            StudentDetails(
                student_id=student_id,
                national_id="000000000",
                date_of_birth=date(2015, 3, 12),
                address="רחוב הדגמה 1, עיר הדגמה",
                home_language="עברית",
                idd_severity="קלה",
                additional_diagnoses=["הפרעת קשב וריכוז"],
                emergency_contacts=[
                    {"full_name": "הורה לדוגמה", "relationship": "אם", "phone": "050-0000000"}
                ],
                legal_status=LegalStatus.PARENTS_ARE_GUARDIANS,
                guardians=[{"full_name": "הורה לדוגמה", "relationship": "אם"}],
                has_allergies_or_dietary=True,
                allergies_dietary=["אלרגיה לבוטנים"],
                takes_regular_medication=True,
                medications=["ריטלין"],
                medication_independence="זקוק לתזכורת והשגחה",
                emergency_protocol='במקרה חירום ליצור קשר עם ההורים ולהזעיק מד"א.',
                assistive_devices=["משקפיים"],
                expression_mode="דיבור מילולי שוטף",
                language_comprehension="מבין הוראות מורכבות",
                current_or_last_framework="גן תקשורת עירוני",
                prior_task_experience="סייעה בחלוקת חומרים בכיתה.",
                interests_strengths="אוהבת ציור ומוזיקה; חזקה בזיכרון חזותי.",
                triggers="רעש פתאומי חזק.",
                distress_early_signs="כיסוי אוזניים והימנעות מקשר עין.",
                calming_methods="מעבר לפינה שקטה והאזנה למוזיקה רגועה.",
            )
        )
        self._session.flush()

    def _seed_social_note(self, student_id: uuid.UUID) -> None:
        manager = self._find_user(MANAGER.email)
        assert manager is not None
        self._session.add(
            SocialNote(
                student_id=student_id,
                content="הערת עו״ס לדוגמה — התלמידה משתלבת יפה ומראה התקדמות.",
                updated_by=manager.id,
                updated_at=datetime.now(UTC),
            )
        )
        self._session.flush()

    def _add_label(self, name: str, order: int, institution_id: uuid.UUID) -> Label:
        label = Label(name=name, order=order, institution_id=institution_id)
        self._session.add(label)
        self._session.flush()
        return label

    def _add_sub_label(
        self, name: str, label_id: uuid.UUID, order: int, institution_id: uuid.UUID
    ) -> SubLabel:
        sub_label = SubLabel(
            name=name, label_id=label_id, order=order, institution_id=institution_id
        )
        self._session.add(sub_label)
        self._session.flush()
        return sub_label

    def _add_skill(
        self, name: str, sub_label_id: uuid.UUID, order: int, institution_id: uuid.UUID
    ) -> Skill:
        skill = Skill(
            name=name, sub_label_id=sub_label_id, order=order, institution_id=institution_id
        )
        self._session.add(skill)
        self._session.flush()
        return skill

    def _add_solution(self, text: str, skill_id: uuid.UUID, institution_id: uuid.UUID) -> Solution:
        solution = Solution(text=text, skill_id=skill_id, institution_id=institution_id)
        self._session.add(solution)
        self._session.flush()
        return solution

    def _find_user(self, email: str) -> User | None:
        return self._session.scalars(select(User).where(User.email == email)).one_or_none()
