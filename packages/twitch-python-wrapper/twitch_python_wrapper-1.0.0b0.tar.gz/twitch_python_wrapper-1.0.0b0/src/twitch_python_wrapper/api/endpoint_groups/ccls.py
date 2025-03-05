from typing import Literal

import httpx

from twitch_python_wrapper.api.client import APIClient
from twitch_python_wrapper.api.enums import ContentClassificationLabelId
from twitch_python_wrapper.api.objects import ContentClassificationLabel


class CCLs:
    def __init__(self, client: APIClient):
        self.client = client

    def get_content_classification_labels(self,
                                          locale: Literal["bg-BG", "cs-CZ", "da-DK", "da-DK", "de-DE", "el-GR", "en-GB", "en-US", "es-ES", "es-MX", "fi-FI", "fr-FR", "hu-HU", "it-IT", "ja-JP", "ko-KR", "nl-NL", "no-NO", "pl-PL", "pt-BT", "pt-PT", "ro-RO", "ru-RU", "sk-SK", "sv-SE", "th-TH", "tr-TR", "vi-VN", "zh-CN", "zh-TW"] = "en-US") -> tuple[ContentClassificationLabel, ...]:
        """
        `Twitch API Reference <https://dev.twitch.tv/docs/api/reference/#get-content-classification-labels>`_

        Returns information about Twitch content classification labels

        :param locale: Locale of the Content Classification Labels. You may specify a maximum of 1 locale.
            Default: ``"en-US"``. Supported locales: ``"bg-BG", "cs-CZ", "da-DK", "da-DK", "de-DE", "el-GR", "en-GB",
            "en-US", "es-ES", "es-MX", "fi-FI", "fr-FR", "hu-HU", "it-IT", "ja-JP", "ko-KR", "nl-NL", "no-NO", "pl-PL",
            "pt-BT", "pt-PT", "ro-RO", "ru-RU", "sk-SK", "sv-SE", "th-TH", "tr-TR", "vi-VN", "zh-CN", "zh-TW"``

        :return: A tuple that contains information about the available content classification labels
        """

        url = self.client.url + "content_classification_labels"

        req = httpx.get(url,
                        params={"locale": locale},
                        headers=self.client.headers,
                        timeout=self.client.timeout)
        req.raise_for_status()
        res = req.json()["data"]

        labels = list()
        for label in res:
            labels.append(ContentClassificationLabel(
                id=ContentClassificationLabelId(label["id"]),
                description=label["description"],
                name=label["name"])
            )

        return tuple(labels)
