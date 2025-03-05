from twitch_python_wrapper.enums import Enums


class CheermoteType(Enums):
    GLOBAL_FIRST_PARTY = "global_first_party"
    GLOBAL_THIRD_PARTY = "global_third_party"
    CHANNEL_CUSTOM = "channel_custom"
    DISPLAY_ONLY = "display_only"
    SPONSORED = "sponsored"

class EmoteType(Enums):
    BITSTIER = "bitstier"
    FOLLOWER = "follower"
    SUBSCRIPTIONS = "subscriptions"

class EmoteFormat(Enums):
    ANIMATED = "animated"
    STATIC = "static"

class EmoteThemeMode(Enums):
    DARK = "dark"
    LIGHT = "light"

class SubscriptionStatus(Enums):
    ENABLED = "enabled"
    WEBHOOK_CALLBACK_VERIFICATION_PENDING = "webhook_callback_verification_pending"
    WEBHOOK_CALLBACK_VERIFICATION_FAILED = "webhook_callback_verification_failed"
    NOTIFICATION_FAILURES_EXCEEDED = "notification_failures_exceeded"
    WEBSOCKET_DISCONNECTED = "websocket_disconnected"
    WEBSOCKET_FAILED_PING_PONG = "websocket_failed_ping_pong"
    WEBSOCKET_RECEIVED_INBOUND_TRAFFIC = "websocket_received_inbound_traffic"
    WEBSOCKET_INTERNAL_ERROR = "websocket_internal_error"
    WEBSOCKET_NETWORK_FAILURE = "websocket_network_timeout"
    WEBSOCKET_NETWORK_ERROR = "websocket_network_error"
    WEBSOCKET_FAILED_TO_RECONNECT = "websocket_failed_to_reconnect"

class ContentClassificationLabelId(Enums):
    DEBATED_SOCIAL_ISSUES_AND_POLITICS = "DebatedSocialIssuesAndPolitics"
    DRUGS_INTOXICATION = "DrugsIntoxication"
    GAMBLING = "Gambling"
    MATURE_GAME = "MatureGame"
    PROFANITY_VULGARITY = "ProfanityVulgarity"
    SEXUAL_THEMES = "SexualThemes"
    VIOLENT_GRAPHIC = "ViolentGraphic"

class UserType(Enums):
    ADMIN = "admin"
    GLOBAL_MOD = "global_mod"
    STAFF = "staff"
    NORMAL = ""

class BroadcasterType(Enums):
    AFFILIATE = "affiliate"
    PARTNER = "partner"
    NORMAL = ""

class VideoType(Enums):
    ARCHIVE = "archive"
    HIGHLIGHT = "highlight"
    UPLOAD = "upload"
