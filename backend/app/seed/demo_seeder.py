import uuid
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.client.database.tenant_binding import TenantBinding
from backend.app.models.client.institution import Institution
from backend.app.models.client.label import Label
from backend.app.models.client.legal_status import LegalStatus
from backend.app.models.client.meeting_foci_entry import MeetingFociEntry
from backend.app.models.client.meeting_plan_entry import MeetingPlanEntry
from backend.app.models.client.meeting_plan_solution import MeetingPlanSolution
from backend.app.models.client.meeting_rating import MeetingRating
from backend.app.models.client.skill import Skill
from backend.app.models.client.social_note_entry import SocialNoteEntry
from backend.app.models.client.solution import Solution
from backend.app.models.client.student import Student
from backend.app.models.client.student_details import StudentDetails
from backend.app.models.client.team_meeting import TeamMeeting
from backend.app.models.client.user import User
from backend.app.models.client.user_status import UserStatus
from backend.app.models.client.workshop import Workshop
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
        workshops = self._seed_workshops(institution.id)
        self._seed_users(workshops["סדנה א׳"].id, institution.id)
        skills = self._seed_taxonomy(institution.id)
        students = self._seed_students(workshops, institution.id)
        self._seed_meeting(students["נועה כהן"].id, skills, institution.id)
        self._seed_details(students["נועה כהן"].id, institution.id)
        self._seed_social_note(students["נועה כהן"].id, institution.id)

    def _seed_institution(self) -> Institution:
        institution = Institution(name=DEMO_INSTITUTION_NAME, code=DEMO_INSTITUTION_CODE)
        self._session.add(institution)
        self._session.flush()
        TenantBinding.bind(self._session, institution.id)
        return institution

    def _seed_workshops(self, institution_id: uuid.UUID) -> dict[str, Workshop]:
        workshops = {
            name: Workshop(name=name, color=color, institution_id=institution_id)
            for name, color in (("סדנה א׳", "#3F8420"), ("סדנה ב׳", "#85C441"))
        }
        self._session.add_all(workshops.values())
        self._session.flush()
        return workshops

    def _seed_users(self, instructor_workshop_id: uuid.UUID, institution_id: uuid.UUID) -> None:
        for account in ALL_ACCOUNTS:
            workshop_id = instructor_workshop_id if account is INSTRUCTOR else None
            self._session.add(self._build_user(account, workshop_id, institution_id))
        self._session.flush()

    def _build_user(
        self, account: DemoAccount, workshop_id: uuid.UUID | None, institution_id: uuid.UUID
    ) -> User:
        return User(
            full_name=account.full_name,
            email=account.email,
            username=account.username,
            password_hash=self._hasher.hash(DEMO_PASSWORD),
            role=account.role,
            workshop_id=workshop_id,
            status=UserStatus.ACTIVE,
            institution_id=institution_id,
        )

    def _seed_taxonomy(self, institution_id: uuid.UUID) -> dict[str, Skill]:
        communication = self._add_label("תקשורת", 0, institution_id)
        independence = self._add_label("עצמאות", 1, institution_id)

        expression = self._add_skill(
            "הבעה בעל פה",
            communication.id,
            0,
            institution_id,
            green="מביע צרכים ורצונות באופן עצמאי",
            yellow="מביע צרכים בעזרת עידוד והכוונה",
            red="נמנע מהבעה מילולית וזקוק לתיווך מלא",
        )
        listening = self._add_skill(
            "הקשבה בקבוצה",
            communication.id,
            1,
            institution_id,
            green="מקשיב וממתין לתורו באופן עצמאי",
            yellow="מקשיב בהשגחה וזקוק לתזכורות",
            red="מתקשה להקשיב וזקוק להשגחה צמודה",
        )
        organization = self._add_skill(
            "התארגנות בוקר",
            independence.id,
            0,
            institution_id,
            green="מתארגן בבוקר באופן עצמאי",
            yellow="מתארגן בעזרת תזכורות חלקיות",
            red="זקוק לליווי מלא בהתארגנות הבוקר",
        )

        self._add_solution(
            "תרגול יומי מול המראה", expression.id, MeetingRating.YELLOW, institution_id
        )
        self._add_solution(
            "שימוש בכרטיסיות תמונה", expression.id, MeetingRating.RED, institution_id
        )
        self._add_solution("ישיבה בקדמת הקבוצה", listening.id, MeetingRating.YELLOW, institution_id)
        self._add_solution("לוח משימות מצויר", organization.id, MeetingRating.RED, institution_id)
        self._session.flush()

        return {"expression": expression, "listening": listening, "organization": organization}

    def _seed_students(
        self, workshops: dict[str, Workshop], institution_id: uuid.UUID
    ) -> dict[str, Student]:
        students = {
            name: Student(
                full_name=name,
                workshop_id=workshops[workshop_name].id,
                institution_id=institution_id,
            )
            for name, workshop_name in (
                ("נועה כהן", "סדנה א׳"),
                ("איתי לוי", "סדנה א׳"),
                ("מאיה ברק", "סדנה ב׳"),
            )
        }
        self._session.add_all(students.values())
        self._session.flush()
        return students

    def _seed_meeting(
        self, student_id: uuid.UUID, skills: dict[str, Skill], institution_id: uuid.UUID
    ) -> None:
        author = self._find_user(INSTRUCTOR.email)
        assert author is not None
        meeting = TeamMeeting(
            student_id=student_id,
            meeting_date=date(2026, 6, 15),
            summary=(
                "בישיבת הצוות סקרנו את מוקדי הכוח והמוקדים לחיזוק של נועה ואת התוכנית האישית. "
                "סוכם להמשיך בתרגול היומי ולעקוב אחר ההתקדמות בישיבה הבאה."
            ),
            author_id=author.id,
            institution_id=institution_id,
        )
        meeting.foci_entries = [
            self._foci_entry(skills["expression"], MeetingRating.GREEN, 0, institution_id),
            self._foci_entry(skills["listening"], MeetingRating.YELLOW, 1, institution_id),
            self._foci_entry(skills["organization"], MeetingRating.RED, 2, institution_id),
        ]
        meeting.plan_entries = [
            self._plan_entry(
                skills["listening"], MeetingRating.YELLOW, 0, ["ישיבה בקדמת הקבוצה"], institution_id
            ),
            self._plan_entry(
                skills["organization"], MeetingRating.RED, 1, ["לוח משימות מצויר"], institution_id
            ),
        ]
        self._session.add(meeting)
        self._session.flush()

    def _foci_entry(
        self, skill: Skill, rating: MeetingRating, position: int, institution_id: uuid.UUID
    ) -> MeetingFociEntry:
        return MeetingFociEntry(
            skill_id=skill.id,
            skill_name_snapshot=skill.name,
            rating=rating,
            position=position,
            institution_id=institution_id,
        )

    def _plan_entry(
        self,
        skill: Skill,
        rating: MeetingRating,
        position: int,
        solution_texts: list[str],
        institution_id: uuid.UUID,
    ) -> MeetingPlanEntry:
        entry = MeetingPlanEntry(
            skill_id=skill.id,
            skill_name_snapshot=skill.name,
            rating=rating,
            position=position,
            institution_id=institution_id,
        )
        entry.solutions = [
            self._plan_solution(skill.id, text, index, institution_id)
            for index, text in enumerate(solution_texts)
        ]
        return entry

    def _plan_solution(
        self, skill_id: uuid.UUID, text: str, position: int, institution_id: uuid.UUID
    ) -> MeetingPlanSolution:
        solution = self._session.scalars(
            select(Solution).where(Solution.skill_id == skill_id, Solution.text == text)
        ).one()
        return MeetingPlanSolution(
            solution_id=solution.id,
            solution_text_snapshot=text,
            position=position,
            institution_id=institution_id,
        )

    def _seed_details(self, student_id: uuid.UUID, institution_id: uuid.UUID) -> None:
        self._session.add(
            StudentDetails(
                student_id=student_id,
                institution_id=institution_id,
                national_id="000000000",
                date_of_birth=date(2015, 3, 12),
                address="רחוב הדגמה 1, עיר הדגמה",
                home_language="עברית",
                idd_severity="קלה",
                disability_severity="קל-בינוני",
                functioning_level="בינוני",
                additional_diagnoses=["הפרעת קשב וריכוז", "אוטיזם"],
                emergency_contacts=[
                    {"full_name": "הורה לדוגמה", "relationship": "אמא", "phone": "050-0000000"}
                ],
                legal_status=LegalStatus.PARENTS_ARE_GUARDIANS,
                guardians=[{"full_name": "הורה לדוגמה", "relationship": "אמא"}],
                has_allergies_or_dietary=True,
                allergies_dietary=["אלרגיה לבוטנים"],
                takes_regular_medication=True,
                medications=["ריטלין"],
                medication_independence="זקוק לתזכורת והשגחה",
                emergency_protocol='במקרה חירום ליצור קשר עם ההורים ולהזעיק מד"א.',
                assistive_devices=["משקפיים"],
                expression_mode="דיבור מילולי שוטף",
                language_comprehension="מבין הוראות מורכבות",
                previous_institution="גן תקשורת עירוני",
                current_institution="סדנת תקשורת בבית הספר",
                prior_task_experience="סייעה בחלוקת חומרים בסדנה.",
                interests_strengths="אוהבת ציור ומוזיקה; חזקה בזיכרון חזותי.",
                triggers="רעש פתאומי חזק.",
                distress_early_signs="כיסוי אוזניים והימנעות מקשר עין.",
                calming_methods="מעבר לפינה שקטה והאזנה למוזיקה רגועה.",
            )
        )
        self._session.flush()

    def _seed_social_note(self, student_id: uuid.UUID, institution_id: uuid.UUID) -> None:
        manager = self._find_user(MANAGER.email)
        assert manager is not None
        entries = (
            (date(2026, 6, 12), "שיחה ראשונית עם ההורים — התלמידה משתלבת יפה ומראה התקדמות."),
            (date(2026, 8, 30), "מעקב — נצפתה עלייה בביטחון העצמי ובשיתוף הפעולה בסדנה."),
        )
        for note_date, content in entries:
            self._session.add(
                SocialNoteEntry(
                    student_id=student_id,
                    institution_id=institution_id,
                    note_date=note_date,
                    content=content,
                    author_id=manager.id,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
            )
        self._session.flush()

    def _add_label(self, name: str, order: int, institution_id: uuid.UUID) -> Label:
        label = Label(name=name, order=order, institution_id=institution_id)
        self._session.add(label)
        self._session.flush()
        return label

    def _add_skill(
        self,
        name: str,
        label_id: uuid.UUID,
        order: int,
        institution_id: uuid.UUID,
        green: str,
        yellow: str,
        red: str,
    ) -> Skill:
        skill = Skill(
            name=name,
            label_id=label_id,
            order=order,
            institution_id=institution_id,
            green_text=green,
            yellow_text=yellow,
            red_text=red,
        )
        self._session.add(skill)
        self._session.flush()
        return skill

    def _add_solution(
        self, text: str, skill_id: uuid.UUID, rating: MeetingRating, institution_id: uuid.UUID
    ) -> Solution:
        solution = Solution(
            text=text, skill_id=skill_id, rating=rating, institution_id=institution_id
        )
        self._session.add(solution)
        self._session.flush()
        return solution

    def _find_user(self, email: str) -> User | None:
        return self._session.scalars(select(User).where(User.email == email)).one_or_none()
