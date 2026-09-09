from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authorize_action_request_context_type_0 import AuthorizeActionRequestContextType0
    from ..models.authorize_action_request_predictions_type_0 import AuthorizeActionRequestPredictionsType0
    from ..models.authorize_action_request_relations_type_0 import AuthorizeActionRequestRelationsType0
    from ..models.tool_call import ToolCall


T = TypeVar("T", bound="AuthorizeActionRequest")


@_attrs_define
class AuthorizeActionRequest:
    """
    Attributes:
        action (ToolCall):
        context (AuthorizeActionRequestContextType0 | None | Unset): Optional contextual facts the policy reasons over
            (e.g. an external signal, a flag, a classifier output). Merged with args as candidate client_facts; args wins on
            a key collision. A required-but-missing contextual fact yields a fail-closed deny. Each value may be a bare
            scalar OR a ``{"value": <v>, "confidence": <c>}`` carrier for per-observation confidence.
        predictions (AuthorizeActionRequestPredictionsType0 | None | Unset): Optional VERIFIED-PREDICTION REFERENCES as
            a {role: {model_id, as_of}} map. Each role references a persisted PredictionRecord the PLATFORM produced+stored;
            the platform fetches the SCOPED (org+owner) trusted row and admits its certified fields to the decision EDB
            keyed `<role>.<field>` (`<role>.value`, `<role>.probability` only if certified, `<role>.fired.<signal>`). The
            caller NEVER supplies the forecast value. FAIL-CLOSED: a missing / un-proof_checked / as_of-mismatched /
            uncertified-probability reference admits no fact, so a policy reading `<role>.<field>` cannot certify a permit
            and the action is denied. Byte-identical when omitted.
        relations (AuthorizeActionRequestRelationsType0 | None | Unset): Optional caller-supplied multi-row SETS for a
            policy that reasons over a declared relation, scoped to this request — e.g. the approvals backing a distinct-
            actor quorum: {"approvals": [{"approver_id": "bob"}, {"approver_id": "carol"}]}. Each row is independently
            certified (declared column / in-domain / ground); the kernel COMPUTES the aggregate (e.g. distinct count) over
            the certified rows — a caller cannot self-attest a count, and duplicate rows fold to one distinct key. Keys
            naming an undeclared relation are ignored. A relation NOT supplied here keeps its ledger/proposed-action-row
            behaviour (byte-identical when omitted).
    """

    action: ToolCall
    context: AuthorizeActionRequestContextType0 | None | Unset = UNSET
    predictions: AuthorizeActionRequestPredictionsType0 | None | Unset = UNSET
    relations: AuthorizeActionRequestRelationsType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.authorize_action_request_context_type_0 import AuthorizeActionRequestContextType0
        from ..models.authorize_action_request_predictions_type_0 import AuthorizeActionRequestPredictionsType0
        from ..models.authorize_action_request_relations_type_0 import AuthorizeActionRequestRelationsType0

        action = self.action.to_dict()

        context: dict[str, Any] | None | Unset
        if isinstance(self.context, Unset):
            context = UNSET
        elif isinstance(self.context, AuthorizeActionRequestContextType0):
            context = self.context.to_dict()
        else:
            context = self.context

        predictions: dict[str, Any] | None | Unset
        if isinstance(self.predictions, Unset):
            predictions = UNSET
        elif isinstance(self.predictions, AuthorizeActionRequestPredictionsType0):
            predictions = self.predictions.to_dict()
        else:
            predictions = self.predictions

        relations: dict[str, Any] | None | Unset
        if isinstance(self.relations, Unset):
            relations = UNSET
        elif isinstance(self.relations, AuthorizeActionRequestRelationsType0):
            relations = self.relations.to_dict()
        else:
            relations = self.relations

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action": action,
            }
        )
        if context is not UNSET:
            field_dict["context"] = context
        if predictions is not UNSET:
            field_dict["predictions"] = predictions
        if relations is not UNSET:
            field_dict["relations"] = relations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authorize_action_request_context_type_0 import AuthorizeActionRequestContextType0
        from ..models.authorize_action_request_predictions_type_0 import AuthorizeActionRequestPredictionsType0
        from ..models.authorize_action_request_relations_type_0 import AuthorizeActionRequestRelationsType0
        from ..models.tool_call import ToolCall

        d = dict(src_dict)
        action = ToolCall.from_dict(d.pop("action"))

        def _parse_context(data: object) -> AuthorizeActionRequestContextType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                context_type_0 = AuthorizeActionRequestContextType0.from_dict(data)

                return context_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AuthorizeActionRequestContextType0 | None | Unset, data)

        context = _parse_context(d.pop("context", UNSET))

        def _parse_predictions(data: object) -> AuthorizeActionRequestPredictionsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                predictions_type_0 = AuthorizeActionRequestPredictionsType0.from_dict(data)

                return predictions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AuthorizeActionRequestPredictionsType0 | None | Unset, data)

        predictions = _parse_predictions(d.pop("predictions", UNSET))

        def _parse_relations(data: object) -> AuthorizeActionRequestRelationsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                relations_type_0 = AuthorizeActionRequestRelationsType0.from_dict(data)

                return relations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AuthorizeActionRequestRelationsType0 | None | Unset, data)

        relations = _parse_relations(d.pop("relations", UNSET))

        authorize_action_request = cls(
            action=action,
            context=context,
            predictions=predictions,
            relations=relations,
        )

        authorize_action_request.additional_properties = d
        return authorize_action_request

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
