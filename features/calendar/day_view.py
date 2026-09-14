from models.lesson import Lesson


def render_day_view(app, lessons: list[Lesson]):
    app.build_day_board(lessons)
