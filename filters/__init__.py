from loader import dp

from .deeplink_filter import IsDeepLink, IsCorrectDeepLink


if __name__ == "filters":
    dp.filters_factory.bind(IsDeepLink)
    dp.filters_factory.bind(IsCorrectDeepLink)
