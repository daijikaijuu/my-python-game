"""
Образовательная игра на Python 3.12
Разработана в рамках индивидуального итогового проекта
МБОУ "Гимназия №75", г. Казань
"""

from typing import Any, override
import pygame
import math


# Инициализация Pygame
_ = pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60


# Цвета
class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 120, 255)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    BROWN = (139, 69, 19)
    GRAY = (128, 128, 128)
    LIGHT_BLUE = (173, 216, 230)
    PURPLE = (128, 0, 128)
    SKIN = (255, 220, 177)  # Телесный цвет для лица


# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Образовательный платформер на Python 3.12")
clock = pygame.time.Clock()

# Инициализация шрифтов
try:
    font_large = pygame.font.SysFont("Arial", 36, bold=True)
    font_medium = pygame.font.SysFont("Arial", 24)
    font_small = pygame.font.SysFont("Arial", 18)
except:
    font_large = pygame.font.Font(None, 36)
    font_medium = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 18)


class Player(pygame.sprite.Sprite):
    """Класс игрока с физикой движения и анимацией"""

    def __init__(self) -> None:
        super().__init__()
        self.image: pygame.Surface = pygame.Surface((35, 50), pygame.SRCALPHA)
        self._draw_character()
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.center = (100, HEIGHT - 100)
        self.velocity_y: float = 0.0
        self.jumping: bool = False
        self.speed: int = 4
        self.score: int = 0
        self.lives: int = 2  # Две жизни
        self.invincible: bool = False
        self.invincible_timer: int = 0

    def _draw_character(self) -> None:
        """Отрисовка персонажа"""
        # Тело
        pygame.draw.rect(self.image, Colors.BLUE, (5, 10, 25, 30), border_radius=5)
        # Голова (теперь телесного цвета)
        pygame.draw.circle(self.image, Colors.SKIN, (17, 8), 8)
        # Глаза
        pygame.draw.circle(self.image, Colors.BLACK, (13, 6), 2)
        pygame.draw.circle(self.image, Colors.BLACK, (21, 6), 2)
        # Ноги
        pygame.draw.rect(self.image, Colors.BROWN, (8, 40, 8, 10))
        pygame.draw.rect(self.image, Colors.BROWN, (19, 40, 8, 10))

    @override
    def update(self) -> None:
        """Обновление физики персонажа"""
        # Гравитация
        self.velocity_y += 0.5
        self.rect.y += int(self.velocity_y)

        # Ограничение падения
        if self.rect.bottom > HEIGHT - 50:
            self.rect.bottom = HEIGHT - 50
            self.jumping = False
            self.velocity_y = 0

        # Ограничение выхода за границы
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)

        # Обновление таймера неуязвимости
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

    def jump(self) -> None:
        """Прыжок персонажа"""
        if not self.jumping:
            self.velocity_y = -12
            self.jumping = True

    def move_left(self) -> None:
        """Движение влево"""
        self.rect.x -= self.speed

    def move_right(self) -> None:
        """Движение вправо"""
        self.rect.x += self.speed

    def take_damage(self) -> bool:
        """Получение урона, возвращает True если игрок умер"""
        if not self.invincible:
            self.lives -= 1
            self.invincible = True
            self.invincible_timer = 60  # 1 секунда неуязвимости (60 кадров)
            return self.lives <= 0
        return False


class Coin(pygame.sprite.Sprite):
    """Класс собираемой монетки с анимацией"""

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.image: pygame.Surface = pygame.Surface((25, 25), pygame.SRCALPHA)
        self._draw_coin()
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.original_y: int = y

    def _draw_coin(self) -> None:
        """Отрисовка монетки"""
        # Внешний круг
        pygame.draw.circle(self.image, Colors.YELLOW, (12, 12), 12)
        # Внутренний круг
        pygame.draw.circle(self.image, (255, 215, 0), (12, 12), 8)
        # Блики
        pygame.draw.ellipse(self.image, (255, 255, 200), (5, 5, 8, 4))

    @override
    def update(self) -> None:
        """Анимация подпрыгивания"""
        self.rect.y = self.original_y + int(
            math.sin(pygame.time.get_ticks() * 0.005) * 3
        )


