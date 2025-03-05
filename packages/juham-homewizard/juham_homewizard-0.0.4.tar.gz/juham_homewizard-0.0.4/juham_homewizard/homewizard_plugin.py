from typing_extensions import override
from masterpiece import Plugin, Composite
from .homewizardwatermeter import HomeWizardWaterMeter


class HomeWizardPlugin(Plugin):
    """Plugin class for installing and instantiating HomeWizard's water meter into the host application."""

    enable_watermeter: bool = True

    def __init__(self, name: str = "homewizard") -> None:
        """Create and install HomeWizard."""
        super().__init__(name)

    @override
    def install(self, app: Composite) -> None:
        if self.enable_watermeter:
            app.add(HomeWizardWaterMeter())
