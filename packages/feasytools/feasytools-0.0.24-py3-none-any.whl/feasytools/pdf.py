from abc import abstractmethod
from enum import IntEnum
import random
from typing import Union
from xml.etree import ElementTree as ET


class PDModel(IntEnum):
    Uniform = 0
    Normal = 1
    Triangular = 2
    Exponential = 3
    LogNormal = 4
    Beta = 5
    Gamma = 6
    Weibull = 7
    LogLogistic = 8


class PDFunc:
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def sample(self) -> float:
        raise NotImplementedError()

    def __call__(self):
        return self.sample()

    def __repr__(self):
        s = []
        for k, v in self.__dict__.items():
            s.append(f"{k}={v}")
        return f"{self.__class__.__name__}({', '.join(s)})"


class PDUniform(PDFunc):
    def __init__(self, low: float = 0, high: float = 1):
        self.low = low
        self.high = high

    def sample(self):
        return random.uniform(self.low, self.high)


class PDNormal(PDFunc):
    def __init__(self, mean: float = 0, std: float = 1):
        self.mean = mean
        self.std = std

    def sample(self):
        return random.normalvariate(self.mean, self.std)


class PDTriangular(PDFunc):
    def __init__(self, low: float = 0, high: float = 1, mode: float = 0.5):
        self.low = low
        self.high = high
        self.mode = mode

    def sample(self):
        return random.triangular(self.low, self.high, self.mode)


class PDExponential(PDFunc):
    def __init__(self, lambd: float = 1):
        self.lambd = lambd

    def sample(self):
        return random.expovariate(self.lambd)


class PDLogNormal(PDFunc):
    def __init__(self, mean: float = 0, std: float = 1):
        self.mean = mean
        self.std = std

    def sample(self):
        return random.lognormvariate(self.mean, self.std)


class PDBeta(PDFunc):
    def __init__(self, alpha: float = 1, beta: float = 1):
        self.alpha = alpha
        self.beta = beta

    def sample(self):
        return random.betavariate(self.alpha, self.beta)


class PDGamma(PDFunc):
    def __init__(self, alpha: float = 1, beta: float = 1):
        self.alpha = alpha
        self.beta = beta

    def sample(self):
        return random.gammavariate(self.alpha, self.beta)


class PDWeibull(PDFunc):
    def __init__(self, alpha: float = 1, beta: float = 1):
        self.alpha = alpha
        self.beta = beta

    def sample(self):
        return random.weibullvariate(self.alpha, self.beta)


class PDLogLogistic(PDFunc):
    def __init__(self, mean: float = 0, std: float = 1):
        self.mean = mean
        self.std = std

    def sample(self):
        return random.lognormvariate(self.mean, self.std)


class PDDiscrete(PDFunc):
    def __init__(self, values: list[float], weights: list[float]):
        self.values = values
        self.weights = weights

    def sample(self):
        return random.choices(self.values, self.weights)[0]

    @staticmethod
    def fromXMLNode(node: ET.Element):
        values = []
        weights = []
        for n in node:
            assert (
                n.tag == "item"
            ), f"Tags' name must be lower case 'item', not '{n.tag}'."
            values.append(float(n.get("value")))
            weights.append(float(n.get("weight")))
        return PDDiscrete(values, weights)


def GetPDFuncFromXMLNode(node: ET.Element):
    model = node.get("model")
    if model == "Discrete":
        return PDDiscrete.fromXMLNode(node)
    args = []
    if model == "Normal":
        args.append(float(node.get("mean")))
        args.append(float(node.get("std")))
    elif model == "Uniform":
        args.append(float(node.get("low")))
        args.append(float(node.get("high")))
    elif model == "Triangular":
        args.append(float(node.get("low")))
        args.append(float(node.get("high")))
        args.append(float(node.get("mode")))
    elif model == "Exponential":
        args.append(float(node.get("lambda")))
    elif model == "LogNormal":
        args.append(float(node.get("std")))
        args.append(float(node.get("mean")))
    elif model == "Beta":
        args.append(float(node.get("alpha")))
        args.append(float(node.get("beta")))
    elif model == "Gamma":
        args.append(float(node.get("alpha")))
        args.append(float(node.get("beta")))
    elif model == "Weibull":
        args.append(float(node.get("alpha")))
        args.append(float(node.get("beta")))
    elif model == "LogLogistic":
        args.append(float(node.get("mean")))
        args.append(float(node.get("std")))
    else:
        raise ValueError(f"Unknown probability distribution model {model}")
    return CreatePDFunc(model, *args)


def CreatePDFunc(model: Union[str, PDModel], *args, **kwargs):
    if model == PDModel.Uniform or model == "Uniform":
        return PDUniform(*args, **kwargs)
    elif model == PDModel.Normal or model == "Normal":
        return PDNormal(*args, **kwargs)
    elif model == PDModel.Triangular or model == "Triangular":
        return PDTriangular(*args, **kwargs)
    elif model == PDModel.Exponential or model == "Exponential":
        return PDExponential(*args, **kwargs)
    elif model == PDModel.LogNormal or model == "LogNormal":
        return PDLogNormal(*args, **kwargs)
    elif model == PDModel.Beta or model == "Beta":
        return PDBeta(*args, **kwargs)
    elif model == PDModel.Gamma or model == "Gamma":
        return PDGamma(*args, **kwargs)
    elif model == PDModel.Weibull or model == "Weibull":
        return PDWeibull(*args, **kwargs)
    elif model == PDModel.LogLogistic or model == "LogLogistic":
        return PDLogLogistic(*args, **kwargs)
    elif model == "Discrete":
        return PDDiscrete(*args, **kwargs)
    else:
        raise ValueError(f"Unknown probability distribution model {model}")
