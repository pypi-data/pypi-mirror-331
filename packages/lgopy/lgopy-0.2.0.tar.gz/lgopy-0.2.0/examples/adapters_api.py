from concurrent.futures import ThreadPoolExecutor

from lgopy.core import Block, apply_transform, LgoPipeline, BlockHub
import typing
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Animal:
    """
    A simple class representing an animal
    """
    def __init__(self, name):
        self.name = name

    def speak(self):
        """
        Make the animal speak
        :return:
        """
        print("Hello, I am {}".format(self.name))
        return self


    def eat(self, food):
        """
        Make the animal eat
        :param food:
        :return:
        """
        print("I am eating {}".format(food))
        return self

class Bird(Animal):
    def __init__(self, name):
        super().__init__(name)
        self.can_fly = True

    def fly(self):
        print("I am flying")
        return self

@BlockHub.register(
    name="MakeNoise",
    display_name="Make Noise",
    category="Animal",
    description="Make the animal speak"
)
class MakeNoise(Block):
    def __init__(self):
        super(MakeNoise, self).__init__()

    def setup(self, X: typing.Any):
        print("setting up the block")

    def call(self, animal: Animal):
        return animal.speak()

@BlockHub.register(
    name="FeedAnimal",
    display_name="Feed Animal",
    category="Animal",
    description="Feed the animal"
)
class FeedAnimal(Block):
    def __init__(self, food: str):
        super(FeedAnimal, self).__init__()
        self.food = food

    def setup(self, X: typing.Any):
        ...

    def call(self, animal: "Animal"):
        return animal.eat(self.food)


@apply_transform.register
def _(x: Animal, block: Block):
    print("running block on a Animal instance")
    return block.call(x)

@apply_transform.register
def _(x: Bird, block: Block):
    print("running block on a Bird instance")
    return block.call(x)


@apply_transform.register
def _( x: typing.List[Animal],block: Block):
    print(f"running block on a list of Animal instances for {block}")
    with ThreadPoolExecutor() as executor:
        return list(executor.map(block.call, x))

if __name__ == '__main__':
    # ds = [
    #     Animal("cow"),
    #     Animal("horse"),
    #     Animal("pig"),
    #     Bird("parrot")
    # ]
    pipeline = LgoPipeline.from_steps(
        MakeNoise(),
        FeedAnimal("hay")
    )

    print(pipeline.to_json())


    # pipeline.save("pipeline.json")
    # pipeline = LgoPipeline.from_json(pipeline.to_json())
    # ds = pipeline(ds)
    # print(FeedAnimal.to_pydantic_model().model_json_schema())
    # FeedAnimal.build()
    # FeedAnimal.serve(blocking=True)
    # FeedAnimal.publish(
    #     publisher="openai",
    #     authors=["openai", "langchain"],
    #     github="",
    #     version="0.0.1",
    #     dependencies=["openai"]
    # )
    #print(BlockHub.blocks_json())

