from models.lesson import Lesson


def render_year_view(app, lessons: list[Lesson]):
    app.build_year_board(lessons)
