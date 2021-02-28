import lifesaver


class WebConfig(lifesaver.config.Config):
    # Hypercorn config
    http: dict

    # Quart config
    app: dict


class MyConfig(lifesaver.bot.BotConfig):
    web: WebConfig
