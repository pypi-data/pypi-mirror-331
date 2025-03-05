import typing
from typing import Union, List

import numpy as np

from lgopy.core import Block, LgoPipeline, BlockHub


class Subtract(Block):
    def __init__(self, x: int = 1, y: int = 1):
        super().__init__()
        self.x = x
        self.y = y

    def setup(self, X: Union[np.ndarray, List[np.ndarray]]):
        """
        it setups the block
        """
        arr = np.array(X)

    def call(self, _) -> int:
        """
        it applies the transform to the input array
        :param x: input data
        :return:
        """
        return self.x - self.y

class Add(Block):
    def __init__(self, freq: typing.Annotated[float, "represent the frequency"] = 1):
        super().__init__()
        self.freq = freq

    def setup(self, X: typing.Any):
        """
        it setups the block
        """

    def call(self, x: np.ndarray) -> np.ndarray:
        """
        it applies the transform to the input array
        :param x: input data
        :return:
        """
        return x + 1

class Print(Block):
    def __init__(self):
        super().__init__()

    def call(self, x: typing.AnyStr) -> str:
        """
        it applies the transform to the input array
        :param x: input data
        :return:
        """
        return f"Hello {x}"

if __name__ == '__main__':
    for block in [Subtract, Add, Print]:
        print(block.to_pydantic_model().schema())

# legopy.init(
#     artifacts_path="file://artifacts", # where store file, images, etc. if any
#     metadata_path="metadata.db", # where to store metadata, such metrics, parameters, etc.
# )
#module = Subtract.build()

# block = Subtract()
# block.build()
# block.serve(blocking=True)

#
# Subtract().serve(blocking=True)
# Subtract(10, 2).serve(blocking=True)


# pipeline = LgoPipeline.from_steps(
#     Subtract(),
#     Add(),
#     Print(),
# )
# pipeline.serve(blocking=True)
#Subtract.publish()
#result = module().call("Hello World")
#Print().serve(blocking=True)
#Subtract(5, 2).serve(blocking=True)

