from dataclasses import dataclass

@dataclass(frozen=True)
class SubscriptionTierConfig:
    can_send_voice: bool
    voice_limit_seconds: int
    can_send_images: bool
    can_send_files: bool
    can_use_roles: bool
    can_get_miniapp_answers: bool
    can_get_doc_answers: bool
    can_generate_images: bool
    generate_images_file: bool


class SubscriptionConfig:
    _tiers: dict[int, SubscriptionTierConfig] = {
        0: SubscriptionTierConfig(
            can_send_voice=True,
            voice_limit_seconds=15,
            can_send_images=True,
            can_use_roles=False,
            can_send_files=False,
            can_get_miniapp_answers=False,
            can_get_doc_answers=False,
            can_generate_images=False,
            generate_images_file=False,
        ),
        1: SubscriptionTierConfig(
            can_send_voice=True,
            voice_limit_seconds=300,
            can_send_images=True,
            can_use_roles=True,
            can_send_files=True,
            can_get_miniapp_answers=True,
            can_get_doc_answers=True,
            can_generate_images=True,
            generate_images_file=True,
        ),
    }

    @classmethod
    def get(cls, tier_name: str) -> SubscriptionTierConfig:
        if tier_name not in cls._tiers:
            raise ValueError(f"Unknown subscription tier: {tier_name}")
        return cls._tiers[tier_name]
