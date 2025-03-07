from dataclasses import dataclass
from typing import Dict, List, Optional, cast

from foursquare.map_sdk.api.base import Action
from foursquare.map_sdk.api.enums import ActionType
from foursquare.map_sdk.transport.base import (
    BaseInteractiveTransport,
    BaseNonInteractiveTransport,
    BaseTransport,
)


@dataclass
class TooltipField:
    name: str
    format: Optional[str] = None


@dataclass
class TooltipConfig:
    fields_to_show: Dict[str, List[TooltipField]]
    compare_mode: bool = False
    compare_type: Optional[str] = None


@dataclass
class TooltipInteractionConfig:
    tooltip_config: TooltipConfig
    enabled: bool = True


@dataclass
class TooltipInteractionResponse:
    enabled: bool


###########
# ACTIONS #
###########


class SetTooltipConfig(Action):
    class Meta(Action.Meta):
        args = ["tooltip_interaction_config"]

    type: ActionType = ActionType.SET_TOOLTIP_CONFIG
    tooltip_interaction_config: TooltipInteractionConfig


###########
# METHODS #
###########


class BaseTooltipApiMethods:
    transport: BaseTransport

    def set_tooltip_config(
        self, tooltip_interaction_config: TooltipInteractionConfig
    ) -> Optional[TooltipInteractionResponse]:
        """Sets the tooltip configuration for different datasets.

        Args:
                tooltipInteractionConfig:  Configuration to set
        Returns (widget map only):
            TooltipInteractionResponse(enabled) - Information describing if tooltip is enabled (visible)
        """
        action = SetTooltipConfig(tooltip_interaction_config=tooltip_interaction_config)
        return self.transport.send_action_non_null(
            action=action, response_class=TooltipInteractionResponse
        )


class TooltipApiNonInteractiveMixin(BaseTooltipApiMethods):
    """Tooltip methods that are supported in non-interactive (i.e. pure HTML) maps"""

    transport: BaseNonInteractiveTransport

    def set_tooltip_config(
        self, tooltip_interaction_config: TooltipInteractionConfig
    ) -> None:
        super().set_tooltip_config(
            tooltip_interaction_config=tooltip_interaction_config
        )
        return


class TooltipApiInteractiveMixin(BaseTooltipApiMethods):
    """Tooltip methods that are supported in interactive (i.e. widget) maps"""

    transport: BaseInteractiveTransport

    def set_tooltip_config(
        self, tooltip_interaction_config: TooltipInteractionConfig
    ) -> TooltipInteractionResponse:
        return cast(
            TooltipInteractionResponse,
            super().set_tooltip_config(
                tooltip_interaction_config=tooltip_interaction_config
            ),
        )
