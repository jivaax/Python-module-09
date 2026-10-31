from enum import Enum
from pydantic import BaseModel, Field, model_validator, ValidationError
from datetime import datetime


class Rank(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission(self) -> "SpaceMission":
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")
        if self.duration_days > 365:
            crew_experience = sum(
                member.years_experience >= 5 for member in self.crew
            )
            if crew_experience < len(self.crew) / 2:
                raise ValueError(
                    "For missions longer than 1 year, 50% of crew members "
                    "must have at least 5 years of experience"
                )
        if not any(
            member.rank in [Rank.COMMANDER, Rank.CAPTAIN]
            for member in self.crew
        ):
            raise ValueError(
                "Crew members must have at least one of the following "
                "ranks: Commander or Captain"
            )
        for member in self.crew:
            if member.is_active is False:
                raise ValueError(
                    "All crew members must be active for the mission"
                )
        return self


def main() -> None:
    crew_members = [
        CrewMember(
            member_id="C001",
            name="Sarah Connor",
            rank=Rank.COMMANDER,
            age=45,
            years_experience=20,
            specialization="Mission Command"
        ),
        CrewMember(
            member_id="C002",
            name="John Smith",
            rank=Rank.LIEUTENANT,
            age=35,
            years_experience=10,
            specialization="Navigation"
        ),
        CrewMember(
            member_id="C003",
            name="Alice Johnson",
            rank=Rank.OFFICER,
            age=30,
            years_experience=5,
            specialization="Engineering"
        )
    ]
    space_mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date=datetime(2026, 10, 30, 12, 0),
        duration_days=900,
        crew=crew_members,
        budget_millions=2500.0
    )
    print("Space Mission Crew Validation")
    print("===================================")
    print("Valid mission created:")
    print(f"Mission: {space_mission.mission_name}")
    print(f"ID: {space_mission.mission_id}")
    print(f"Destination: {space_mission.destination}")
    print(f"Duration: {space_mission.duration_days} days")
    print(f"Budget: ${space_mission.budget_millions}M")
    print(f"Crew Size: {len(space_mission.crew)}")
    print("Crew Members:")
    for member in space_mission.crew:
        print(
            f"  - {member.name} ({member.rank.value}) - "
            f"{member.specialization}"
        )
    print("\n===================================")
    print("Expected validation error:")
    try:
        SpaceMission(
            mission_id="X2024_MARS",
            mission_name="Mars Colony Establishment",
            destination="Mars",
            launch_date=datetime(2026, 10, 30, 12, 0),
            duration_days=900,
            crew=crew_members,
            budget_millions=2500.0
        )
    except ValidationError as e:
        print(e)


if __name__ == "__main__":
    main()
