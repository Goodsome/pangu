from d4_leaderboard.domain.value_objects.skill import Skill
from d4_leaderboard.domain.value_objects.skill_build import SkillBuild


def _skill(codename: str) -> Skill:
    return Skill(sno=1, codename=codename, name=codename)


def test_skill_build_key_is_order_insensitive() -> None:
    a = SkillBuild.from_skills([_skill("whirlwind"), _skill("warcry")])
    b = SkillBuild.from_skills([_skill("warcry"), _skill("whirlwind")])
    assert a is not None and b is not None
    assert a.key == b.key == "warcry+whirlwind"


def test_skill_build_deduplicates_codenames() -> None:
    build = SkillBuild.from_skills([_skill("warcry"), _skill("warcry")])
    assert build is not None
    assert build.codenames == ("warcry",)
    assert build.key == "warcry"


def test_skill_build_empty_skills_returns_none() -> None:
    assert SkillBuild.from_skills([]) is None


def test_skill_build_key_roundtrip() -> None:
    build = SkillBuild.from_skills([_skill("b"), _skill("a"), _skill("c")])
    assert build is not None
    assert SkillBuild.from_key(build.key) == build
