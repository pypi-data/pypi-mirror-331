'''
Code taken from Pytorch, modified to be meta Linear module.
'''

import math

import torch
import torch.nn as nn
# from torch.nn import functional as F, init
from torch.nn.parameter import Parameter


__all__ = [
    'Linear'
]


class Linear(nn.Module):
    r"""Meta linear module.
    Uses tntorch library to compress the high dimensional meta weights.

    Args:
        in_features: size of each input sample
        out_features: size of each output sample
        bias: If set to ``False``, the layer will not learn an additive bias.
            Default: ``True``
        order: The order of meta. Default: 1.
        depth: number of iterations that input will go through this module.
        compression: compression algorithm used on high dimensional meta weights.
            Default: ``TT`` (Tensor Train)
        rank: Low rank of the compression. Must not be absent if compression is not None.
            E.g. for a 3D meta weight of shape (a, b, c). A rank=(1,3,4,1) will decompose the meta weigt into 3 tensors of shape (1,a,3), (3,b,4), and (4,c,1).

    Shape:
        - Input: :math:`(*, H_{in})` where :math:`*` means any number of
          dimensions including none and :math:`H_{in} = \text{in\_features}`.
        - Output: :math:`(*, H_{out})` where all but the last dimension
          are the same shape as the input and :math:`H_{out} = \text{out\_features}`.

    Attributes:
        weight: the learnable weights of the module of shape
            :math:`(\text{out\_features}, \text{in\_features})`. The values are
            initialized from :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})`, where
            :math:`k = \frac{1}{\text{in\_features}}`
        bias:   the learnable bias of the module of shape :math:`(\text{out\_features})`.
                If :attr:`bias` is ``True``, the values are initialized from
                :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
                :math:`k = \frac{1}{\text{in\_features}}`
        order: The order of meta. Default: 1.
        depth: number of iterations that input will go through this module.
        compression: compression algorithm used on high dimensional meta weights.
        rank: Low rank of the compression.

    Examples::

        >>> m = Linear(20, 30)
        >>> input = torch.randn(128, 20)
        >>> output = m(input)
        >>> print(output.size())
        torch.Size([128, 30])
    """

    __constants__ = ["in_features", "out_features"]
    in_features: int
    out_features: int
    weight: torch.Tensor

    def __init__(
        self,
        in_features: int,
        out_features: int,
        bias: bool = True,
        order: int = 1,
        depth: int = 1,
        compression: str | None = 'TT',
        rank: int | list[int] | None = None,
        device=None,
        dtype=None,
    ) -> None:
        if depth > 1:
            assert in_features == out_features

        factory_kwargs = {"device": device, "dtype": dtype}
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.order = order
        self.depth = depth
        self.compression = compression

        weight_shape = (in_features,) * order + (in_features, out_features)
        if compression is None:
            self.weight = Parameter(torch.rand(weight_shape, **factory_kwargs))
        elif compression == 'TT':
            assert rank is not None
            if isinstance(rank, int):
                rank = [1] + [rank] * (order + 1) + [1]
            assert rank[0] == rank[-1] == 1
            assert len(rank) == order + 3
            self.cores = nn.ParameterList(
                [nn.Parameter(torch.rand((r1, d, r2), **factory_kwargs)) for r1, d, r2 in zip(rank[:-1], weight_shape, rank[1:])]
            )
        else:
            raise NotImplementedError
        if bias:
            self.bias = Parameter(torch.zeros(out_features, **factory_kwargs))
        else:
            self.register_parameter("bias", None)


    def forward(self, x: torch.Tensor) -> torch.Tensor:
        sqrt_d = math.sqrt(x.shape[-1])

        if self.compression is None:
            for i in range(self.depth):
                # first perform meta forward
                w = torch.einsum('ijk,k...->ij...', x, self.weight)
                for j in range(self.order):
                    w = torch.einsum('ijk,ijk...->ij...', x, w) / sqrt_d
                x = w
        elif self.compression == 'TT':
            for i in range(self.depth):
                w = self.cores[0].unsqueeze(0)
                for c in self.cores[1:]:
                    w = torch.einsum('bnd,bndR->bnR', x, w)
                    w = torch.einsum('bnr,rdR->bndR', w, c)
                x = w.squeeze(-1)
        if self.bias is not None:
            x += self.bias
        return x

    def extra_repr(self) -> str:
        return f"in_features={self.in_features}, out_features={self.out_features}, bias={self.bias is not None}, order={self.order}, iters={self.depth}"
