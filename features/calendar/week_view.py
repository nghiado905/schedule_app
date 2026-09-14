from models.lesson import Lesson


def render_week_view(app, lessons: list[Lesson]):
    app.build_week_board(lessons)
