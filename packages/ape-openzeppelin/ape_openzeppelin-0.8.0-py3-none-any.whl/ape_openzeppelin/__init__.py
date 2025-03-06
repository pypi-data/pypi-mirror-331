from ape import plugins


def __getattr__(name: str):
    if name == "OpenZeppelinDependency":
        from .dependency import OpenZeppelinDependency

        return OpenZeppelinDependency

    raise AttributeError(name)


@plugins.register(plugins.DependencyPlugin)
def dependencies():
    from .dependency import OpenZeppelinDependency

    yield "openzeppelin", OpenZeppelinDependency


__all__ = ["OpenZeppelinDependency"]
