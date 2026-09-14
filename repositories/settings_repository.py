from models.settings import Settings


class SettingsRepository:
    def get(self) -> Settings:
        return Settings()

    def save(self, settings: Settings):
        return settings