class Enemy(pygame.sprite.Sprite):
    """Класс врага с патрулированием по платформе"""

    left_bound: int
    right_bound: int

    def __init__(
        self,
        platform_rect: pygame.Rect,
        speed: int = 2,
        custom_bounds: tuple[int, int] | None = None,
    ):
        super().__init__()
        self.image: pygame.Surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        self._draw_enemy()
        self.rect: pygame.Rect = self.image.get_rect()

        # Позиционируем врага на платформе
        self.platform_rect: pygame.Rect = platform_rect
        self.rect.bottom = platform_rect.top
        self.rect.centerx = platform_rect.centerx

        # Уменьшаем скорость на 30%
        self.speed: int = max(1, int(speed * 0.7))
        self.direction: int = 1

        # Настраиваем границы патрулирования
        if custom_bounds:
            self.left_bound, self.right_bound = custom_bounds
        else:
            self.left_bound = platform_rect.left + 20  # Отступ от края платформы
            self.right_bound = platform_rect.right - 20  # Отступ от края платформы

    def _draw_enemy(self) -> None:
        """Отрисовка врага"""
        # Тело
        pygame.draw.circle(self.image, Colors.RED, (20, 20), 18)
        # Глаза
        pygame.draw.circle(self.image, Colors.WHITE, (14, 14), 5)
        pygame.draw.circle(self.image, Colors.WHITE, (26, 14), 5)
        pygame.draw.circle(self.image, Colors.BLACK, (14, 14), 2)
        pygame.draw.circle(self.image, Colors.BLACK, (26, 14), 2)
        # Рот
        pygame.draw.arc(self.image, Colors.BLACK, (10, 18, 20, 15), 0, math.pi, 2)

    @override
    def update(self) -> None:
        """Обновление патрулирования по платформе"""
        self.rect.x += self.speed * self.direction

        # Изменение направления при достижении границ платформы
        if self.rect.right >= self.right_bound or self.rect.left <= self.left_bound:
            self.direction *= -1

        # Гарантируем, что враг остается на платформе
        self.rect.bottom = self.platform_rect.top


class Platform(pygame.sprite.Sprite):
    """Класс игровой платформы"""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        super().__init__()
        self.image: pygame.Surface = pygame.Surface((width, height))
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self._draw_platform(width, height)

    def _draw_platform(self, width: int, height: int) -> None:
        """Отрисовка платформы с текстурой"""
        self.image.fill(Colors.GRAY)
        pygame.draw.rect(self.image, Colors.BROWN, (0, 0, width, height), 2)
        # Текстура платформы
        for i in range(0, width, 15):
            pygame.draw.line(self.image, (100, 100, 100), (i, 0), (i, height), 1)


class Ground(pygame.sprite.Sprite):
    """Класс земли/основания"""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        super().__init__()
        self.image: pygame.Surface = pygame.Surface((width, height))
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self._draw_ground(width, height)

    def _draw_ground(self, width: int, height: int) -> None:
        """Отрисовка земли с травой"""
        self.image.fill(Colors.BROWN)
        pygame.draw.rect(self.image, Colors.GREEN, (0, 0, width, 10))
        # Детали травы
        for i in range(0, width, 20):
            pygame.draw.line(self.image, (0, 200, 0), (i, 0), (i + 10, -5), 2)


class FinishFlag(pygame.sprite.Sprite):
    """Класс финишного флага"""

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.image: pygame.Surface = pygame.Surface((30, 50), pygame.SRCALPHA)
        self._draw_flag()
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x

    def _draw_flag(self) -> None:
        """Отрисовка флага"""
        # Флагшток
        pygame.draw.rect(self.image, Colors.BROWN, (12, 0, 6, 50))
        # Флаг
        flag_points = [(18, 10), (18, 30), (28, 20)]
        pygame.draw.polygon(self.image, Colors.PURPLE, flag_points)


