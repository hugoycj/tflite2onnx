import tflite
from onnx import helper

from .. import tensor
from ..common import logger
from .op import Operator


OpTypeMapping = {
        tflite.BuiltinOperator.ADD : 'Add',     # noqa: E203
}


class Binary(Operator):
    def __init__(self, model, graph, index):
        super().__init__(model, graph, index)
        logger.debug("Converting...")
        op = self.tflite
        opcode = model.OperatorCodes(op.OpcodeIndex()).BuiltinCode()
        assert(opcode in OpTypeMapping)
        self.type = OpTypeMapping[opcode]

        assert(op.InputsLength() == 2)
        assert(op.OutputsLength() == 1)

        for i in range(op.InputsLength()):
            ti = op.Inputs(i)
            to = tensor.convert(model, graph, ti)
            self.inputs.append(to)

        ti = op.Outputs(0)
        to = tensor.convert(model, graph, ti)
        self.outputs.append(to)

        inames = [t.name for t in self.inputs]
        onames = [t.name for t in self.outputs]
        logger.debug("Making ONNX...")
        self.onnx = helper.make_node(self.type, inames, onames)
