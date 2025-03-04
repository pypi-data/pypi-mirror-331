class FastPrometheusError(Exception):
    pass


class NameAlreadyExistsError(FastPrometheusError):
    pass


class ConfigAttributeError(FastPrometheusError):
    pass
