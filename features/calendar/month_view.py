from models.lesson import Lesson


def render_month_view(app, lessons: list[Lesson]):
    app.build_month_board(lessons)
