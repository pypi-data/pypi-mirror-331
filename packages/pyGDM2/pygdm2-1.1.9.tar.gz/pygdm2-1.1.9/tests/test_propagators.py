# encoding=utf-8
# %%
import unittest

import numpy as np

from pyGDM2.propagators.propagators import _G0_EE_asymptotic
from pyGDM2.propagators.propagators import Gs_EE_asymptotic
from pyGDM2.tools import generate_coord_map_XY, generate_coord_map_XZ


def convert_to_3x3(G_elements):
    xx, yy, zz, xy, xz, yx, yz, zx, zy = np.array(G_elements).T
    G_3x3 = np.moveaxis(np.array([[xx, xy, xz], [yx, yy, yz], [zx, zy, zz]]), -1, 0)
    return G_3x3


class TestAsymptoticSurface3D(unittest.TestCase):

    def setUp(self):

        self.wavelength = 515.0

        self.plotting = False

    def test_Gs(self):
        # test equivalence of farfield G_0 and G_s in absence of an interface
        eps1 = 1.0
        eps2 = 1.0
        
        r_probe_2d = generate_coord_map_XZ(
            -1000, 1000, 15, -1000, 1000, 15, Y0=1000
        
        ).astype(np.float32)
        r_source = np.array([0, 0, 100], dtype=np.float32)

        # evaluate G0 and Gs
        G0_2d = []
        Gs_2d = []
        for _r_p in r_probe_2d:
            G0_2d.append(_G0_EE_asymptotic(r_source, _r_p, self.wavelength, eps2))
            Gs_2d.append(
                Gs_EE_asymptotic(r_source, _r_p, self.wavelength, eps1, eps2)
            )

        # convert shape and test equivalence
        G0_map = convert_to_3x3(G0_2d)
        Gs_map = convert_to_3x3(Gs_2d)

        np.testing.assert_allclose(G0_map, Gs_map, rtol=1e-5, atol=1e-7)

        # optional plotting
        if self.plotting:
            import matplotlib.pyplot as plt
            from pyGDM2.visu import scalarfield

            def clean_subplot(im=None):
                if im is not None:
                    plt.colorbar(im)
                plt.xticks([])
                plt.yticks([])
                plt.xlabel("")
                plt.ylabel("")

            plt.figure(figsize=(20, 8))
            for m in range(3):
                for n in range(3):

                    plt.subplot(3, 6, 1 + 6 * m + 2 * n, title=f"G0{m}{n}")
                    im = scalarfield(
                        np.concatenate(
                            [r_probe_2d, G0_map[..., m, n][..., None]], axis=1
                        ),
                        show=False,
                    )
                    clean_subplot(im)

                    plt.subplot(3, 6, 1 + 6 * m + 2 * n + 1, title=f"Gs{m}{n}")
                    im = scalarfield(
                        np.concatenate(
                            [r_probe_2d, Gs_map[..., m, n][..., None]], axis=1
                        ),
                        show=False,
                    )
                    clean_subplot(im)

            plt.tight_layout()
            plt.show()


# %%
if __name__ == "__main__":
    print("testing Green's tensors...")
    np.set_printoptions(precision=7)
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
