import pygame
import pytest

from music_led_streamer.object.image_fragment import ImageFragment

class TestImageFragmentInit:

    @pytest.mark.parametrize(
        "id, x, y, width, height, start_x, start_y, center_x, center_y, image_width, image_height, expected_width, expected_height",  # noqa: E501
        [
            ("happy_path_1", 10, 20, 50, 60, 100, 200, 300, 400, 100, 120, 50, 60),  # noqa: E501
            ("happy_path_2", 0, 0, 200, 300, 0, 0, 100, 100, 200, 300, 200, 300),  # noqa: E501
            ("edge_case_width_too_large", 10, 20, 150, 60, 100, 200, 300, 400, 100, 120, 90, 60),  # noqa: E501
            ("edge_case_height_too_large", 10, 20, 50, 160, 100, 200, 300, 400, 100, 120, 50, 100),  # noqa: E501
            ("edge_case_zero_width_height", 10, 20, 0, 0, 100, 200, 300, 400, 100, 120, 0, 0),  # noqa: E501
        ],
    )
    def test_init(self, id, x, y, width, height, start_x, start_y, center_x, center_y, image_width, image_height, expected_width, expected_height, mocker):  # noqa: E501

        # Arrange
        image_mock = mocker.Mock()
        image_mock.get_width.return_value = image_width
        image_mock.get_height.return_value = image_height
        subsurface_mock = mocker.Mock()
        image_mock.subsurface.return_value = subsurface_mock
        copy_mock = mocker.Mock()
        subsurface_mock.copy.return_value = copy_mock
        mocker.patch("random.uniform", return_value=2.5)

        # Act
        fragment = ImageFragment(image_mock, x, y, width, height, start_x, start_y, center_x, center_y)

        # Assert
        image_mock.subsurface.assert_called_once_with(pygame.Rect(x, y, expected_width, expected_height))  # noqa: E501
        subsurface_mock.copy.assert_called_once()
        assert fragment.original_image == copy_mock
        assert fragment.start_x == start_x
        assert fragment.start_y == start_y
        assert fragment.x == start_x
        assert fragment.y == start_y
        assert fragment.width == expected_width
        assert fragment.height == expected_height
        assert fragment.center_x == center_x
        assert fragment.center_y == center_y
        assert fragment.speed == 2.5
        assert fragment.target_x == start_x
        assert fragment.target_y == start_y
        assert fragment.angle == 0

class TestImageFragmentDraw:

    @pytest.mark.parametrize(
        "id, width, height, angle",
        [
            ("happy_path_1", 100, 50, 30),
            ("happy_path_2", 200, 100, 45),
            ("edge_case_zero_angle", 100, 50, 0),
            ("edge_case_negative_angle", 100, 50, -45),
            ("edge_case_360_angle", 100, 50, 360),
        ],
    )
    def test_draw_happy_path(self, id, width, height, angle, mocker):

        # Arrange
        screen_mock = mocker.Mock()
        image_mock = mocker.Mock()
        image_mock.get_width.return_value = width
        image_mock.get_height.return_value = height
        rotated_image_mock = mocker.Mock()
        mocker.patch("pygame.transform.rotate", return_value=rotated_image_mock)
        mocker.patch("pygame.image.load", return_value=image_mock)
        rect_mock = mocker.Mock()
        rect_mock.topleft = (0, 0)
        mocker.patch("pygame.Surface.get_rect", return_value=rect_mock)
        fragment = ImageFragment("test_image.png", 0, 0)
        fragment.angle = angle

        # Act
        fragment.draw(screen_mock)

        # Assert
        pygame.transform.rotate.assert_called_once_with(image_mock, angle)
        pygame.Surface.get_rect.assert_called_once_with(center=(fragment.x + fragment.width // 2, fragment.y + fragment.height // 2))
        screen_mock.blit.assert_called_once_with(rotated_image_mock, rect_mock.topleft)

    @pytest.mark.parametrize(
        "id, exception",
        [
            ("error_case_invalid_image_path", FileNotFoundError),
        ],
    )
    def test_draw_error_cases(self, id, exception, mocker):

        # Arrange
        mocker.patch("pygame.image.load", side_effect=exception)

        # Act & Assert
        with pytest.raises(exception):
            ImageFragment("invalid_path.png", 0, 0)
            
class TestImageFragmentUpdate:

    @pytest.mark.parametrize(
        "id, bass, midrange, treble, base_fragment_speed, space_expansion_factor, rotate_expansion_factor, expected_x, expected_y, expected_angle",
        [
            ("happy_path_1", 10, 5, 2, 3, 2, 25, 10.0, 11.0, 125),  # noqa: E501
            ("happy_path_2", 0, 0, 0, 0, 0, 0, 0.0, 0.0, 0),
            ("edge_case_max_values", 100, 100, 100, 100, 100, 100, 10000.0, 10100.0, 10000),  # noqa: E501
            ("edge_case_negative_values", -10, -5, -2, -3, -2, -25, 10.0, 5.0, -125),  # noqa: E501
        ],
    )
    def test_update_happy_path(self, id, bass, midrange, treble, base_fragment_speed, space_expansion_factor, rotate_expansion_factor, expected_x, expected_y, expected_angle):  # noqa: E501
        # Arrange
        fragment = ImageFragment("test_image.png", 0, 0, center_x=50, center_y=50)
        fragment.x = 0.0
        fragment.y = 0.0
        fragment.target_x = 0.0
        fragment.target_y = 0.0
        fragment.start_x = 100
        fragment.start_y = 100

        # Act
        fragment.update(bass, midrange, treble, base_fragment_speed, space_expansion_factor, rotate_expansion_factor)

        # Assert
        assert abs(fragment.x - expected_x) < 0.001  # Using a tolerance for floating-point comparisons
        assert abs(fragment.y - expected_y) < 0.001
        assert fragment.angle == expected_angle


    @pytest.mark.parametrize(
        "id, start_x, start_y, center_x, center_y",
        [
            ("edge_case_same_start_center", 50, 50, 50, 50),
            ("edge_case_zero_magnitude", 0, 0, 0, 0),
        ],
    )
    def test_update_edge_cases(self, id, start_x, start_y, center_x, center_y):

        # Arrange
        fragment = ImageFragment("test_image.png", 0, 0, center_x=center_x, center_y=center_y)
        fragment.x = 0.0
        fragment.y = 0.0
        fragment.target_x = 0.0
        fragment.target_y = 0.0
        fragment.start_x = start_x
        fragment.start_y = start_y

        # Act
        fragment.update(10, 5, 2, 3, 2, 25)

        # Assert
        if id == "edge_case_same_start_center":
            assert fragment.x == 20.0
            assert fragment.y == 26.0
        elif id == "edge_case_zero_magnitude":
            assert fragment.x == 0.0
            assert fragment.y == 6.0

        assert fragment.angle == 125