class Game:
    """Основной класс игры"""

    def __init__(self) -> None:
        self.player: Player | None = None
        self.all_sprites: pygame.sprite.Group[Any] = pygame.sprite.Group()
        self.platforms: pygame.sprite.Group[Any] = pygame.sprite.Group()
        self.coins: pygame.sprite.Group[Any] = pygame.sprite.Group()
        self.enemies: pygame.sprite.Group[Any] = pygame.sprite.Group()
        self.finish_flag: FinishFlag | None = None
        self.coin_positions: list[tuple[int, int]] = []
        self.game_over: bool = False
        self.game_won: bool = False

    def create_level(self) -> None:
        """Создание игрового уровня"""
        # Создание игрока
        self.player = Player()
        self.all_sprites.add(self.player)

        # Создание земли
        ground = Ground(0, HEIGHT - 50, WIDTH, 50)
        self.platforms.add(ground)
        self.all_sprites.add(ground)

        # Платформы (опущены ниже для более легкого доступа)
        platform_data = [
            (100, 450, 200, 20),  # Первая платформа
            (400, 400, 150, 20),  # Вторая платформа
            (200, 300, 100, 20),  # Третья платформа
            (600, 450, 150, 20),  # Четвертая платформа
            (500, 250, 100, 20),  # Пятая платформа (самая верхняя)
        ]

        platforms_list: list[Platform] = []
        for x, y, width, height in platform_data:
            platform = Platform(x, y, width, height)
            self.platforms.add(platform)
            self.all_sprites.add(platform)
            platforms_list.append(platform)

        # Монетки (перенесены с финишной платформы на другие платформы)
        self.coin_positions = [
            (150, 420),
            (250, 420),
            (350, 370),
            (450, 370),
            (550, 420),
            (650, 420),
            # Вместо (550, 220) -> (150, 370)
            (250, 270),
            (150, 370),
            (700, 420),
            (100, 520),
            (300, 520),
            (400, 420),
            (650, 370),  # Вместо (530, 220) -> (650, 370)
        ]

        for x, y in self.coin_positions:
            coin = Coin(x, y)
            self.coins.add(coin)
            self.all_sprites.add(coin)

        # Враги - создаем на конкретных платформах (убрали врага с верхней платформы)
        # Используем индексы платформ из platforms_list
        enemy_data = [
            (platforms_list[0].rect, 2, None),  # На первой платформе
            (platforms_list[1].rect, 3, None),  # На второй платформе
            (platforms_list[3].rect, 2, None),  # На четвертой платформе
        ]

        for platform_rect, speed, custom_bounds in enemy_data:
            enemy = Enemy(platform_rect, speed, custom_bounds)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        # Финишный флаг на верхней платформе
        self.finish_flag = FinishFlag(550, 250)
        self.all_sprites.add(self.finish_flag)

    def draw_background(self) -> None:
        """Отрисовка фона с анимированными облаками"""
        # Небо
        screen.fill(Colors.LIGHT_BLUE)

        # Анимированные облака
        current_time = pygame.time.get_ticks()
        for i in range(5):
            x = (current_time // 50 + i * 200) % (WIDTH + 200) - 100
            y = 80 + i * 40
            pygame.draw.ellipse(screen, Colors.WHITE, (x, y, 100, 40))
            pygame.draw.ellipse(screen, Colors.WHITE, (x + 30, y - 20, 80, 40))
            pygame.draw.ellipse(screen, Colors.WHITE, (x + 60, y, 70, 30))

        # Солнце
        pygame.draw.circle(screen, (255, 255, 100), (700, 80), 40)

    def handle_events(self) -> bool:
        """Обработка событий игры"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and not self.game_over:
                    self.player.jump()
                if event.key == pygame.K_r and (self.game_over or self.game_won):
                    self.restart_game()
        return True

    def check_collisions(self) -> None:
        """Проверка всех столкновений в игре"""
        # Проверка столкновений с платформами (снизу и сверху)
        platform_hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        on_ground = False

        for platform in platform_hits:
            # Столкновение сверху (игрок падает на платформу)
            if (
                self.player.velocity_y > 0
                and self.player.rect.bottom > platform.rect.top
                and self.player.rect.top < platform.rect.top
            ):
                self.player.rect.bottom = platform.rect.top
                self.player.jumping = False
                self.player.velocity_y = 0
                on_ground = True

            # Столкновение снизу (игрок ударяется головой о платформу)
            elif (
                self.player.velocity_y < 0
                and self.player.rect.top < platform.rect.bottom
                and self.player.rect.bottom > platform.rect.bottom
            ):
                self.player.rect.top = platform.rect.bottom
                self.player.velocity_y = 0

        # Если игрок не на земле и не на платформе, он в воздухе
        if not on_ground and self.player.rect.bottom < HEIGHT - 50:
            self.player.jumping = True

    def update_game_state(self) -> None:
        """Обновление состояния игры"""
        if self.game_over or self.game_won:
            return

        # Обработка управления
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.move_left()
        if keys[pygame.K_RIGHT]:
            self.player.move_right()

        # Обновление объектов
        self.player.update()
        self.enemies.update()
        self.coins.update()

        # Проверка столкновений
        self.check_collisions()

        # Сбор монеток
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for _ in coin_hits:
            self.player.score += 10

        # Столкновение с врагами
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if enemy_hits:
            if self.player.take_damage():
                self.game_over = True

        # Проверка достижения финиша
        if self.finish_flag and pygame.sprite.collide_rect(
            self.player, self.finish_flag
        ):
            self.game_won = True

    def draw_ui(self) -> None:
        """Отрисовка пользовательского интерфейса"""
        # Счет
        score_text = font_medium.render(
            f"Очки: {self.player.score}", True, Colors.BLACK
        )
        screen.blit(score_text, (10, 10))

        # Жизни
        lives_text = font_medium.render(f"Жизни: {self.player.lives}", True, Colors.RED)
        screen.blit(lives_text, (WIDTH - 120, 10))

        # Управление
        controls_text = font_small.render(
            "Управление: ← → двигаться, ↑ прыжок, R перезапуск", True, Colors.BLACK
        )
        screen.blit(controls_text, (10, HEIGHT - 30))

        # Мигание при неуязвимости
        if self.player.invincible and self.player.invincible_timer % 10 < 5:
            # Создаем полупрозрачную поверхность для мигания
            blink_surface = pygame.Surface(
                (self.player.rect.width, self.player.rect.height), pygame.SRCALPHA
            )
            blink_surface.fill((255, 255, 255, 128))
            screen.blit(blink_surface, self.player.rect)

    def draw_game_over(self) -> None:
        """Отрисовка экрана завершения игры"""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        game_over_text = font_large.render("ИГРА ОКОНЧЕНА!", True, Colors.RED)
        restart_text = font_medium.render("Нажми R для перезапуска", True, Colors.WHITE)

        screen.blit(
            game_over_text,
            (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50),
        )
        screen.blit(
            restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10)
        )

    def draw_victory(self) -> None:
        """Отрисовка экрана победы"""
        # Определение количества звезд
        total_coins = len(self.coin_positions)
        collected_coins = self.player.score // 10

        if collected_coins >= total_coins * 0.8:
            stars = 3
        elif collected_coins >= total_coins * 0.5:
            stars = 2
        else:
            stars = 1

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Тексты победы
        texts = [
            font_large.render("ПОБЕДА!", True, Colors.GREEN),
            font_medium.render(f"Звезды: {stars}", True, Colors.YELLOW),
            font_medium.render(
                f"Собрано монет: {collected_coins}/{total_coins}", True, Colors.WHITE
            ),
            font_medium.render("Нажми R для перезапуска", True, Colors.WHITE),
        ]

        # Расположение текстов
        y_positions = [
            HEIGHT // 2 - 80,
            HEIGHT // 2 - 30,
            HEIGHT // 2 + 10,
            HEIGHT // 2 + 50,
        ]
        for text, y in zip(texts, y_positions):
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))

        # Отрисовка звезд
        for i in range(stars):
            star_x = WIDTH // 2 - (stars * 25) + i * 50
            self._draw_star(star_x, HEIGHT // 2 + 100)

    def _draw_star(self, x: int, y: int) -> None:
        """Отрисовка звезды"""
        points = [
            (x, y),
            (x + 10, y - 20),
            (x + 20, y),
            (x + 5, y + 10),
            (x + 15, y + 30),
            (x, y + 15),
            (x - 15, y + 30),
            (x - 5, y + 10),
            (x - 20, y),
            (x - 10, y - 20),
        ]
        pygame.draw.polygon(screen, Colors.YELLOW, points)

    def restart_game(self) -> None:
        """Перезапуск игры"""
        self.__init__()
        self.create_level()

    def run(self) -> None:
        """Основной игровой цикл"""
        self.create_level()
        running = True

        while running:
            clock.tick(FPS)

            # Обработка событий
            running = self.handle_events()

            # Обновление состояния игры
            self.update_game_state()

            # Отрисовка
            self.draw_background()
            self.all_sprites.draw(screen)
            self.draw_ui()

            # Отрисовка экранов завершения
            if self.game_over:
                self.draw_game_over()
            elif self.game_won:
                self.draw_victory()

            pygame.display.flip()

        pygame.quit()


def main():
    """Точка входа в программу"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
