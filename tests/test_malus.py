"""Tests des malus : rendu dans une QImage, sans fenêtre, à des instants choisis."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from fakes import color_at, make_context, painted_pixels, render
from PySide6.QtGui import QColor, QImage

from chaos_overlay.malus import REGISTRY, mlg_gif
from chaos_overlay.malus.base import EffectContext, Malus
from chaos_overlay.malus.fake_kill_feed import YOU, FakeKillFeed
from chaos_overlay.malus.low_hp import heartbeat
from chaos_overlay.malus.mosquito import SIZE, Mosquito
from chaos_overlay.profiles import PROFILES

ALL_KEYS = list(REGISTRY)
# Instants « au milieu » de chaque effet, hors fondus.
SMALL_EFFECTS = {"fake_crosshair", "blind_spot", "paranoia", "mosquito", "drunk_crosshair", "fake_kill_feed"}


def is_transparent(color: QColor) -> bool:
    return color.alpha() == 0


def is_black(color: QColor) -> bool:
    return color.alpha() == 255 and color.red() < 10 and color.green() < 10 and color.blue() < 10


@pytest.fixture(autouse=True)
def _qt(qapp: object) -> None:
    """Toute la suite a besoin d'une QApplication (polices, images)."""


# --- Contrat commun -------------------------------------------------------------------------


