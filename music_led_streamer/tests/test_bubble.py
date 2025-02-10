import pytest
import pygame
import random
import math

from music_led_streamer.object.bubble import Bubble

class TestBubble:

    @pytest.mark.parametrize(
        "id, x, y, size, speed, color",
        [
            ("happy_path_1", 10, 20, 30, 2, (255, 0, 0)),
            ("happy_path_2", 0, 0, 10, 1, (0, 255, 0)),
            ("edge_case_zero_size", 10, 20, 0, 2, (0, 0, 255)),
            ("edge_case_negative_speed", 10, 20, 30, -2, (255, 255, 0)),
        ],
    )
    def test_init(self, id, x, y, size, speed, color):

        # Act
        bubble = Bubble(x, y, size, speed, color)

        # Assert
        assert bubble.x == x
        assert bubble.y == y
        assert bubble.size == size
        assert bubble.speed == speed
        assert bubble.color == color

    @pytest.mark.parametrize(
        "id, treble_intensity, expected_y",
        [
            ("happy_path_positive_intensity", 0.5, 15.0),
            ("happy_path_zero_intensity", 0.0, 18.0),
            ("edge_case_negative_intensity", -0.5, 23.0),
            ("edge_case_high_intensity", 2.0, 5.0),

        ],
    )
    def test_move(self, id, treble_intensity, expected_y):
        # Arrange
        bubble = Bubble(10, 20, 30, 2, (255, 0, 0))

        # Act
        bubble.move(treble_intensity)

        # Assert
        assert bubble.y == expected_y


    @pytest.mark.parametrize(
        "id, size",
        [
            ("happy_path_normal_size", 30),
            ("edge_case_zero_size", 0),
            ("edge_case_small_size", 1),
        ],
    )
    def test_draw(self, id, size, mocker):
        # Arrange
        screen_mock = mocker.Mock()
        bubble = Bubble(10, 20, size, 2, (255, 0, 0))
        draw_circle_mock = mocker.patch("pygame.draw.circle")
        surface_mock = mocker.Mock()
        mocker.patch("pygame.Surface", return_value=surface_mock)

        # Act
        bubble.draw(screen_mock)

        # Assert
        pygame.Surface.assert_called_once_with((int(size * 2), int(size * 2)), pygame.SRCALPHA)  # noqa: E501
        if size > 0:
            calls = [mocker.call(surface_mock,(255, 255, 255, 150), (int(size * 0.35), int(size * 0.35)), max(1, int(size * 0.2)))]
            for i in range(int(size), 0, -1):
                alpha = int(255 * (i / size))
                color_with_alpha = (255, 0, 0, alpha)
                calls.append(mocker.call(surface_mock, color_with_alpha, (int(size), int(size)), i))

            draw_circle_mock.assert_has_calls(calls)

        screen_mock.blit.assert_called_once_with(surface_mock, (int(10 - size), int(20 - size)))

