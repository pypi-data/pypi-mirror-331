from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator
from sklearn.base import TransformerMixin
import typing
from multimethod import multimethod
from sklearn.exceptions import NotFittedError
from pydantic import BaseModel
from sklearn.utils.validation import check_is_fitted
from .block_mixin import BlockMixin
import logging

logger = logging.getLogger(__name__)


class RequestData(BaseModel):
    data: typing.Any | None = None
    args: dict | None = None

def is_step_fitted(block):
    """
    Check if a step is fitted
    :param step:
    :return:
    """
    try:
        check_is_fitted(block)
    except NotFittedError:
        return False
    return True

@multimethod
def apply_transform(x: typing.Any,  block: Block = None):
    """
    it applies the transform to the input array
    :param block: block
    :param x: input data
    :param y: target data (optional)
    :return:
    """
    return block.call(x)


@apply_transform.register(np.ndarray)
def _(x: np.ndarray, block: Block = None):
    """
    it applies the transform to the input array
    :param block: block
    :param x: input data
    :param y: target data (optional)
    :return:
    """
    return block.call(x)


@apply_transform.register(list)
def _(x: list, block: Block = None):
    """
    it applies the transform to the input array
    :param block: block
    :param x: input data
    :param y: target data (optional)
    :return:
    """
    return [block.call(xi) for xi in x]

class Block(BaseEstimator, TransformerMixin, BlockMixin):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = {}


    def fit(self, X: typing.Any, y: typing.Any=None, **fit_params) -> typing.Any:
        """
        it applies the transform to the input data
        :param X:
        :param y:
        :param fit_params:
        :return:
        """
        # setup the block when fitting
        self.setup(X)
        return self

    def transform(self, x: typing.Any, y=None):
        """
        it applies the transform to the input data
        :param x:
        :param X:
        :return:
        """
        return apply_transform(x, self)

    def serve(self, *args, **kwargs):
        """
        it serves the block

        """
        from fastapi import FastAPI
        from fastapi.responses import  JSONResponse
        from ray import serve


        app = FastAPI()
        block = self
        block_name = block.__class__.__name__.lower()

        @serve.deployment
        @serve.ingress(app)
        class BlockDeployment:
            """
            Block deployment class
            """
            @app.get("/health")
            def root(self):
                """
                health check
                :return:
                """
                return f"Block {block_name} is up and running"

            @app.post("/")
            def call(self, request_data : RequestData):
                """
                it calls the block
                :param request_data:
                :return:
                """
                if request_data.args:
                    arguments = request_data.args
                    for key, value in arguments.items():
                        setattr(block, key, value)
                result = block(request_data.data)
                return JSONResponse(content={"output": result})

        deployment = BlockDeployment.bind()
        serve.run(deployment, route_prefix=f"/{block_name}", *args, **kwargs)


    def setup(self, X: typing.Any):
        """
        it setups the block
        """

    def call(self, x: typing.Any) -> typing.Any:
        """
        it applies the transform to the input array
        :param x: input data
        :return:
        """
        raise NotImplementedError()

    # single array transformation
    def __call__(self, x: typing.Any):
        """
        it applies the transform to the input array
        :param x: input data
        :return:
        """
        return self.transform(x)
