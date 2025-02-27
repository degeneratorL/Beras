import numpy as np

from typing import Literal
from beras.core import Diffable, Variable, Tensor

DENSE_INITIALIZERS = Literal["zero", "normal", "xavier", "kaiming", "xavier uniform", "kaiming uniform"]

class Dense(Diffable):

    def __init__(self, input_size, output_size, initializer: DENSE_INITIALIZERS = "normal"):
        self.w, self.b = self._initialize_weight(initializer, input_size, output_size)

    @property
    def weights(self) -> list[Tensor]:
        return self.w, self.b

    def forward(self, x: Tensor) -> Tensor:
        """
        Forward pass for a dense layer! Refer to lecture slides for how this is computed.
        """
        if x.ndim == 1:
            x = x[None, :]
        return x @ self.w + self.b  # (batch_size, output_size)NotImplementedError

    def get_input_gradients(self) -> list[Tensor]:
        return [self.w] 
        # For a dense layer f(x)=x@w + b, partial f wrt x = w  (shape: (input_size, output_size)) NotImplementedError

    def get_weight_gradients(self) -> list[Tensor]:
        x = self.inputs[0]
        out_dim = self.w.shape[1]

        if x.ndim == 1:
            # x.shape = (n,)
            n = x.shape[0]
            w_grad = np.zeros((n, out_dim), dtype=x.dtype)
            for j in range(out_dim):
                w_grad[:, j] = x
            
            b_grad = np.ones((out_dim,), dtype=x.dtype)

            return [w_grad, b_grad]

        else:
            # x.shape = (batch_size, n)
            batch_size, n = x.shape

            w_grad = np.zeros((batch_size, n, out_dim), dtype=x.dtype)
            for i in range(batch_size):
                for j in range(out_dim):
                    w_grad[i, :, j] = x[i]
            
            b_grad = np.ones((out_dim, ), dtype=x.dtype)

            return [w_grad, b_grad]

    @staticmethod
    def _initialize_weight(initializer, input_size, output_size) -> tuple[Variable, Variable]:
        """
        Initializes the values of the weights and biases. The bias weights should always start at zero.
        However, the weights should follow the given distribution defined by the initializer parameter
        (zero, normal, xavier, or kaiming). You can do this with an if statement
        cycling through each option!

        Details on each weight initialization option:
            - Zero: Weights and biases contain only 0's. Generally a bad idea since the gradient update
            will be the same for each weight so all weights will have the same values.
            - Normal: Weights are initialized according to a normal distribution.
            - Xavier: Goal is to initialize the weights so that the variance of the activations are the
            same across every layer. This helps to prevent exploding or vanishing gradients. Typically
            works better for layers with tanh or sigmoid activation.
            - Kaiming: Similar purpose as Xavier initialization. Typically works better for layers
            with ReLU activation.
        """

        initializer = initializer.lower()
        if initializer == "zero":
            w = np.zeros((input_size, output_size), dtype=np.float32)
            b = np.zeros((output_size,), dtype=np.float32)

        elif initializer == "normal":
            w = np.random.normal(loc=0.0, scale=1.0, size=(input_size, output_size)).astype(np.float32)
            b = np.zeros((output_size,), dtype=np.float32)

        elif initializer == "xavier":
            # Glorot normal => stddev = sqrt(2/(fan_in + fan_out))
            std = np.sqrt(2.0 / (input_size + output_size))
            w = np.random.normal(loc=0.0, scale=std, size=(input_size, output_size)).astype(np.float32)
            b = np.zeros((output_size,), dtype=np.float32)

        elif initializer == "kaiming":
            # He normal => stddev = sqrt(2/fan_in)
            std = np.sqrt(2.0 / input_size)
            w = np.random.normal(loc=0.0, scale=std, size=(input_size, output_size)).astype(np.float32)
            b = np.zeros((output_size,), dtype=np.float32)

        elif initializer == "xavier uniform":
            limit = np.sqrt(6.0 / (input_size + output_size))
            w = np.random.uniform(-limit, limit, (input_size, output_size)).astype(np.float32)
            b = np.zeros((output_size,), dtype=np.float32)

        elif initializer == "kaiming uniform":
            limit = np.sqrt(6.0 / input_size)
            w = np.random.uniform(-limit, limit, (input_size, output_size)).astype(np.float32)
            b = np.zeros((output_size,), dtype=np.float32)

        else:
            raise ValueError(f"Unknown dense weight initialization strategy '{initializer}' requested")

        return Variable(w), Variable(b)
