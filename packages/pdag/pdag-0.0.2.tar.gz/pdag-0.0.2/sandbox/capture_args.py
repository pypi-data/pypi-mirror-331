from dataclasses import dataclass

from pdag.utils import InitArgsRecorder


@dataclass
class C(InitArgsRecorder):
    x: int
    y: str = "default"


@dataclass
class D(C):
    z: float = 0.0


# When the user initializes the classes:
c = C(10)
d = D(10, "hello", 3.14)
d2 = D(42, z=3.14)

print("c was initialized with:", c.__init_args__, c.__init_kwargs__)
print("d was initialized with:", d.__init_args__, d.__init_kwargs__)
print("d2 was initialized with:", d2.__init_args__, d2.__init_kwargs__)
