from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.feedback_log_entry_rule_snapshot_type_0 import (
        FeedbackLogEntryRuleSnapshotType0,
    )
    from ..models.feedback_log_entry_scorecard_snapshot_type_0 import (
        FeedbackLogEntryScorecardSnapshotType0,
    )


T = TypeVar("T", bound="FeedbackLogEntry")


@_attrs_define
class FeedbackLogEntry:
    """
    Attributes:
        decision (str):
        id (int):
        platform_id (int):
        decided_at (None | str | Unset):
        reason (None | str | Unset):
        rule_id (int | None | Unset):
        rule_snapshot (FeedbackLogEntryRuleSnapshotType0 | None | Unset):
        scorecard_snapshot (FeedbackLogEntryScorecardSnapshotType0 | None | Unset):
        suggestor_backend (None | str | Unset):
        user_id (int | None | Unset):
    """

    decision: str
    id: int
    platform_id: int
    decided_at: None | str | Unset = UNSET
    reason: None | str | Unset = UNSET
    rule_id: int | None | Unset = UNSET
    rule_snapshot: FeedbackLogEntryRuleSnapshotType0 | None | Unset = UNSET
    scorecard_snapshot: FeedbackLogEntryScorecardSnapshotType0 | None | Unset = UNSET
    suggestor_backend: None | str | Unset = UNSET
    user_id: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.feedback_log_entry_rule_snapshot_type_0 import (
            FeedbackLogEntryRuleSnapshotType0,
        )
        from ..models.feedback_log_entry_scorecard_snapshot_type_0 import (
            FeedbackLogEntryScorecardSnapshotType0,
        )

        decision = self.decision

        id = self.id

        platform_id = self.platform_id

        decided_at: None | str | Unset
        if isinstance(self.decided_at, Unset):
            decided_at = UNSET
        else:
            decided_at = self.decided_at

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        rule_id: int | None | Unset
        if isinstance(self.rule_id, Unset):
            rule_id = UNSET
        else:
            rule_id = self.rule_id

        rule_snapshot: dict[str, Any] | None | Unset
        if isinstance(self.rule_snapshot, Unset):
            rule_snapshot = UNSET
        elif isinstance(self.rule_snapshot, FeedbackLogEntryRuleSnapshotType0):
            rule_snapshot = self.rule_snapshot.to_dict()
        else:
            rule_snapshot = self.rule_snapshot

        scorecard_snapshot: dict[str, Any] | None | Unset
        if isinstance(self.scorecard_snapshot, Unset):
            scorecard_snapshot = UNSET
        elif isinstance(
            self.scorecard_snapshot, FeedbackLogEntryScorecardSnapshotType0
        ):
            scorecard_snapshot = self.scorecard_snapshot.to_dict()
        else:
            scorecard_snapshot = self.scorecard_snapshot

        suggestor_backend: None | str | Unset
        if isinstance(self.suggestor_backend, Unset):
            suggestor_backend = UNSET
        else:
            suggestor_backend = self.suggestor_backend

        user_id: int | None | Unset
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        else:
            user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "decision": decision,
                "id": id,
                "platform_id": platform_id,
            }
        )
        if decided_at is not UNSET:
            field_dict["decided_at"] = decided_at
        if reason is not UNSET:
            field_dict["reason"] = reason
        if rule_id is not UNSET:
            field_dict["rule_id"] = rule_id
        if rule_snapshot is not UNSET:
            field_dict["rule_snapshot"] = rule_snapshot
        if scorecard_snapshot is not UNSET:
            field_dict["scorecard_snapshot"] = scorecard_snapshot
        if suggestor_backend is not UNSET:
            field_dict["suggestor_backend"] = suggestor_backend
        if user_id is not UNSET:
            field_dict["user_id"] = user_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.feedback_log_entry_rule_snapshot_type_0 import (
            FeedbackLogEntryRuleSnapshotType0,
        )
        from ..models.feedback_log_entry_scorecard_snapshot_type_0 import (
            FeedbackLogEntryScorecardSnapshotType0,
        )

        d = dict(src_dict)
        decision = d.pop("decision")

        id = d.pop("id")

        platform_id = d.pop("platform_id")

        def _parse_decided_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        decided_at = _parse_decided_at(d.pop("decided_at", UNSET))

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        def _parse_rule_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        rule_id = _parse_rule_id(d.pop("rule_id", UNSET))

        def _parse_rule_snapshot(
            data: object,
        ) -> FeedbackLogEntryRuleSnapshotType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rule_snapshot_type_0 = FeedbackLogEntryRuleSnapshotType0.from_dict(data)

                return rule_snapshot_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FeedbackLogEntryRuleSnapshotType0 | None | Unset, data)

        rule_snapshot = _parse_rule_snapshot(d.pop("rule_snapshot", UNSET))

        def _parse_scorecard_snapshot(
            data: object,
        ) -> FeedbackLogEntryScorecardSnapshotType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scorecard_snapshot_type_0 = (
                    FeedbackLogEntryScorecardSnapshotType0.from_dict(data)
                )

                return scorecard_snapshot_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FeedbackLogEntryScorecardSnapshotType0 | None | Unset, data)

        scorecard_snapshot = _parse_scorecard_snapshot(
            d.pop("scorecard_snapshot", UNSET)
        )

        def _parse_suggestor_backend(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        suggestor_backend = _parse_suggestor_backend(d.pop("suggestor_backend", UNSET))

        def _parse_user_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        user_id = _parse_user_id(d.pop("user_id", UNSET))

        feedback_log_entry = cls(
            decision=decision,
            id=id,
            platform_id=platform_id,
            decided_at=decided_at,
            reason=reason,
            rule_id=rule_id,
            rule_snapshot=rule_snapshot,
            scorecard_snapshot=scorecard_snapshot,
            suggestor_backend=suggestor_backend,
            user_id=user_id,
        )

        feedback_log_entry.additional_properties = d
        return feedback_log_entry

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
