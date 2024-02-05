

import inspect
import typing
import typing_extensions

import injector


ConfigureModule = typing.Callable[[injector.Binder], None]


class Bind:
    binder: injector.Binder

    def __init__(self, binder: injector.Binder):
        self.binder = binder

    def value[T](self, type: typing.Type[T], value: T) -> None:
        self.binder.bind(
            type,
            injector.InstanceProvider(value),
            injector.SingletonScope
        )

    def singleton[T](self, callable: typing.Callable[..., T]) -> None:
        if inspect.isclass(callable):
            self.binder.bind(
                callable,
                injector.ClassProvider(injector.inject(callable)),
                injector.SingletonScope
            )
        else:
            annotations = typing_extensions.get_type_hints(callable)
            if "return" in annotations:
                self.binder.bind(
                    annotations["return"],
                    injector.inject(callable),
                    injector.SingletonScope
                )
            else:
                raise Exception(
                    f"callable {callable} doesn't have return type")

    @classmethod
    def module(cls, configure: typing.Callable[["Bind"], None]) -> ConfigureModule:
        def decorated(binder: injector.Binder) -> None:
            configure(cls(binder))
        return decorated

    @staticmethod
    def merge(conf1: ConfigureModule, *conf2: ConfigureModule) -> ConfigureModule:
        def merged(binder: injector.Binder) -> None:
            conf1(binder)
            for conf in conf2:
                conf(binder)
        return merged
