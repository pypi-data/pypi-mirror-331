from datetime import datetime

from settings_models._combat import SettingsModel, Field
from settings_models.validators import timezone_validator


class EnforcementSettings(SettingsModel):
    """
    Settings for enforcement service
    """
    payment_deadline_hours: int = Field(..., gt=0, le=960,
                                        description="How long someone can pay after exiting parking lot "
                                                    "(not including generally applied additional day)")
    strictness: int = Field(..., description="Strictness level for enforcement. Values to be defined")
    enabled: bool = Field(..., description="If enforcement is enabled")
    last_edited: datetime = Field(..., description="Last time (UTC) when enabled setting was changed")

    last_edited_validator = timezone_validator("last_edited")
