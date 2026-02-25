"""
SoyAdmin 아이콘 — QtAwesome 기반, 테마 색상과 연동.

사용 가능한 아이콘 세트 (prefix.아이콘이름):
- Font Awesome 6: fa6 (regular), fa6s (solid), fa6b (brands)
  예: fa6s.shield-halved, fa6s.user-shield, fa6s.gear
- Font Awesome 5: fa5, fa5s, fa5b
- Material Design: mdi6, mdi  예: mdi6.cog
- Phosphor: ph  예: ph.gear
- Remix Icon: ri  예: ri.settings-3-fill
- Codicons: msc

색상은 theme.TEXT_SECONDARY / TEXT_PRIMARY 등과 맞춤.
"""
import qtawesome as qta

from theme import TEXT_PRIMARY, TEXT_SECONDARY


def icon(name: str, color: str | None = None, color_active: str | None = None, **kwargs):
    """테마 기본 색을 쓰는 qta.icon() 래퍼."""
    if color is None:
        color = TEXT_SECONDARY
    if color_active is None:
        color_active = TEXT_PRIMARY
    return qta.icon(name, color=color, color_active=color_active, **kwargs)


# 자주 쓰는 아이콘 (테마 색 적용)
def admin_icon():
    """관리자 모드 버튼용 (방패/설정)."""
    return icon("fa6s.shield-halved")


def settings_icon():
    """설정 버튼용."""
    return icon("fa6s.gear")


def user_icon():
    """사용자/작업자용."""
    return icon("fa6s.user")


def home_icon():
    """홈/메인 화면용."""
    return icon("fa6s.house")