@pytest.mark.parametrize("key", ALL_KEYS)
def test_draws_something_in_the_middle(key: str) -> None:
    malus = REGISTRY[key](make_context())
    image = render(malus, malus.duration_ms // 2)
    step = 2 if key in SMALL_EFFECTS else 8
    assert painted_pixels(image, step) > 0, "le malus n'a rien dessiné"


@pytest.mark.parametrize("key", ALL_KEYS)
def test_draws_nothing_after_its_duration_or_before_start(key: str) -> None:
    malus = REGISTRY[key](make_context())
    assert malus.is_finished(malus.duration_ms)
    assert not malus.is_finished(malus.duration_ms - 1)
    assert painted_pixels(render(malus, malus.duration_ms), step=2) == 0
    assert painted_pixels(render(malus, -1), step=2) == 0


@pytest.mark.parametrize("key", ALL_KEYS)
def test_metadata(key: str) -> None:
    malus_class = REGISTRY[key]
    assert malus_class.label.strip()
    assert malus_class.description.strip()
    assert 500 <= malus_class.default_duration_ms <= 60000


@pytest.mark.parametrize("key", ALL_KEYS)
def test_same_seed_same_image(key: str) -> None:
    """Les tirages sont faits au déclenchement : deux instances de même graine dessinent pareil."""
    first, second = REGISTRY[key](make_context(seed=7)), REGISTRY[key](make_context(seed=7))
    elapsed = first.duration_ms // 2
    assert render(first, elapsed) == render(second, elapsed)


@pytest.mark.parametrize("key", ALL_KEYS)
@pytest.mark.parametrize(("width", "height"), [(1280, 720), (2560, 1440), (3840, 2160)])
def test_other_resolutions_do_not_crash(key: str, width: int, height: int) -> None:
    malus = REGISTRY[key](make_context(width=width, height=height))
    render(malus, malus.duration_ms // 2)


def test_custom_duration() -> None:
    malus = REGISTRY["flashbang"](make_context(), duration_ms=500)
    assert malus.duration_ms == 500
    assert malus.is_finished(500)


class Plain(Malus):
    key = "plain_test"
    label = "Test"
    description = "Test"
    default_duration_ms = 1000
    fade_in_ms = 200
    fade_out_ms = 400

    def paint(self, painter: object, elapsed_ms: int) -> None:  # type: ignore[override]
        pass


def test_opacity_envelope() -> None:
    malus = Plain(make_context())
    assert malus.opacity(0) == 0.0
    assert malus.opacity(100) == pytest.approx(0.5)
    assert malus.opacity(200) == 1.0
    assert malus.opacity(600) == 1.0
    assert malus.opacity(800) == pytest.approx(0.5)
    assert malus.opacity(1000) == 0.0


def test_fades_never_exceed_half_of_a_short_effect() -> None:
    malus = Plain(make_context(), duration_ms=200)
    assert malus.opacity(100) == pytest.approx(1.0)
    assert 0.0 < malus.opacity(50) < 1.0


def test_scale_follows_screen_height() -> None:
    assert make_context(height=1080).scale == 1.0
    assert make_context(width=3840, height=2160).px(15) == 30
    assert make_context(width=1280, height=720).px(1) == 1


# --- Effets un par un (géométrie de la v2 conservée en 1080p) ---------------------------------


def test_flashbang_is_white_then_fades() -> None:
    malus = REGISTRY["flashbang"](make_context())
    start = color_at(render(malus, 0), 960, 540)
    assert (start.red(), start.green(), start.blue(), start.alpha()) == (255, 255, 255, 255)
    assert color_at(render(malus, 2200), 960, 540).alpha() < 255


def test_tunnel_vision_keeps_a_600_px_square() -> None:
    image = render(REGISTRY["tunnel_vision"](make_context()), 4000)
    assert is_transparent(color_at(image, 960, 540))
    assert is_transparent(color_at(image, 960 - 295, 540 - 295))
    assert is_black(color_at(image, 960 - 305, 540))
    assert is_black(color_at(image, 10, 10))


@pytest.mark.parametrize("profile", list(PROFILES))
def test_hud_blocker_masks_every_zone_of_the_profile(profile: str) -> None:
    ctx = make_context(profile=profile)
    image = render(REGISTRY["hud_blocker"](ctx), 6000)
    for x0, y0, x1, y1 in PROFILES[profile].hud_zones:
        assert is_black(color_at(image, (x0 + x1) / 2 * 1920, (y0 + y1) / 2 * 1080))
    assert is_transparent(color_at(image, 960, 540))


def test_valorant_profile_keeps_v2_zones() -> None:
    assert PROFILES["valorant"].hud_zones == ((0.0, 0.0, 0.20, 0.30), (0.75, 0.80, 1.0, 1.0), (0.25, 0.85, 0.45, 1.0))


def test_scanlines_alternate() -> None:
    image = render(REGISTRY["scanlines"](make_context()), 5000)
    assert is_black(color_at(image, 100, 1))
    assert is_transparent(color_at(image, 100, 5))
    assert is_black(color_at(image, 100, 9))


def test_fake_crash_is_blue_full_screen() -> None:
    image = render(REGISTRY["fake_crash"](make_context()), 1000)
    assert color_at(image, 5, 5) == QColor("#003399")


def test_blind_spot_is_a_160_px_disc() -> None:
    image = render(REGISTRY["blind_spot"](make_context()), 4000)
    assert is_black(color_at(image, 960, 540))
    assert is_transparent(color_at(image, 960 + 90, 540))


def test_sniper_scope_hides_everything_but_the_lens() -> None:
    malus = REGISTRY["sniper_scope"](make_context())
    image = render(malus, 4000)
    center = malus.center(4000)  # type: ignore[attr-defined]
    assert is_transparent(color_at(image, center.x() + 100, center.y() + 100))
    assert is_black(color_at(image, 5, 5))


def test_low_hp_reddens_edges_only() -> None:
    image = render(REGISTRY["low_hp"](make_context()), 4000)
    assert is_transparent(color_at(image, 960, 540))
    edge = color_at(image, 2, 2)
    assert edge.alpha() > 0 and edge.red() > edge.green()


def test_heartbeat_stays_in_range() -> None:
    values = [heartbeat(t) for t in range(0, 3000, 10)]
    assert 0.55 <= min(values) and max(values) <= 1.0
    assert heartbeat(0) == pytest.approx(1.0)


def test_kill_feed_adds_one_line_every_700_ms() -> None:
    malus = FakeKillFeed(make_context(seed=3))
    assert len(malus.visible_entries(0)) == 1
    assert len(malus.visible_entries(700)) == 2
    assert len(malus.visible_entries(5900)) == 5
    assert all(killer != victim for killer, _, victim in malus.entries)


def test_kill_feed_often_kills_you() -> None:
    victims = [victim for seed in range(30) for _, _, victim in FakeKillFeed(make_context(seed=seed)).entries]
    assert YOU in victims


def test_drunk_crosshair_moves_around_center() -> None:
    malus = REGISTRY["drunk_crosshair"](make_context(seed=1))
    positions = [malus.position(t) for t in range(0, 10000, 250)]  # type: ignore[attr-defined]
    assert len({(round(p.x()), round(p.y())) for p in positions}) > 10
    assert all(abs(p.x() - 960) <= 111 and abs(p.y() - 540) <= 111 for p in positions)


def test_mosquito_stays_on_screen() -> None:
    ctx = make_context(seed=4, width=800, height=600)
    malus, size = Mosquito(ctx), ctx.px(SIZE)
    for elapsed in range(0, 10000, 30):
        malus.advance_to(elapsed)
        assert 0 <= malus.x <= 800 - size and 0 <= malus.y <= 600 - size


def test_two_mosquitoes_do_not_share_state() -> None:
    """Bug de la v1 : un 2e moustique écrasait l'état du 1er."""
    first, second = Mosquito(make_context(seed=1)), Mosquito(make_context(seed=2))
    first.advance_to(3000)
    second.advance_to(300)
    assert (first.ticks, second.ticks) == (100, 10)
    assert first.rng is not second.rng


# --- GIF ------------------------------------------------------------------------------------


class FakeReader:
    """Faux QImageReader : `count` images de couleurs différentes, puis une image nulle."""

    opened = 0

    def __init__(self, count: int) -> None:
        FakeReader.opened += 1
        self.count = count
        self.position = 0

    def read(self) -> QImage:
        if self.position >= self.count:
            return QImage()
        image = QImage(4, 4, QImage.Format.Format_ARGB32)
        image.fill(QColor(self.position, 0, 0))
        self.position += 1
        return image


def test_gif_stream_reads_in_order_and_loops() -> None:
    FakeReader.opened = 0
    stream = mlg_gif.GifStream(lambda: FakeReader(3))
    frames = [stream.frame(index) for index in range(8)]
    assert [frame.pixelColor(0, 0).red() for frame in frames if frame is not None] == [0, 1, 2, 0, 1, 2, 0, 1]
    assert stream.frame_count == 3


def test_gif_stream_empty_file() -> None:
    stream = mlg_gif.GifStream(lambda: FakeReader(0))
    assert stream.frame(0) is None
    assert stream.frame(5) is None


def test_gif_frame_every_40_ms_and_never_all_in_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    requested: list[int] = []
    malus = REGISTRY["mlg_fullscreen"](make_context())
    assert malus.stream is not None  # type: ignore[attr-defined]
    real_frame = malus.stream.frame  # type: ignore[attr-defined]

    def spy(index: int) -> QImage | None:
        requested.append(index)
        return real_frame(index)

    monkeypatch.setattr(malus.stream, "frame", spy)  # type: ignore[attr-defined]
    for elapsed in (0, 39, 40, 120):
        render(malus, elapsed)
    assert requested == [0, 0, 1, 3]


def test_real_mlg_gif_is_readable() -> None:
    stream = mlg_gif.GifStream(lambda: mlg_gif._open_qt_reader(Path(mlg_gif.resource_path(mlg_gif.GIF_FILENAME))))
    first = stream.frame(0)
    assert first is not None and not first.isNull()
    assert (first.width(), first.height()) == (640, 360)


def test_gif_missing_file_does_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(mlg_gif, "resource_path", lambda name: tmp_path / "absent.gif")
    with caplog.at_level(logging.WARNING):
        malus = REGISTRY["mlg_fullscreen"](make_context())
    assert "introuvable" in caplog.text
    assert painted_pixels(render(malus, 3000)) == 0


def test_effect_context_is_immutable() -> None:
    ctx: EffectContext = make_context()
    with pytest.raises(AttributeError):
        ctx.width = 5  # type: ignore[misc]
