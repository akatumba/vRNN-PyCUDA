import unittest
import numpy as np
from src.model.Cell import Cell
from src.model.LSTM import RNN
from src.model.lstm_layer import *

import pycuda.gpuarray
from pycuda.tools import mark_cuda_test

class RNNTestCase(unittest.TestCase):

    """def test_init(self):
        rnn = RNN(10, [1, 3, 5])
        answer = "5 layers: \n"
        answer += "  Input layer of size 10 to 10\n"
        answer += "  Hidden layer of size 10 to 1\n"
        answer += "  Hidden layer of size 1 to 3\n"
        answer += "  Hidden layer of size 3 to 5\n"
        answer += "  Output layer of size 5 to 10\n"

        self.assertEqual(rnn.__repr__(), answer)
    """


class LstmLayerTestCase(unittest.TestCase):

    @mark_cuda_test
    def test_forward_prop(self):
        np.random.seed(1)
        x = np.random.randn(3, 10, 7)
        a0 = np.random.randn(5, 10)
        Wf = np.random.randn(5, 5 + 3)
        bf = np.random.randn(5, 1)
        Wi = np.random.randn(5, 5 + 3)
        bi = np.random.randn(5, 1)
        Wo = np.random.randn(5, 5 + 3)
        bo = np.random.randn(5, 1)
        Wc = np.random.randn(5, 5 + 3)
        bc = np.random.randn(5, 1)
        Wy = np.random.randn(2, 5)
        by = np.random.randn(2, 1)

        parameters = {"Wf": Wf, "Wi": Wi, "Wo": Wo, "Wc": Wc, "Wy": Wy, "bf": bf, "bi": bi, "bo": bo, "bc": bc,
                      "by": by}

        Wf_gpu = pycuda.gpuarray.to_gpu(Wf)
        Wi_gpu = pycuda.gpuarray.to_gpu(Wi)
        Wo_gpu = pycuda.gpuarray.to_gpu(Wo)
        Wc_gpu = pycuda.gpuarray.to_gpu(Wc)
        Wy_gpu = pycuda.gpuarray.to_gpu(Wy)
        bf_gpu = pycuda.gpuarray.to_gpu(bf)
        bi_gpu = pycuda.gpuarray.to_gpu(bi)
        bo_gpu = pycuda.gpuarray.to_gpu(bo)
        bc_gpu = pycuda.gpuarray.to_gpu(bc)
        by_gpu = pycuda.gpuarray.to_gpu(by)

        parameters_gpu = {"Wf": Wf_gpu, "Wi": Wi_gpu, "Wo": Wo_gpu, "Wc": Wc_gpu, "Wy": Wy_gpu, "bf": bf_gpu, "bi": bi_gpu, "bo": bo_gpu, "bc": bc_gpu,
                      "by": by_gpu}

        a, y, c, caches = lstm_forward(x, a0, parameters, False)

        a, y, c, caches = lstm_forward(x, a0, parameters_gpu, True)


class CellTestCase(unittest.TestCase):

    """def test_forward_prop(self):
        cell = Cell(4, 4)
        x_t = np.array([[0], [0], [0], [1]])
        y_t = [[1], [1], [1], [1]]

        self.assertListEqual(cell.forward_prop(x_t).tolist(), y_t)
    """

    @mark_cuda_test
    def test_forward_prop_gpu(self):
        vocab = 10
        batches = 2
        cell = Cell(vocab, batches, (0,0))
        gpu_cell = Cell(vocab, batches, (0,0))
        gpu_cell.cell_to_gpu()
        x_t = np.zeros((vocab, batches))
        h_prev = np.zeros((vocab, batches))
        c_prev = np.zeros((vocab, batches))
        x_t[5][0] = 1
        x_t[7][1] = 1
        x_t_gpu = pycuda.gpuarray.to_gpu(x_t)
        h_prev_gpu = pycuda.gpuarray.to_gpu(h_prev)
        c_prev_gpu = pycuda.gpuarray.to_gpu(c_prev)

        h, c = cell.forward_prop(c_prev, h_prev, x_t)
        print("CPU done")
        h_gpu, c_gpu = gpu_cell.forward_prop_gpu(c_prev_gpu, h_prev_gpu, x_t_gpu)
        gpu_cell.cell_from_gpu()
        print("GPU Done")

        h_gpu_mem = h_gpu.get()

        for j in range(batches):
            for i in range(vocab):
                self.assertLessEqual(abs(h[i][j] - h_gpu_mem[i][j]), 0.25)