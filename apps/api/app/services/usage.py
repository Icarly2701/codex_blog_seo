from dataclasses import dataclass


@dataclass(frozen=True)
class UsageState:
    count: int
    limit: int


def can_generate(state: UsageState) -> bool:
    return state.count < state.limit


def increment_count(state: UsageState) -> UsageState:
    return UsageState(count=state.count + 1, limit=state.limit)


def remaining_quota(state: UsageState) -> int:
    return max(state.limit - state.count, 0)
